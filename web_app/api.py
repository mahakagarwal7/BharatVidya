# web_app/api.py
"""
FastAPI backend for Educational Video Generator.

Endpoints:
  POST /api/generate     - Start video generation job
  GET  /api/status/{id}  - Check job status
  GET  /api/videos       - List completed videos
  GET  /api/video/{id}   - Get specific video info
  GET  /api/health       - Health check
"""

import os
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Optional

from .models import (
    GenerateRequest, JobResponse, JobStatusResponse,
    VideoInfo, VideoListResponse, HealthResponse, JobStatus
)
from .jobs import job_manager, JobStatus as JStatus
from .video_service import generate_video_with_progress


# Create FastAPI app
app = FastAPI(
    title="Educational Video Generator API",
    description="Generate educational explainer videos using AI",
    version="1.0.0"
)

# CORS configuration - reads from CORS_ORIGINS env var for production
default_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

# Add production origins from environment variable
cors_origins_env = os.getenv("CORS_ORIGINS", "")
if cors_origins_env:
    production_origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()]
    default_origins.extend(production_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=default_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static video files
OUTPUTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs")
os.makedirs(OUTPUTS_DIR, exist_ok=True)

# Mount outputs directory for video serving
app.mount("/videos", StaticFiles(directory=OUTPUTS_DIR), name="videos")


# ============================================
# API Endpoints
# ============================================

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Check API health and Ollama availability"""
    ollama_ok = False
    try:
        import requests
        resp = requests.get("http://localhost:11434/api/tags", timeout=2)
        ollama_ok = resp.status_code == 200
    except:
        pass
    
    return HealthResponse(
        status="healthy",
        ollama_available=ollama_ok,
        version="1.0.0"
    )


@app.post("/api/generate", response_model=JobResponse)
async def generate_video(request: GenerateRequest):
    """
    Start a video generation job.
    
    Returns immediately with job_id. Poll /api/status/{job_id} for progress.
    """
    # Create job
    job = job_manager.create_job(
        concept=request.concept,
        language=request.language,
        enable_animations=request.enable_animations
    )
    
    # Start background processing
    job_manager.run_job(job.job_id, generate_video_with_progress)
    
    return JobResponse(
        job_id=job.job_id,
        status=JobStatus.QUEUED,
        message=f"Video generation started for: {request.concept}"
    )


@app.get("/api/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """Get the status of a video generation job"""
    job = job_manager.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Build video URL - prefer S3 URL if available, fall back to local
    video_url = None
    if job.video_url:
        # S3/CloudFront URL
        video_url = job.video_url
    elif job.video_path and os.path.exists(job.video_path):
        # Local fallback
        filename = os.path.basename(job.video_path)
        video_url = f"/videos/{filename}"
    
    return JobStatusResponse(
        job_id=job.job_id,
        status=JobStatus(job.status.value),
        step=job.step,
        progress=job.progress,
        video_url=video_url,
        plan=job.plan,
        error=job.error,
        created_at=job.created_at,
        completed_at=job.completed_at
    )


@app.get("/api/videos", response_model=VideoListResponse)
async def list_videos():
    """List all completed videos"""
    completed_jobs = job_manager.get_all_completed()
    
    videos = []
    for job in completed_jobs:
        if job.video_path and os.path.exists(job.video_path):
            filename = os.path.basename(job.video_path)
            title = job.plan.get("title", job.concept) if job.plan else job.concept
            
            videos.append(VideoInfo(
                job_id=job.job_id,
                title=title,
                concept=job.concept,
                video_url=f"/videos/{filename}",
                language=job.language,
                created_at=job.created_at,
                duration=None  # Could extract from video metadata
            ))
    
    return VideoListResponse(
        videos=videos,
        total=len(videos)
    )


@app.get("/api/video/{job_id}")
async def get_video_info(job_id: str):
    """Get info about a specific video"""
    job = job_manager.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != JStatus.COMPLETE:
        raise HTTPException(status_code=400, detail=f"Video not ready. Status: {job.status}")
    
    if not job.video_path or not os.path.exists(job.video_path):
        raise HTTPException(status_code=404, detail="Video file not found")
    
    filename = os.path.basename(job.video_path)
    title = job.plan.get("title", job.concept) if job.plan else job.concept
    
    return VideoInfo(
        job_id=job.job_id,
        title=title,
        concept=job.concept,
        video_url=f"/videos/{filename}",
        language=job.language,
        created_at=job.created_at
    )


@app.get("/api/topics")
async def get_supported_topics():
    """Get list of topics with specialized animations"""
    # These are the topics with custom animations
    animated_topics = [
        "bubble_sort", "binary_search", "quadratic", 
        "sine_wave", "projectile_motion", "pendulum",
        "linear_equation", "heat", "geometry", "chemistry", "wave", "statistics",
        "coordinate_geometry", "circuit", "optics", "force",
        "organic_chemistry", "organic_reaction", 
        "physical_chemistry", "inorganic_chemistry",
        "magnetic_field", "electromagnetic", "gravity"
    ]
    
    return {
        "animated_topics": animated_topics,
        "supported_languages": [
            {"code": "en", "name": "English"},
            {"code": "hi", "name": "Hindi"},
            {"code": "pa", "name": "Punjabi"},
            {"code": "te", "name": "Telugu"},
            {"code": "ta", "name": "Tamil"},
            {"code": "bn", "name": "Bengali"},
            {"code": "gu", "name": "Gujarati"},
            {"code": "mr", "name": "Marathi"},
            {"code": "kn", "name": "Kannada"},
            {"code": "ml", "name": "Malayalam"},
            {"code": "es", "name": "Spanish"},
            {"code": "fr", "name": "French"},
            {"code": "de", "name": "German"},
            {"code": "zh", "name": "Chinese"},
            {"code": "ja", "name": "Japanese"},
            {"code": "ko", "name": "Korean"},
        ]
    }


# ============================================
# Development server
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
