# web_app/models.py
"""Pydantic models for API requests/responses"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETE = "complete"
    FAILED = "failed"


class GenerateRequest(BaseModel):
    """Request to generate an educational video"""
    concept: str = Field(..., min_length=3, max_length=500, description="Topic/concept to explain")
    language: str = Field(default="en", description="Language code (en, hi, es, fr, etc.)")
    enable_animations: bool = Field(default=True, description="Include topic-based animations")


class JobResponse(BaseModel):
    """Response when a job is created"""
    job_id: str
    status: JobStatus
    message: str


class JobStatusResponse(BaseModel):
    """Response for job status check"""
    job_id: str
    status: JobStatus
    step: Optional[str] = None
    progress: Optional[int] = None  # 0-100
    video_url: Optional[str] = None
    plan: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None


class VideoInfo(BaseModel):
    """Info about a generated video"""
    job_id: str
    title: str
    concept: str
    video_url: str
    language: str
    created_at: str
    duration: Optional[float] = None


class VideoListResponse(BaseModel):
    """List of generated videos"""
    videos: List[VideoInfo]
    total: int


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    ollama_available: bool
    version: str
