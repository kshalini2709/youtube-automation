import os
import json
import shutil
import re
import random

from prompt import build_prompt
from llm_router import generate_text

NORMALIZED_DIR = "normalized"
FINAL_DIR = "final"

os.makedirs(FINAL_DIR, exist_ok=True)


def safe_parse_json(text):
    if not text:
        return None
    try:
        return json.loads(text)
    except Exception:
        pass
    # extract JSON block if wrapped
    try:
        s = text.find("{"); e = text.rfind("}")
        if s != -1 and e != -1:
            return json.loads(text[s:e+1])
    except Exception:
        return None
    return None


# -----------------------------
# CLEAN FILENAME → HUMAN TEXT
# -----------------------------
def clean_title(name: str) -> str:
    name = name.replace("_final", "").replace("_Final", "")
    name = name.replace("_", " ")
    name = re.sub(r"\s+", " ", name)
    return name.strip()

# -----------------------------
# SMART FALLBACK (DYNAMIC)
# -----------------------------
def smart_fallback(cleaned_title, topic):
    # We IGNORE filename words completely
    # We only infer TYPE of video

    title = random.choice([
        "One Decision Changed His Life 🔥",
        "This Moment Changed Everything 😳",
        "Nobody Saw This Coming 👀",
        "A Choice That Changed Life"
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
# 📝 BATCH CAPTION ONLY
# =========================
def generate_captions_for_normalized(
    topic,
    language,
    tone,
    keywords,
    provider,
    logger=print
):
    if not os.path.exists(NORMALIZED_DIR):
        logger("❌ normalized/ folder not found")
        return []

    videos = [v for v in os.listdir(NORMALIZED_DIR) if v.endswith(".mp4")]
    if not videos:
        logger("⚠️ No videos found in normalized/")
        return []

    results = []

    for video in videos:
        raw_base = video.replace(".mp4", "")
        cleaned = clean_title(raw_base)

        src_video = os.path.join(NORMALIZED_DIR, video)
        final_video = os.path.join(FINAL_DIR, video)

        caption_file = os.path.join(FINAL_DIR, f"{raw_base}_caption.txt")
        title_file = os.path.join(FINAL_DIR, f"{raw_base}_title.txt")

        # if os.path.exists(caption_file):
        #     logger(f"⏭️ Skipped (already exists): {video}")
        #     continue

        prompt = build_prompt(
            video_title=cleaned,
            topic=topic,
            language=language,
            tone=tone,
            keywords=keywords or []
        )

        raw = generate_text(prompt, provider)

        # logger(f"RAW AI OUTPUT:\n{raw}\n{'-'*40}")

        data = safe_parse_json(raw)

        if not data or not data.get("title") or not data.get("caption"):
            data = smart_fallback(cleaned, topic)

        shutil.copy2(src_video, final_video)

        with open(caption_file, "w", encoding="utf-8") as f:
            f.write(f"{data['caption']}\n\n{' '.join(data['hashtags'])}")

        with open(title_file, "w", encoding="utf-8") as f:
            f.write(data["title"][:90])

        results.append({
            "video": final_video,
            "caption_file": caption_file,
            "title_file": title_file
        })

        logger(f"✅ Caption generated for {video}")

    logger("🎉 Caption generation completed")
    return results
