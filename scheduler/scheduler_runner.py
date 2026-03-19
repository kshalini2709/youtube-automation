from youtube_uploader import upload_video
from upload_registry import is_uploaded
from scheduler.scheduler_store import load_jobs, update_job


def run_job(job, logger=print):
    """
    job = {
        id,
        video_path,
        account,
        privacy
    }
    """

    channel_id = job["account"]["channel_id"]

    if is_uploaded(job["video_path"], channel_id):
        logger(f"⏭️ Scheduler skipped duplicate upload: {job['video_path']}")
        update_job(job["id"], status="done")
        return

    logger(f"⏰ Scheduled upload started: {job['video_path']}")

    try:
        upload_video(
            video_path=job["video_path"],
            account=job["account"],
            privacy=job["privacy"],
            logger=logger
        )
        update_job(job["id"], status="done")
        logger("✅ Scheduled upload finished")

    except Exception as e:
        update_job(
            job["id"],
            status="failed",
            attempts=job.get("attempts", 0) + 1,
            last_error=str(e)
        )
        logger(f"❌ Scheduled upload failed: {e}")
