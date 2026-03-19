import json

def build_prompt(video_title, topic, language, tone, keywords):
    context = {
        "video_meaning": video_title,
        "user_topic": topic,
        "language": language or "auto-detect",
        "tone": tone or "emotional, high-retention",
        "keywords": keywords or []
    }

    context_json = json.dumps(context, ensure_ascii=False)

    return f"""
You are a YouTube Shorts copywriter.

Below is VIDEO CONTEXT provided as JSON.
You must understand the MEANING, not copy words.

VIDEO_CONTEXT:
{context_json}

IMPORTANT GUIDELINES:
- Avoid copying exact words from the filename
- You may rephrase ideas in a natural human way
- Focus on the story, emotion, or concept behind the video

TASK:
Generate:
1. A NEW clickable title (5–8 words)
2. A NEW engaging caption (2–3 lines)
3. Relevant hashtags (8–12 total)

Rules:
- Title & caption should feel rewritten, not copied
- Emojis allowed naturally
- Optimized for Shorts / Reels

Return ONLY valid JSON:
{{
  "title": "",
  "caption": "",
  "hashtags": []
}}
"""
