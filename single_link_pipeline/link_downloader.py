import os
import subprocess
import re
import time

BASE_DIR = "single_link_pipeline"

DOWNLOAD_DIR = os.path.join(BASE_DIR, "download")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def _clean_filename(name: str) -> str:
    name = re.sub(r"[^\w\s-]", "", name)
    name = re.sub(r"\s+", "_", name)
    name = name.strip("_")

    # Windows reserved names safety
    if name.upper() in {"CON", "PRN", "AUX", "NUL"}:
        name = f"video_{int(time.time())}"

    return name[:120]


def download_single_video(url: str, logger=print) -> str | None:
    """
    Downloads ONE YouTube video safely.
    Output always goes into:
    single_link_pipeline/download/

    Returns:
        final video path (str) OR None on failure
    """

    logger("⬇ Starting single-link download...")

    ts = int(time.time())

    output_template = os.path.join(
        DOWNLOAD_DIR,
        f"%(title)s_{ts}.%(ext)s"
    )

    cmd = [
        "yt-dlp",
        "-f", "bv*[ext=mp4]+ba[ext=m4a]/mp4",
        "--merge-output-format", "mp4",
        "--no-playlist",
        "-o", output_template,
        url
    ]

    try:
        subprocess.run(cmd, check=True)
    except Exception as e:
        logger(f"❌ Download failed: {e}")
        return None

    # Find the exact downloaded file
    candidates = [
        f for f in os.listdir(DOWNLOAD_DIR)
        if f.endswith(".mp4") and str(ts) in f
    ]

    if not candidates:
        logger("❌ Download finished but video file not found")
        return None

    raw_path = os.path.join(DOWNLOAD_DIR, candidates[0])

    base, ext = os.path.splitext(os.path.basename(raw_path))
    safe_name = _clean_filename(base) + ext
    final_path = os.path.join(DOWNLOAD_DIR, safe_name)

    if raw_path != final_path and not os.path.exists(final_path):
        os.rename(raw_path, final_path)

    logger(f"✅ Downloaded successfully: {final_path}")
    return final_path
