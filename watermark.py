import os
import subprocess
import shutil

OUTPUT_DIR = "watermarked"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def watermark_video(
    input_video,
    text,
    text_size,          # now expects SMALL values (0.5 – 5)
    text_opacity,
    text_x,             # base X (%)
    text_y,             # base Y (%)
    move_text=True,
    move_radius=6,      # 🔥 NEW: how much text floats (in %)
    top_logo_path=None,
    bottom_logo_path=None,
    top_logo_x=50,      # 🔥 NEW
    top_logo_y=5,       # 🔥 NEW
    bottom_logo_x=50,   # 🔥 NEW
    bottom_logo_y=90,   # 🔥 NEW
    logo_width=200,
    logo_opacity=1.0,
    logger=print
):
    base = os.path.basename(input_video)

    for ext in (".mp4.webm", ".webm", ".mp4"):
        if base.lower().endswith(ext):
            base = base[:-len(ext)]
    
    name = base
    output = os.path.join(OUTPUT_DIR, f"{name}_wm.mp4")

    has_gpu = shutil.which("nvidia-smi") is not None

    gpu_args = [
        "-c:v", "h264_nvenc",
        "-preset", "p7",
        "-rc", "vbr",
        "-cq", "18",
        
        "-b:v", "4M",
        "-maxrate", "4M",
        "-bufsize", "8M",
    ]

    cpu_args = [
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "17"
    ]

    # -----------------------------
    # TEXT POSITION (FLOAT AROUND BASE)
    # -----------------------------
    base_x = f"(w-text_w)*{text_x/100}"
    base_y = f"(h-text_h)*{text_y/100}"

    if move_text:
        x_expr = f"{base_x} + sin(t*0.6)*(w*{move_radius/100})"
        y_expr = f"{base_y} + cos(t*0.4)*(h*{move_radius/100})"
    else:
        x_expr = base_x
        y_expr = base_y

    filters = [
        f"[0:v]drawtext="
        f"text='{text}':"
        f"font=Arial:"
        f"fontsize=h*{text_size/100}:"  # 👈 FIXED SCALE
        f"fontcolor=white@{text_opacity}:"
        f"borderw=2:"
        f"bordercolor=black@{text_opacity}:"
        f"x={x_expr}:"
        f"y={y_expr}"
        "[v1]"
    ]

    inputs = ["-i", input_video]
    last = "v1"
    idx = 1

    # -----------------------------
    # TOP LOGO (FULL POSITION CONTROL)
    # -----------------------------
    if top_logo_path:
        inputs += ["-i", top_logo_path]
        filters.append(
            f"[{idx}:v]scale={logo_width}:-1,"
            f"format=rgba,colorchannelmixer=aa={logo_opacity}[toplogo]"
        )
        filters.append(
            f"[{last}][toplogo]overlay="
            f"x=(W-w)*{top_logo_x/100}:"
            f"y=(H-h)*{top_logo_y/100}[vtop]"
        )
        last = "vtop"
        idx += 1

    # -----------------------------
    # BOTTOM LOGO (FULL POSITION CONTROL)
    # -----------------------------
    if bottom_logo_path:
        inputs += ["-i", bottom_logo_path]
        filters.append(
            f"[{idx}:v]scale={logo_width}:-1,"
            f"format=rgba,colorchannelmixer=aa={logo_opacity}[bottomlogo]"
        )
        filters.append(
            f"[{last}][bottomlogo]overlay="
            f"x=(W-w)*{bottom_logo_x/100}:"
            f"y=(H-h)*{bottom_logo_y/100}[outv]"
        )
        last = "outv"

    filter_complex = ";".join(filters)

    base_cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", f"[{last}]",
        "-map", "0:a?",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        output
    ]

    try:
        if has_gpu:
            subprocess.run(base_cmd[:-1] + gpu_args + [output], check=True)
            logger(f"✅ WATERMARKED (GPU): {output}")
            return output
        else:
            raise subprocess.CalledProcessError(1, "gpu")

    except subprocess.CalledProcessError:
        logger("⚠️ GPU failed → CPU fallback")
        subprocess.run(base_cmd[:-1] + cpu_args + [output], check=True)
        logger(f"✅ WATERMARKED (CPU): {output}")
        return output
