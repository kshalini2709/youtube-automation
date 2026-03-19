import os
from dotenv import load_dotenv

load_dotenv()

# ===== OpenAI =====
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# ===== OpenRouter =====
OPENROUTER_KEYS = [
    k.strip() for k in os.getenv("OPENROUTER_KEYS", "").split(",") if k.strip()
]
OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "meta-llama/llama-3.1-8b-instruct"
)

# ===== Gemini =====
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "models/gemini-2.0-flash"
)
