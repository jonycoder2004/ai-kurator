# database.py — JSON orqali ma'lumotlarni saqlash
import json
from typing import Dict, List, Set

from config import CHANNELS_FILE, LAST_VIDEO_FILE, SUBSCRIBERS_FILE

# ── Default kanallar (birinchi ishga tushganda) ──
DEFAULT_CHANNELS = [
    "https://www.youtube.com/@iamAImaster",
    "https://www.youtube.com/@AzizbekBahodirov_CEO",
    "https://www.youtube.com/@%D0%9D%D0%B5%D0%B9%D1%80%D0%BE%D0%B1%D0%B0%D1%82%D1%8F",
    "https://www.youtube.com/@xondamir_ai",
]


def _read(path, default):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return default
    return default


def _write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# ── Kanallar ──

def get_channels() -> List[str]:
    data = _read(CHANNELS_FILE, None)
    if data is None:
        _write(CHANNELS_FILE, DEFAULT_CHANNELS)
        return DEFAULT_CHANNELS
    return data


def set_channels(channels: List[str]) -> None:
    _write(CHANNELS_FILE, channels)


def add_channel(url: str) -> bool:
    chans = get_channels()
    if url in chans:
        return False
    chans.append(url)
    set_channels(chans)
    return True


def remove_channel(url: str) -> bool:
    chans = get_channels()
    if url not in chans:
        return False
    chans.remove(url)
    set_channels(chans)
    return True


# ── Oxirgi video ──

def get_last_video_map() -> Dict[str, str]:
    return _read(LAST_VIDEO_FILE, {})


def set_last_video(channel_id: str, video_id: str) -> None:
    data = get_last_video_map()
    data[channel_id] = video_id
    _write(LAST_VIDEO_FILE, data)


# ── Obunachlar ──

def get_subscribers() -> Set[int]:
    return set(_read(SUBSCRIBERS_FILE, []))


def add_subscriber(uid: int) -> bool:
    subs = get_subscribers()
    if uid in subs:
        return False
    subs.add(uid)
    _write(SUBSCRIBERS_FILE, list(subs))
    return True


def remove_subscriber(uid: int) -> bool:
    subs = get_subscribers()
    if uid not in subs:
        return False
    subs.discard(uid)
    _write(SUBSCRIBERS_FILE, list(subs))
    return True
