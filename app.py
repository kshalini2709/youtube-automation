import streamlit as st
import os

# from link_downloader
from single_link_pipeline.link_downloader import download_single_video
from single_link_pipeline.watermark import watermark_single_video
from single_link_pipeline.normalize import normalize_single_video
from single_link_pipeline.caption_generator import generate_caption_for_single_video
from single_link_pipeline.youtube_uploader import upload_single_video


# from batch downloader
from ingest import ingest_channel
from watermark import watermark_video
from normalize import normalize_video
from caption_generator import generate_captions_for_normalized
from youtube_auth import load_accounts
from youtube_uploader import upload_video

# =======================
# COMMON WATERMARK CONTROLS
# =======================
def watermark_controls():
    text = st.text_input("Watermark Text", "@yourbrand")
    text_size = st.slider("Text Size", 0.5, 5.0, 1.5, 0.1)
    text_opacity = st.slider("Text Opacity", 0.1, 1.0, 0.8)

    text_x = st.slider("Text Base X (%)", 0, 100, 50)
    text_y = st.slider("Text Base Y (%)", 0, 100, 80)

    move_text = st.toggle("Smooth Moving Text", value=True)
    move_radius = st.slider("Text Movement Area (%)", 1, 15, 6)

    st.divider()
    st.markdown("### 🖼 Logos")

    top_logo = st.file_uploader("Top Logo (PNG)", type=["png"])
    bottom_logo = st.file_uploader("Bottom Logo (PNG)", type=["png"])

    logo_width = st.slider("Logo Width", 50, 400, 180)
    logo_opacity = st.slider("Logo Opacity", 0.1, 1.0, 1.0)

    top_logo_x = st.slider("Top Logo X (%)", 0, 100, 50)
    top_logo_y = st.slider("Top Logo Y (%)", 0, 50, 5)

    bottom_logo_x = st.slider("Bottom Logo X (%)", 0, 100, 50)
    bottom_logo_y = st.slider("Bottom Logo Y (%)", 50, 100, 90)

    # -------- SAVE LOGOS --------
    os.makedirs("uploads", exist_ok=True)

    top_logo_path = None
    bottom_logo_path = None

    if top_logo:
        top_logo_path = os.path.join("uploads", top_logo.name)
        with open(top_logo_path, "wb") as f:
            f.write(top_logo.read())

    if bottom_logo:
        bottom_logo_path = os.path.join("uploads", bottom_logo.name)
        with open(bottom_logo_path, "wb") as f:
            f.write(bottom_logo.read())

    return {
        "text": text,
        "text_size": text_size,
        "text_opacity": text_opacity,
        "text_x": text_x,
        "text_y": text_y,
        "move_text": move_text,
        "move_radius": move_radius,
        "top_logo_path": top_logo_path,
        "bottom_logo_path": bottom_logo_path,
        "top_logo_x": top_logo_x,
        "top_logo_y": top_logo_y,
        "bottom_logo_x": bottom_logo_x,
        "bottom_logo_y": bottom_logo_y,
        "logo_width": logo_width,
        "logo_opacity": logo_opacity,
    }

st.set_page_config(
    page_title="YouTube Automation Studio",
    page_icon="🎬",
    layout="wide"
)

st.markdown("""
<style>

/* ===== GLOBAL ===== */
.main {
    background-color: #0f1117;
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 4rem;
}

/* ===== CARD ===== */
.section-card {
    background: #151922;
    border-radius: 16px;
    padding: 18px 20px;
    margin-bottom: 20px;
    box-shadow: 0 10px 28px rgba(0,0,0,0.35);
    animation: fadeUp 0.45s ease;
}

/* ===== TITLES ===== */
.section-title {
    font-size: 1.05rem;
    font-weight: 700;
    margin-bottom: 10px;
}

/* ===== VIDEO CONTROL ===== */
.video-wrapper video {
    max-height: 100px;          /* 🔥 video size control */
    width: 100%;
    border-radius: 14px;
    object-fit: contain;
    background: black;
}

/* ===== SETTINGS PANEL ===== */
.settings-panel {
    max-height: 100px;          /* 🔥 right side height */
    overflow-y: auto;
    padding-right: 6px;
}

/* ===== SCROLLBAR ===== */
.settings-panel::-webkit-scrollbar {
    width: 6px;
}
.settings-panel::-webkit-scrollbar-thumb {
    background: #2b2f3a;
    border-radius: 10px;
}

/* ===== BUTTON ===== */
.stButton button {
    width: 100%;
    height: 44px;
    border-radius: 12px;
    font-weight: 600;
    background: linear-gradient(135deg,#ff416c,#ff4b2b);
    border: none;
    color: white;
    transition: transform .15s ease, box-shadow .15s ease;
}
.stButton button:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 20px rgba(255,75,43,0.35);
}

/* ===== INPUTS ===== */
.stTextInput input,
.stSelectbox div,
.stSlider {
    border-radius: 10px;
}

/* ===== ANIMATION ===== */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}

</style>
""", unsafe_allow_html=True)

# =======================
# SIDEBAR NAVIGATION
# =======================
st.sidebar.title("⚙️ Studio")
mode = st.sidebar.radio(
    "Select Mode",
    [
        "🔗 Link Download & Post",
        "📥 Ingest & Download",
        "💧 Watermark Downloads",
        "⚖️ Normalize Videos",
        "📝 Caption Generator",
        "📺 YouTube Accounts",
        "📤 Upload to YouTube",
        "⏰ Scheduler"
    ]
)

# =======================
# 🔗 LINK → DOWNLOAD → WATERMARK → NORMALIZE
# =======================
if mode == "🔗 Link Download & Post":
    st.title("🔗 Single Link Video Pipeline")

    # ---------- SESSION STATE ----------
    for k in ["sl_downloaded", "sl_watermarked", "sl_normalized"]:
        if k not in st.session_state:
            st.session_state[k] = None

    def current_video():
        return (
            st.session_state.sl_normalized
            or st.session_state.sl_watermarked
            or st.session_state.sl_downloaded
        )

    # =======================
    # 1️⃣ DOWNLOAD
    # =======================
    st.subheader("1️⃣ Download Video")

    col_left, col_right = st.columns([0.4, 0.8])

    with col_left:
        if st.session_state.sl_downloaded:
            st.markdown("<div class='section-card'>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>🎥 Download Preview</div>", unsafe_allow_html=True)
            st.markdown("<div class='video-wrapper'>", unsafe_allow_html=True)
            st.video(st.session_state.sl_downloaded)
            st.markdown("</div></div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>📥 Download Settings</div>", unsafe_allow_html=True)

        video_url = st.text_input(
            "YouTube Video / Shorts URL",
            placeholder="https://youtube.com/watch?v=xxxx"
        )

        if st.button("⬇ Download Video"):
            if not video_url:
                st.warning("Paste a valid YouTube URL")
            else:
                with st.spinner("Downloading..."):
                    out = download_single_video(video_url, logger=st.write)
                if out:
                    st.session_state.sl_downloaded = out
                    st.session_state.sl_watermarked = None
                    st.session_state.sl_normalized = None
                    st.success("✅ Download completed")

        st.markdown("</div>", unsafe_allow_html=True)

    if not st.session_state.sl_downloaded:
        st.stop()

    # =======================
    # 2️⃣ WATERMARK
    # =======================
    st.subheader("2️⃣ Watermark (Optional)")

    col_left, col_right = st.columns([0.4, 0.8])

    with col_left:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>🎥 Watermark Preview</div>", unsafe_allow_html=True)
        st.markdown("<div class='video-wrapper'>", unsafe_allow_html=True)
        st.video(current_video())
        st.markdown("</div></div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("<div class='section-card settings-panel'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>⚙️ Watermark Settings</div>", unsafe_allow_html=True)

        controls = watermark_controls()

        if st.button("💧 Apply / Re-Apply Watermark"):
            with st.spinner("Applying watermark..."):
                wm = watermark_single_video(
                    input_video=st.session_state.sl_downloaded,
                    **controls,
                    logger=st.write
                )
            st.session_state.sl_watermarked = wm
            st.session_state.sl_normalized = None
            st.success("✅ Watermark applied")

        st.markdown("</div>", unsafe_allow_html=True)

    # =======================
    # 3️⃣ NORMALIZE
    # =======================
    st.subheader("3️⃣ Normalize (Optional)")

    col_left, col_right = st.columns([0.4, 0.8])

    with col_left:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>🎥 Normalize Preview</div>", unsafe_allow_html=True)
        st.markdown("<div class='video-wrapper'>", unsafe_allow_html=True)
        st.video(current_video())
        st.markdown("</div></div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("<div class='section-card settings-panel'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>⚖️ Normalize Settings</div>", unsafe_allow_html=True)

        quality = st.slider("Video Quality (CRF)", 18, 28, 22)
        audio_bitrate = st.selectbox(
            "Audio Bitrate",
            ["96k", "128k", "160k", "192k"],
            index=1
        )

        if st.button("⚖️ Normalize Video"):
            with st.spinner("Normalizing..."):
                norm = normalize_single_video(
                    input_video=current_video(),
                    quality_crf=quality,
                    audio_bitrate=audio_bitrate,
                    logger=st.write
                )
            st.session_state.sl_normalized = norm
            st.success("✅ Normalized successfully")

        st.markdown("</div>", unsafe_allow_html=True)

    # =======================
    # 4️⃣ CAPTION GENERATOR (SINGLE LINK)
    # =======================
    st.subheader("4️⃣ Caption Generator (Optional)")

    col_left, col_right = st.columns([0.4, 0.8])

    # -------- LEFT : VIDEO PREVIEW --------
    with col_left:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>🎥 Caption Preview Video</div>", unsafe_allow_html=True)

        st.markdown("<div class='video-wrapper'>", unsafe_allow_html=True)
        st.video(current_video())
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # -------- RIGHT : CAPTION SETTINGS --------
    with col_right:
        st.markdown("<div class='section-card settings-panel'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>📝 Caption Settings</div>", unsafe_allow_html=True)

        topic = st.text_input(
            "Topic / Context",
            placeholder="Motivation, MrBeast style, Success story"
        )

        language = st.text_input(
            "Language",
            placeholder="English, Hindi, Hinglish, Tamil"
        )

        tone = st.text_input(
            "Tone / Style",
            placeholder="Viral, Emotional, Aggressive, Inspirational"
        )

        keywords_raw = st.text_input(
            "Extra Keywords (optional)",
            placeholder="success, mindset, shorts"
        )

        provider = st.selectbox(
            "AI Provider",
            ["openrouter", "gemini"],
            index=0
        )

        keywords = [k.strip() for k in keywords_raw.split(",") if k.strip()]

        if st.button("🧠 Generate Caption + Title", use_container_width=True):
            if not topic:
                st.warning("Topic is required")
            else:
                with st.spinner("Generating caption..."):
                    result = generate_caption_for_single_video(
                        video_path=current_video(),
                        topic=topic,
                        language=language,
                        tone=tone,
                        keywords=keywords,
                        provider=provider,
                        logger=st.write
                    )

                if result:
                    st.success("✅ Caption generated")
                    st.write("📄 Caption file:", result["caption_file"])
                    st.write("🏷️ Title file:", result["title_file"])

        st.markdown("</div>", unsafe_allow_html=True)
    
    # =======================
    # 5️⃣ UPLOAD TO YOUTUBE (SINGLE LINK)
    # =======================
    st.subheader("5️⃣ Upload to YouTube (Optional)")

    col_left, col_right = st.columns([0.4, 0.8])

    # -------- LEFT : FINAL VIDEO PREVIEW --------
    with col_left:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>🎥 Final Video</div>", unsafe_allow_html=True)

        st.markdown("<div class='video-wrapper'>", unsafe_allow_html=True)
        st.video(current_video())
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # -------- RIGHT : UPLOAD SETTINGS --------
    with col_right:
        st.markdown("<div class='section-card settings-panel'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>📤 Upload Settings</div>", unsafe_allow_html=True)

        # ====== READ TITLE / CAPTION FROM FINAL FOLDER ======
        final_dir = os.path.join("single_link_pipeline", "final")
        video_base = os.path.splitext(os.path.basename(current_video()))[0]

        title_path = os.path.join(final_dir, f"{video_base}_title.txt")
        caption_path = os.path.join(final_dir, f"{video_base}_caption.txt")


        title_text = ""
        caption_text = ""

        if os.path.exists(title_path):
            with open(title_path, "r", encoding="utf-8") as f:
                title_text = f.read().strip()

        if os.path.exists(caption_path):
            with open(caption_path, "r", encoding="utf-8") as f:
                caption_text = f.read().strip()

        st.markdown("### 📝 Caption & Title Preview")

        if not title_text or not caption_text:
            st.warning("⚠️ Caption/Title not found in final folder. Generate caption first.")
        else:
            title_text = st.text_input(
                "Title (editable)",
                value=title_text
            )

            caption_text = st.text_area(
                "Description (editable)",
                value=caption_text,
                height=200
            )

        st.divider()

        # ====== ACCOUNT / PRIVACY ======
        accounts = load_accounts()

        if not accounts:
            st.warning("⚠️ No YouTube accounts found. Please add an account first.")
        else:
            account = st.selectbox(
                "Select Channel",
                accounts,
                format_func=lambda x: x["name"]
            )

            privacy = st.selectbox(
                "Privacy",
                ["public", "unlisted", "private"],
                index=2
            )

            if st.button("🚀 Upload Video", use_container_width=True):
                if not title_text or not caption_text:
                    st.warning("Generate caption before uploading.")
                else:
                    with st.spinner("Uploading video to YouTube..."):
                        ok = upload_single_video(
                            video_path=current_video(),
                            title=title_text,
                            description=caption_text,
                            account=account,
                            privacy=privacy,
                            logger=st.write
                        )

                    if ok:
                        st.success("🎉 Video uploaded successfully")
                    else:
                        st.warning("⚠️ Upload skipped or failed")

        st.markdown("</div>", unsafe_allow_html=True)


# =======================
# 📥 INGEST MODE
# =======================
if mode == "📥 Ingest & Download":
    st.title("📥 Ingest Shorts")

    with st.form("ingest"):
        url = st.text_input("Channel URL")
        limit = st.number_input("Max Videos", 1, 20, 5)
        min_views = st.number_input("Min Views", 0)
        min_likes = st.number_input("Min Likes", 0)
        run = st.form_submit_button("Start Ingest")

    if run:
        with st.spinner("Downloading…"):
            result = ingest_channel(
                url, limit, min_views, min_likes, logger=st.write
            )
        st.success(f"Downloaded {len(result['downloaded'])} videos")

# =======================
# 💧 WATERMARK DOWNLOADS
# =======================
if mode == "💧 Watermark Downloads":
    st.title("💧 Watermark Downloaded Videos")

    downloads_dir = "downloads"
    os.makedirs(downloads_dir, exist_ok=True)

    videos = [
        f for f in os.listdir(downloads_dir)
        if f.endswith((".mp4", ".webm"))
    ]

    if not videos:
        st.warning("No videos found in downloads folder")
    else:
        selected = st.selectbox(
            "Select a video to preview watermark",
            videos
        )

        preview_path = os.path.join(downloads_dir, selected)

        colA, colB = st.columns([0.4, 0.8])

        with colA:
            st.video(preview_path)

        with colB:
            controls = watermark_controls()

        if st.button("▶ Preview on Selected Video"):
            preview_out = watermark_video(
                input_video=preview_path,
                **controls,
                logger=st.write
            )
            st.video(preview_out)

        st.divider()

        if st.button("✅ Apply Same Watermark to ALL Downloads"):
            for vid in videos:
                src = os.path.join(downloads_dir, vid)

                base = vid
                for ext in (".mp4.webm", ".webm", ".mp4"):
                    if base.endswith(ext):
                        base = base[:-len(ext)]

                wm_path = os.path.join("watermarked", f"{base}_wm.mp4")

                if os.path.exists(wm_path):
                    st.write(f"⏭️ Skipped: {vid}")
                    continue

                with st.spinner(f"Watermarking {vid}"):
                    watermark_video(
                        input_video=src,
                        **controls,
                        logger=st.write
                    )

            st.success("🎉 Batch watermark completed")

# =======================
# 🎚 NORMALIZE MODE
# =======================
if mode == "⚖️ Normalize Videos":
    st.title("⚖️ Normalize Watermarked Videos")

    watermarked_dir = "watermarked"
    final_dir = "final"

    os.makedirs(watermarked_dir, exist_ok=True)
    os.makedirs(final_dir, exist_ok=True)

    videos = [
        f for f in os.listdir(watermarked_dir)
        if f.endswith("_wm.mp4")
    ]

    if not videos:
        st.warning("No watermarked videos found")
    else:
        selected = st.selectbox(
            "Select a video to preview normalize",
            videos
        )

        selected_path = os.path.join(watermarked_dir, selected)

        colA, colB = st.columns([0.4, 0.8])

        with colA:
            st.video(selected_path)

        with colB:
            quality = st.slider("Quality (Lower = Better)", 16, 28, 18)
            audio_bitrate = st.selectbox(
                "Audio Bitrate",
                ["96k", "128k", "160k", "192k"],
                index=1
            )

        if st.button("▶ Preview Normalize"):
            out = normalize_video(
                input_video=selected_path,
                quality_crf=quality,
                audio_bitrate=audio_bitrate,
                logger=st.write
            )
            st.video(out)

        st.divider()

        if st.button("✅ Normalize ALL Watermarked Videos"):
            for vid in videos:
                src = os.path.join(watermarked_dir, vid)
                base = vid.replace("_wm.mp4", "")
                final_path = os.path.join(final_dir, f"{base}_final.mp4")

                if os.path.exists(final_path):
                    st.write(f"⏭️ Skipped: {vid}")
                    continue

                with st.spinner(f"Normalizing {vid}"):
                    normalize_video(
                        input_video=src,
                        quality_crf=quality,
                        audio_bitrate=audio_bitrate,
                        logger=st.write
                    )

            st.success("🎉 All videos normalized")


# =====================
# 📝 CAPTION GENERATOR
# =====================
if mode == "📝 Caption Generator":
    st.title("📝 Caption Generator")

    st.markdown(
        """  
        🧠 Captions are generated by **understanding the video filename**  
        ✍️ Topic / tone / language are used to guide the writing style  
        📁 Output files are saved inside `final/` folder  
        """
    )

    colA, colB = st.columns([1, 1])

    # -------- USER INPUTS --------
    with colA:
        topic = st.text_input(
            "Overall Context / Theme (required)",
            placeholder="e.g. Motivation, Tech facts, Life stories"
        )

        language = st.text_input(
            "Language",
            placeholder="Hindi, Hinglish, English, Tamil, Gujarati, etc"
        )

        tone = st.text_input(
            "Tone / Style",
            placeholder="Emotional, Curious, Viral, Serious"
        )

        keywords_raw = st.text_input(
            "Extra Keywords (optional)",
            placeholder="success, mindset, shorts"
        )

        provider = st.selectbox(
            "AI Provider",
            ["openrouter", "gemini"]
        )

        keywords = [k.strip() for k in keywords_raw.split(",") if k.strip()]

    # -------- NORMALIZED VIDEOS --------
    normalized_dir = "normalized"
    videos = (
        [f for f in os.listdir(normalized_dir) if f.endswith(".mp4")]
        if os.path.exists(normalized_dir)
        else []
    )

    with colB:
        st.subheader("📂 Normalized Videos")

        if not videos:
            st.warning("No videos found in `normalized/` folder")
        else:
            st.success(f"{len(videos)} videos ready")

            st.caption(
                "⚠️ Tip: Video filenames should describe the video clearly for best results"
            )

            with st.expander("📄 View video list"):
                for v in videos:
                    st.write("•", v)

    st.divider()

    # -------- ACTION --------
    if st.button("🚀 Generate Captions for ALL Videos"):
        if not videos:
            st.warning("Please normalize videos first.")
            st.stop()

        if not topic:
            st.warning("Overall context is required.")
            st.stop()

        with st.spinner("✍️ Understanding video & generating captions..."):
            result = generate_captions_for_normalized(
                topic=topic,
                language=language,
                tone=tone,
                keywords=keywords,
                provider=provider,
                logger=st.write
            )

        st.success("🎉 Caption generation completed")

        if result:
            st.subheader("✅ Generated Files")
            for item in result:
                st.write("📹", item["video"])
                st.write("🏷️", item["title_file"])
                st.write("📝", item["caption_file"])

# =====================
# 📺 YouTube Accounts
# =====================

if mode == "📺 YouTube Accounts":
    st.title("📺 YouTube Accounts")

    from youtube_auth import add_youtube_account, load_accounts

    if st.button("➕ Add YouTube Account"):
        try:
            acc = add_youtube_account()
            st.success(f"✅ Account added: {acc['name']}")
        except Exception as e:
            st.error(str(e))

    st.divider()

    accounts = load_accounts()
    if not accounts:
        st.warning("No YouTube accounts added yet")
    else:
        for acc in accounts:
            st.write(f"✅ {acc['name']} ({acc['channel_id']})")


# =======================
# 📤 YOUTUBE UPLOAD
# =======================
if mode == "📤 Upload to YouTube":
    st.title("📤 Upload Videos to YouTube")

    accounts = load_accounts()

    if not accounts:
        st.warning("No YouTube accounts added yet")
        st.stop()

    # -------- ACCOUNT SELECT --------
    account_map = {
        f"{acc['name']} ({acc['channel_id']})": acc
        for acc in accounts
    }

    selected_account_name = st.selectbox(
        "Select YouTube Account",
        list(account_map.keys())
    )

    account = account_map[selected_account_name]

    # -------- LOAD FINAL VIDEOS --------
    final_dir = "final"
    videos = [
        f for f in os.listdir(final_dir)
        if f.endswith("_final.mp4")
    ]

    if not videos:
        st.warning("No videos found in final/ folder")
        st.stop()

    st.subheader("📂 Final Videos")

    selected_video = st.selectbox(
        "Select video for preview",
        videos
    )

    video_path = os.path.join(final_dir, selected_video)

    # -------- PREVIEW --------
    colA, colB = st.columns([0.4, 0.8])

    with colA:
        st.video(video_path)

    with colB:
        
        title_path = video_path.replace("_final.mp4", "_final_title.txt")

        if os.path.exists(title_path):
            with open(title_path, "r", encoding="utf-8") as f:
                title = f.read()
        else:
            title = ""

        st.subheader("🏷 Auto Loaded Title")
        title_input = st.text_input(
            "Video Title",
            value=title,
            max_chars=100
        )
   
        caption_path = video_path.replace("_final.mp4", "_final_caption.txt")

        if os.path.exists(caption_path):
            with open(caption_path, "r", encoding="utf-8") as f:
                caption = f.read()
        else:
            caption = ""

        st.subheader("📝 Auto Loaded Caption")
        st.text_area(
            "Caption Preview",
            caption,
            height=300
        )

        privacy = st.selectbox(
            "Privacy",
            ["private", "unlisted", "public"],
            index=0
        )

    st.divider()

    # -------- SINGLE UPLOAD --------
    if st.button("🚀 Upload Selected Video"):
        with st.spinner("Uploading video..."):
            upload_video(
                video_path=video_path,
                account=account,
                title=title_input,
                privacy=privacy,
                logger=st.write
            )
        st.success("🎉 Upload completed")

    st.divider()

    # -------- BULK UPLOAD --------
    if st.button("🔥 Upload ALL Final Videos"):
        for vid in videos:
            path = os.path.join(final_dir, vid)

            with st.spinner(f"Uploading {vid}"):
                upload_video(
                    video_path=path,
                    account=account,
                    title=title_input,
                    privacy=privacy,
                    logger=st.write
                )

        st.success("🎉 All videos uploaded successfully")

# =======================
# ⏰ Scheduler
# =======================

import threading
from datetime import datetime, date, time, timedelta

from scheduler.scheduler_engine import start_scheduler
from scheduler.scheduler_store import add_job, load_jobs, remove_job, update_job
from youtube_auth import load_accounts

# ---- START SCHEDULER ONCE ----
if "scheduler_started" not in st.session_state:
    t = threading.Thread(
        target=start_scheduler,
        kwargs={"logger": print},
        daemon=True
    )
    t.start()
    st.session_state.scheduler_started = True

if mode == "⏰ Scheduler":
    st.title("⏰ YouTube Batch Scheduler")

    st.success("🟢 Scheduler engine is running in background")

    # -------- LOAD ACCOUNTS --------
    accounts = load_accounts()
    if not accounts:
        st.warning("⚠️ No YouTube accounts added yet")
        st.stop()

    # -------- LOAD FINAL VIDEOS --------
    final_dir = "final"
    videos = sorted([
        f for f in os.listdir(final_dir)
        if f.endswith(".mp4")
    ])

    if not videos:
        st.warning("⚠️ No videos found in final/ folder")
        st.stop()

    st.info(f"📂 {len(videos)} videos found in final folder")

    # -------- SELECT ACCOUNT --------
    account = st.selectbox(
        "📺 Select Channel",
        accounts,
        format_func=lambda x: x["name"]
    )

    # -------- PRIVACY --------
    privacy = st.selectbox(
        "Privacy",
        ["private", "unlisted", "public"]
    )

    # -------- GAP --------
    gap_minutes = st.selectbox(
        "⏱ Gap between uploads (minutes)",
        [1, 2, 5, 10, 20, 30, 60],
        index=2
    )

    # -------- DATE & TIME --------
    col1, col2 = st.columns(2)
    with col1:
        run_date = st.date_input("📅 Start Date", min_value=date.today())
    with col2:
        run_time = st.time_input(
            "⏰ Start Time",
            value=time(12, 0),
            step=timedelta(minutes=1)
        )

    start_dt = datetime.combine(run_date, run_time)

    st.divider()

    # -------- SCHEDULE ALL --------
    if st.button("🚀 Schedule ALL Final Videos"):
        for idx, vid in enumerate(videos):
            video_path = os.path.join(final_dir, vid)
            scheduled_time = start_dt + timedelta(minutes=gap_minutes * idx)

            add_job({
                "video_path": video_path,
                "account": account,
                "privacy": privacy,
                "scheduled_at": scheduled_time.isoformat()
            })

        st.success("✅ All videos scheduled successfully")

    st.divider()

    # -------- SHOW JOBS --------
    st.subheader("📋 Scheduled Jobs")
    jobs = load_jobs()

    if not jobs:
        st.info("No scheduled uploads yet")
    else:
        for job in jobs:
            colA, colB, colC = st.columns([5, 2, 2])

            with colA:
                st.write(
                    f"🎬 **{os.path.basename(job['video_path'])}**\n\n"
                    f"📺 {job['account']['name']}\n\n"
                    f"⏰ {job['scheduled_at']}\n\n"
                    f"🔒 {job['privacy']}"
                )

            with colB:
                status = job["status"]
                if status == "pending":
                    st.warning("🟡 Pending")
                elif status == "running":
                    st.info("🔵 Running")
                elif status == "done":
                    st.success("🟢 Done")
                elif status == "failed":
                    st.error("🔴 Failed")

            with colC:
                if job["status"] == "failed":
                    if st.button("🔁 Retry", key=f"retry_{job['id']}"):
                        update_job(
                            job["id"],
                            status="pending",
                            last_error=None
                        )
                        st.experimental_rerun()

                if st.button("❌ Cancel", key=f"del_{job['id']}"):
                    remove_job(job["id"])
                    st.experimental_rerun()
