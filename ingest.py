import os
import subprocess
import json

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def ingest_channel(
    channel_url: str,
    limit: int,
    min_views: int,
    min_likes: int,
    logger=print
):
    """
    1. Channel se shorts laata hai
    2. Metadata filter lagata hai
    3. Eligible videos download karta hai
    4. UI-friendly result return karta hai
    """

    # -------- get shorts ----------
    logger("🔍 Fetching channel shorts...")
    result = subprocess.check_output(
        ["yt-dlp", "--flat-playlist", "--print", "id", channel_url],
        text=True
    )
    video_ids = result.strip().split("\n")

    downloaded = []
    skipped = []
    checked = 0

    for vid in video_ids:
        if len(downloaded) >= limit:
            break

        checked += 1

        try:
            # -------- fetch metadata ----------
            meta_raw = subprocess.check_output(
                [
                    "yt-dlp",
                    "--dump-json",
                    "--skip-download",
                    "--quiet",
                    vid
                ],
                text=True
            )
            meta = json.loads(meta_raw)

            views = meta.get("view_count") or 0
            likes = meta.get("like_count") or 0

            if views < min_views or likes < min_likes:
                skipped.append(vid)
                continue

            # -------- download ----------
            output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")

            if os.path.exists(output_path):
                logger(f"⏭️ Already exists: {vid}")
                downloaded.append(output_path)
                continue

            subprocess.run(
                [
                    "yt-dlp",
                    "--restrict-filenames",
                    "-f", "bv*+ba/b",
                    "-o", output_path,
                    f"https://www.youtube.com/watch?v={vid}"
                ],
                check=True
            )

            logger(f"✅ Downloaded: {vid}")
            downloaded.append(output_path)

        except Exception as e:
            logger(f"❌ Failed {vid}: {e}")
            skipped.append(vid)
            continue

    return {
        "downloaded": downloaded,
        "skipped": skipped,
        "checked": checked
    }
