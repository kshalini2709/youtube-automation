import os
import subprocess
import shutil

BASE_DIR = "single_link_pipeline"

INPUT_DIR = os.path.join(BASE_DIR, "watermark")
OUTPUT_DIR = os.path.join(BASE_DIR, "normalized")

os.makedirs(OUTPUT_DIR, exist_ok=True)


def normalize_single_video(
    input_video,
    quality_crf=18,
    audio_bitrate="128k",
    logger=print
):
    """
    Single-link normalize + compress
    EXACTLY matches batch normalize behavior

    Input  → single_link_pipeline/watermark/
    Output → single_link_pipeline/normalized/
    """

    if not os.path.exists(input_video):
        logger("❌ Input video not found")
        return None

    # -----------------------------
    # CLEAN BASE NAME (SAME AS BATCH)
    # -----------------------------
    base = os.path.basename(input_video)

    for ext in ("_wm.mp4", ".mp4", ".webm"):
        if base.endswith(ext):
            base = base.replace(ext, "")

    output = os.path.join(OUTPUT_DIR, f"{base}_final.mp4")

    if os.path.exists(output):
        logger(f"⏭️ Already normalized: {output}")
        return output

    # -----------------------------
    # GPU / CPU AUTO DETECT
    # -----------------------------
    has_gpu = shutil.which("nvidia-smi") is not None

    if has_gpu:
        cmd = [
            "ffmpeg", "-y",
            "-i", input_video,

            # VIDEO (GPU + COMPRESSED)
            "-c:v", "h264_nvenc",
            "-preset", "p5",
            "-rc", "vbr",
            "-cq", str(quality_crf),
            "-b:v", "4M",
            "-maxrate", "4M",
            "-bufsize", "8M",

            # AUDIO
            "-af", "loudnorm=I=-14:TP=-1:LRA=11",
            "-c:a", "aac",
            "-b:a", audio_bitrate,
            "-ar", "44100",

            "-profile:v", "high",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",

            output
        ]
    else:
        cmd = [
            "ffmpeg", "-y",
            "-i", input_video,

            # VIDEO (CPU + COMPRESSED)
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", str(quality_crf),

            # AUDIO
            "-af", "loudnorm=I=-14:TP=-1:LRA=11",
            "-c:a", "aac",
            "-b:a", audio_bitrate,
            "-ar", "44100",

            "-profile:v", "high",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",

            output
        ]

    try:
        subprocess.run(cmd, check=True)
        logger(f"✅ NORMALIZED + COMPRESSED (single-link): {output}")
        return output
    except Exception as e:
        logger(f"❌ Normalize failed: {e}")
        return None
