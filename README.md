# YouTube Automation Studio (Production Ready)

A complete Streamlit-based YouTube automation system supporting:
- Batch video workflow
- Single-link (one video) workflow
- Watermarking
- Normalization + compression
- AI caption & title generation (credit-safe)
- Manual & scheduled YouTube uploads
- Duplicate upload protection (per account)

This project is designed to run **without GPU, Whisper, or paid AI credits**.

---

## 🔧 System Requirements

- Python 3.10
- Windows OS (tested on Windows 10/11)
- FFmpeg installed and added to PATH
- Internet connection



## 📦 Installation

### 1️⃣ Create virtual environment
python -3.10 -m venv venv
venv\Scripts\activate


### 2️⃣ Install dependencies
pip install -r requirements.txt


---

## 🎞 FFmpeg Setup (MANDATORY)

1. Download FFmpeg from:
   https://www.gyan.dev/ffmpeg/builds/

2. Extract to:
C:\ffmpeg\


3. Add to PATH:
C:\ffmpeg\bin


4. Verify:
ffmpeg -version


---

## 🚀 Run the App

streamlit run app.py


---

## 🧩 Project Structure (Important)

youtube_automation/
│
├── app.py                          # Main Streamlit UI
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
├── .env                            # API keys (OpenAI, Gemini, OpenRouter)
├── client_secret.json              # YouTube OAuth credentials
│
├── uploads/                        # Uploaded logos (watermark)
├── tokens/                         # YouTube OAuth tokens
│
├── downloads/                      # Batch downloaded videos
├── watermarked/                    # Batch watermarked videos
├── normalized/                     # Batch normalized videos
├── final/                          # Batch final videos (ready to upload)
│
├── single_link_pipeline/           # 🔗 SINGLE LINK WORKFLOW (ISOLATED)
│   │
│   ├── download/                   # Single link downloaded video
│   ├── watermark/                  # Single link watermarked video
│   ├── normalized/                 # Single link normalized video
│   ├── final/                      # Single link final video
│   │
│   ├── link_downloader.py          # Single link downloader
│   ├── watermark.py                # Single link watermark logic
│   ├── normalize.py                # Single link normalization
│   ├── caption_generator.py        # Single link caption + title
│   └── youtube_uploader.py         # Single link YouTube uploader
│
├── scheduler/                      # ⏰ BATCH SCHEDULER PIPELINE
│   │
│   ├── scheduler_engine.py
│   ├── scheduler_runner.py
│   └── scheduler_store.py
│
├── caption_generator.py            # Batch caption generator
├── llm_router.py                   # LLM provider router (OpenAI / Gemini)
├── prompt.py                       # Caption & title prompt templates
├── config.py                       # Central configuration
├── ingest.py                       # Batch ingest logic
│
├── youtube_auth.py                 # YouTube OAuth helper
├── youtube_uploader.py             # Batch YouTube uploader
├── upload_registry.py              # Prevent duplicate uploads
├── uploaded_registry.json          # Upload history
│
├── normalize.py                    # Batch normalize logic
└── watermark.py                    # Batch watermark logic


---

## 🔄 Workflows

### 🔗 Single Link Pipeline
- Download (mandatory)
- Watermark (optional)
- Normalize (optional)
- Caption & Title generation (optional)
- Upload (manual)

All steps are **independent**.  
User can skip any step.

---

### 📦 Batch Pipeline
- Folder ingest
- Batch watermark
- Batch normalization
- Batch caption generation
- Batch upload / scheduler

---

## 📝 Caption Generation

- Video filename + user inputs used
- AI providers:
  - OpenRouter
  - Gemini
- Credit-safe fallback captions
- Always generates:
  - `_title.txt`
  - `_caption.txt`

---

## ⏰ Scheduler Safety

- No duplicate uploads per account
- Manual uploads are tracked
- Same video can upload to different channels safely

---

## ❗ Important Notes for Client

- GPU is optional; CPU-only is fully supported
- Project is production-ready and crash-safe



## ✅ Status

✔ Production Ready  
✔ Client Deliverable  
✔ Stable without paid AI credits  
✔ Windows Compatible  