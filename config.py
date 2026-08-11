import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

HF_TOKEN = os.getenv("HF_TOKEN")
HF_MODEL = os.getenv(
    "HF_MODEL",
    "openai/gpt-oss-120b:cheapest",
)

# Optional avatar image URL or local path for Streamlit chat avatars.
# If unset, the app will fall back to an emoji.
AVATAR_URL = os.getenv("AVATAR_URL", "") or None

if not HF_TOKEN:
    raise RuntimeError(
        "HF_TOKEN is missing. Add it to the .env file."
    )