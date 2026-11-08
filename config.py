# config.py — Barcha sozlamalar
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

load_dotenv(BASE_DIR / ".env")

BOT_TOKEN    = os.getenv("BOT_TOKEN", "")
ADMIN_ID     = int(os.getenv("ADMIN_ID", "0"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

CHANNELS_FILE   = DATA_DIR / "channels.json"
LAST_VIDEO_FILE = DATA_DIR / "last_video.json"
SUBSCRIBERS_FILE = DATA_DIR / "subscribers.json"

CHECK_INTERVAL = 300  # 5 daqiqa
