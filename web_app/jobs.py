# web_app/jobs.py
"""Background job management for video generation"""

import threading
import uuid
import time
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import traceback


class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class Job:
    """Represents a video generation job"""
    job_id: str
    concept: str
    language: str
    enable_animations: bool
    status: JobStatus = JobStatus.QUEUED
    step: str = "Queued"
    progress: int = 0
    video_path: Optional[str] = None
    video_url: Optional[str] = None
    plan: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    completed_at: Optional[str] = None


class JobManager:
    """
    Simple in-memory job manager with threading.
    For production, replace with Celery + Redis.
    """
    
    def __init__(self):
        self.jobs: Dict[str, Job] = {}
        self._lock = threading.Lock()
    
    def create_job(self, concept: str, language: str, enable_animations: bool) -> Job:
        """Create a new job and return it"""
        job_id = str(uuid.uuid4())[:8]
        job = Job(
            job_id=job_id,
            concept=concept,
            language=language,
            enable_animations=enable_animations
        )
        with self._lock:
            self.jobs[job_id] = job
        return job
    
    def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID"""
        return self.jobs.get(job_id)
    
    def update_job(self, job_id: str, **kwargs):
        """Update job fields"""
        with self._lock:
            if job_id in self.jobs:
                job = self.jobs[job_id]
                for key, value in kwargs.items():
                    if hasattr(job, key):
                        setattr(job, key, value)
    
    def get_all_completed(self) -> list:
        """Get all completed jobs"""
        return [
            job for job in self.jobs.values() 
            if job.status == JobStatus.COMPLETE
        ]
    
    def run_job(self, job_id: str, generate_func):
        """
        Run the video generation in a background thread.
        
        Args:
            job_id: The job ID to process
            generate_func: Function that takes (concept, language, enable_animations)
                          and returns (video_path, plan)
        """
        thread = threading.Thread(
            target=self._execute_job,
            args=(job_id, generate_func),
            daemon=True
        )
        thread.start()
    
    def _execute_job(self, job_id: str, generate_func):
        """Execute job in background thread"""
        job = self.get_job(job_id)
        if not job:
            return
        
        try:
            self.update_job(
                job_id,
                status=JobStatus.PROCESSING,
                step="Starting video generation...",
                progress=5
            )
            
            
            video_path, plan = generate_func(
                job.concept,
                job.language,
                job.enable_animations,
                progress_callback=lambda step, pct: self.update_job(
                    job_id, step=step, progress=pct
                )
            )
            
            if video_path:
                
                video_url = None
                try:
                    from .s3_service import s3_service
                    if s3_service.enabled:
                        self.update_job(job_id, step="Uploading to cloud...", progress=95)
                        video_url = s3_service.upload_video(video_path, job_id)
                except Exception as e:
                    print(f"⚠️ S3 upload skipped: {e}")
                
                self.update_job(
                    job_id,
                    status=JobStatus.COMPLETE,
                    step="Complete",
                    progress=100,
                    video_path=video_path,
                    video_url=video_url,  
                    plan=plan,
                    completed_at=datetime.utcnow().isoformat()
                )
            else:
                self.update_job(
                    job_id,
                    status=JobStatus.FAILED,
                    step="Failed",
                    error="Video generation returned no output",
                    completed_at=datetime.utcnow().isoformat()
                )
                
        except Exception as e:
            self.update_job(
                job_id,
                status=JobStatus.FAILED,
                step="Failed",
                error=str(e),
                completed_at=datetime.utcnow().isoformat()
            )
            traceback.print_exc()



job_manager = JobManager()
