import time
from datetime import datetime
from scheduler.scheduler_store import load_jobs, update_job
from scheduler.scheduler_runner import run_job

CHECK_INTERVAL = 30  # seconds

def start_scheduler(logger=print):
    logger("🕒 Scheduler engine started")

    while True:
        try:
            jobs = load_jobs()
            now = datetime.now()

            # 👉 sirf pending jobs uthao
            pending_jobs = [
                j for j in jobs
                if j["status"] == "pending"
                and datetime.fromisoformat(j["scheduled_at"]) <= now
            ]

            # sort by scheduled time (oldest first)
            pending_jobs.sort(
                key=lambda j: datetime.fromisoformat(j["scheduled_at"])
            )

            for job in pending_jobs:
                job_id = job["id"]

                logger(f"⏰ Scheduled upload started: {job['video_path']}")

                # ---- mark running ----
                update_job(job_id, status="running")

                try:
                    run_job(job, logger=logger)

                    # ---- success ----
                    update_job(job_id, status="done")
                    logger("✅ Job completed")

                except Exception as e:
                    # ---- failed ----
                    update_job(
                        job_id,
                        status="failed",
                        attempts=job.get("attempts", 0) + 1,
                        last_error=str(e)
                    )
                    logger(f"❌ Job failed: {e}")

                # ⚠️ IMPORTANT: ek job ke baad pause
                break

        except Exception as e:
            logger(f"🔥 Scheduler internal error: {e}")

        time.sleep(CHECK_INTERVAL)
