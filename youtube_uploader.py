import os
import json
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload
from upload_registry import is_uploaded, mark_uploaded


FINAL_DIR = "final"
TOKENS_DIR = "tokens"


def load_caption(video_path):
    base = os.path.splitext(video_path)[0]
    caption_file = f"{base}_caption.txt"

    if os.path.exists(caption_file):
        with open(caption_file, "r", encoding="utf-8") as f:
            return f.read()

    return ""

def extract_tags_from_caption(caption, max_tags=15):
    tags = []
    for word in caption.split():
        if word.startswith("#"):
            tag = word[1:].strip()
            if tag and tag not in tags:
                tags.append(tag)
        if len(tags) >= max_tags:
            break
    return tags

def load_title(video_path):
    base = os.path.splitext(video_path)[0]
    title_file = f"{base}_title.txt"

    if os.path.exists(title_file):
        with open(title_file, "r", encoding="utf-8") as f:
            return f.read().strip()

    return None


def load_youtube_client(token_path):
    creds = Credentials.from_authorized_user_file(token_path)
    return build("youtube", "v3", credentials=creds)


def upload_video(
    video_path,
    account,
    title=None,
    tags=None,
    privacy="private",
    logger=print
):
    """
    account = {
        channel_id,
        name,
        token_path
    }
    """

    youtube = load_youtube_client(account["token_path"])

    caption = load_caption(video_path)

    title_from_file = load_title(video_path)

    channel_id = account["channel_id"]

    if is_uploaded(video_path, channel_id):
        logger(f"⏭️ Skipped (already uploaded on this account): {video_path}")
        return None

    if not caption:
        logger("⚠️ Caption not found, uploading without description")

    if not title:
        title = title_from_file or os.path.basename(video_path).replace("_final.mp4", "")
        title = title[:95]

    auto_tags = tags or extract_tags_from_caption(caption)
    body = {
        "snippet": {
            "title": title[:95],
            "description": caption[:4900],
            "tags": auto_tags
        },
        "status": {
            "privacyStatus": privacy
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

    try:
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                logger(f"⬆ Upload progress: {int(status.progress() * 100)}%")
                
        mark_uploaded(video_path, channel_id)

    except Exception as e:
        logger(f"❌ Upload failed: {e}")
        return None
    

