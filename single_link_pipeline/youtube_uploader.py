import os
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload

from upload_registry import is_uploaded, mark_uploaded

BASE_DIR = "single_link_pipeline"
FINAL_DIR = os.path.join(BASE_DIR, "final")


# ----------------------------
# LOAD TITLE + CAPTION
# ----------------------------
def load_caption_and_title(video_path):
    base = os.path.splitext(os.path.basename(video_path))[0]

    title_path = os.path.join(FINAL_DIR, f"{base}_title.txt")
    caption_path = os.path.join(FINAL_DIR, f"{base}_caption.txt")

    title = None
    description = None
    tags = []

    if os.path.exists(title_path):
        with open(title_path, "r", encoding="utf-8") as f:
            title = f.read().strip()

    if os.path.exists(caption_path):
        with open(caption_path, "r", encoding="utf-8") as f:
            text = f.read()
            description = text
            tags = [w[1:] for w in text.split() if w.startswith("#")]

    return title, description, tags


# ----------------------------
# LOAD YOUTUBE CLIENT (TOKEN)
# ----------------------------
def load_youtube_client(token_path):
    creds = Credentials.from_authorized_user_file(token_path)
    return build("youtube", "v3", credentials=creds)


# ============================
# 🚀 SINGLE LINK UPLOADER
# ============================
def upload_single_video(
    video_path,
    account,
    title=None,
    description=None,
    privacy="private",
    override_title=None,
    extra_tags=None,
    logger=print
):

    if not video_path or not os.path.exists(video_path):
        logger("❌ Video not found")
        return False

    video_id = os.path.basename(video_path)
    channel_id = account["channel_id"]

    # ---- DUPLICATE SAFETY ----
    if is_uploaded(video_id, channel_id):
        logger("⏭️ Already uploaded for this account")
        return False

    # ---- LOAD METADATA ----
    file_title, file_description, tags = load_caption_and_title(video_path)

    # PRIORITY:
    # UI title > override title > file title
    title = title or override_title or file_title

    # UI description > file description
    description = description or file_description

    # merge extra tags
    if extra_tags:
        tags = list(set((tags or []) + extra_tags))

    # final fallbacks (absolute safety)
    if not title:
        title = os.path.splitext(video_id)[0][:90]

    if not description:
        description = "Watch till the end 👀"

    # ---- AUTH ----
    youtube = load_youtube_client(account["token_path"])

    body = {
        "snippet": {
            "title": title[:95],
            "description": description[:4900],
            "tags": tags[:15],
            "categoryId": "22"
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(
        video_path,
        chunksize=-1,
        resumable=True,
        mimetype="video/mp4"
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    logger("🚀 Uploading video...")

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            logger(f"⬆ Upload progress: {int(status.progress() * 100)}%")

    mark_uploaded(video_path, channel_id)
    logger("✅ Upload successful")
    return True
