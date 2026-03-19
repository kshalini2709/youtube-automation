import os
import json
import shutil
import re
import random

from prompt import build_prompt
from llm_router import generate_text

BASE_DIR = "single_link_pipeline"
FINAL_DIR = os.path.join(BASE_DIR, "final")
os.makedirs(FINAL_DIR, exist_ok=True)

# -----------------------------
# SAFE JSON PARSE
# -----------------------------
def safe_parse_json(text):
    if not text:
        return None
    try:
        return json.loads(text)
    except Exception:
        pass
    try:
        s = text.find("{")
        e = text.rfind("}")
        if s != -1 and e != -1:
            return json.loads(text[s:e+1])
    except Exception:
        return None
    return None


# -----------------------------
# CLEAN FILENAME → HUMAN TEXT
# -----------------------------
def clean_title(name: str) -> str:
    name = name.replace("_wm", "").replace("_final", "")
    name = name.replace("_", " ")
    name = re.sub(r"\s+", " ", name)
    return name.strip()


# -----------------------------
# SMART FALLBACK (SAME AS BATCH)
# -----------------------------
def smart_fallback(cleaned_title, topic):
    title = random.choice([
        "This Moment Changed Everything 😳",
        "Nobody Expected This Ending 👀",
        "One Decision Changed His Life 🔥",
        "A Story That Will Shock You"
    ])

    caption = (
        "Life can change in a single moment.\n"
        "What happened next shocked everyone 😳\n"
        "Watch till the end 👀"
    )

    hashtags = [
        "#lifechange",
        "#successmindset",
        "#inspiration",
        "#motivation",
        "#storytime",
        "#mindset",
        "#shorts"
    ]

    return {
        "title": title,
        "caption": caption,
        "hashtags": hashtags
    }


# =========================
# 📝 SINGLE VIDEO CAPTION
# =========================
def generate_caption_for_single_video(
    video_path,
    topic,
    language,
    tone,
    keywords,
    provider,
    logger=print
):
    if not video_path or not os.path.exists(video_path):
        logger("❌ Video not found")
        return None

    base = os.path.basename(video_path)
    raw_name = base.replace(".mp4", "")
    cleaned = clean_title(raw_name)

    caption_file = os.path.join(FINAL_DIR, f"{raw_name}_caption.txt")
    title_file = os.path.join(FINAL_DIR, f"{raw_name}_title.txt")

    prompt = build_prompt(
        video_title=cleaned,
        topic=topic,
        language=language,
        tone=tone,
        keywords=keywords or []
    )

    raw = generate_text(prompt, provider)
    data = safe_parse_json(raw)

    if not data or not data.get("title") or not data.get("caption"):
        logger("⚠️ AI failed → using smart fallback")
        data = smart_fallback(cleaned, topic)

    with open(caption_file, "w", encoding="utf-8") as f:
        f.write(f"{data['caption']}\n\n{' '.join(data['hashtags'])}")

    with open(title_file, "w", encoding="utf-8") as f:
        f.write(data["title"][:90])

    logger("✅ Caption generated")

    return {
        "video": video_path,
        "caption_file": caption_file,
        "title_file": title_file
    }
