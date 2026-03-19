import json
import os
from datetime import datetime
from uuid import uuid4

SCHEDULE_FILE = "scheduler/schedules.json"
os.makedirs("scheduler", exist_ok=True)

def load_jobs():
    if not os.path.exists(SCHEDULE_FILE):
        return []
    with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
        jobs = json.load(f)

    # 🔒 Backward compatibility for old jobs
    for j in jobs:
        j.setdefault("id", str(uuid4()))
        j.setdefault("status", "pending")
        j.setdefault("attempts", 0)
        j.setdefault("last_error", None)

    return jobs

def save_jobs(jobs):
    with open(SCHEDULE_FILE, "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=2)

def add_job(job_dict):
    jobs = load_jobs()

    job = {
        "id": job_dict.get("id", str(uuid4())),
        "video_path": job_dict["video_path"],
        "account": job_dict["account"],
        "privacy": job_dict["privacy"],
        "scheduled_at": job_dict["scheduled_at"],
        "status": "pending",
        "attempts": 0,
        "last_error": None
    }

    jobs.append(job)
    save_jobs(jobs)
    return job

def update_job(job_id, **updates):
    jobs = load_jobs()
    for j in jobs:
        if j["id"] == job_id:
            j.update(updates)
            break
    save_jobs(jobs)

def remove_job(job_id):
    jobs = load_jobs()
    jobs = [j for j in jobs if j["id"] != job_id]
    save_jobs(jobs)
