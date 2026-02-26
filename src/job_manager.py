import uuid
from src.animator import run_animation_pipeline  # adjust if needed


jobs = {}


def create_job(prompt: str):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "prompt": prompt,
        "status": "queued",
        "result": None,
        "error": None
    }
    return job_id


def update_job(job_id: str, status: str, result=None, error=None):
    if job_id in jobs:
        jobs[job_id]["status"] = status
        jobs[job_id]["result"] = result
        jobs[job_id]["error"] = error


def get_job(job_id: str):
    return jobs.get(job_id)


def execute_job(prompt: str, job_id: str):
    try:
        update_job(job_id, "processing")

        video_path = run_animation_pipeline(prompt)

        update_job(job_id, "completed", result=video_path)

    except Exception as e:
        update_job(job_id, "failed", error=str(e))