import random
import google.generativeai as genai
from openai import OpenAI

from config import (
    OPENROUTER_KEYS,
    OPENROUTER_MODEL,
    GEMINI_API_KEY,
    GEMINI_MODEL
)

# ---------- GEMINI SETUP ----------
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# ---------- OPENROUTER HELPERS ----------
def _openrouter_clients():
    clients = []
    for key in OPENROUTER_KEYS or []:
        clients.append(
            OpenAI(
                api_key=key,
                base_url="https://openrouter.ai/api/v1"
            )
        )
    random.shuffle(clients)
    return clients

def _try_openrouter(prompt, max_tokens):
    for client in _openrouter_clients():
        try:
            res = client.chat.completions.create(
                model=OPENROUTER_MODEL,
                messages=[
                    {"role": "system", "content": "You are a YouTube Shorts copywriter."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=max_tokens
            )
            txt = res.choices[0].message.content
            if txt:
                return txt
        except Exception:
            continue
    return ""

def _try_gemini(prompt):
    if not GEMINI_API_KEY:
        return ""
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        return model.generate_content(prompt).text or ""
    except Exception:
        return ""

# ---------- MAIN ROUTER ----------
def generate_text(prompt, provider="openrouter", max_tokens=500):
    # Priority logic:
    # - If user chose gemini → try gemini first, then openrouter
    # - Else (openrouter) → try all openrouter keys, then gemini

    if provider == "gemini":
        out = _try_gemini(prompt)
        if out:
            return out
        return _try_openrouter(prompt, max_tokens)

    # default: openrouter
    out = _try_openrouter(prompt, max_tokens)
    if out:
        return out

    # final fallback
    return _try_gemini(prompt) or ""
