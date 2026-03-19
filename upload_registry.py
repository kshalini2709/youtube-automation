import json
import os

REGISTRY_FILE = "uploaded_registry.json"

def _load():
    if not os.path.exists(REGISTRY_FILE):
        return []
    with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def _save(data):
    with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def is_uploaded(video_path, channel_id):
    data = _load()
    return any(
        item["video_path"] == video_path and item["channel_id"] == channel_id
        for item in data
    )

def mark_uploaded(video_path, channel_id):
    data = _load()
    data.append({
        "video_path": video_path,
        "channel_id": channel_id
    })
    _save(data)
