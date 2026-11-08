# monitor.py — YouTube kanallarni kuzatish
import logging
import threading
import time
from typing import Callable, Dict

import feedparser
import yt_dlp

from config import CHECK_INTERVAL
from database import get_channels, get_last_video_map, set_last_video
from gemini_ai import summarize

logger = logging.getLogger(__name__)

# Kanal metadatasini kesh qilish (URL → {channel_id, uploader})
_meta_cache: Dict[str, Dict] = {}


def resolve_channel(url: str) -> Dict[str, str]:
    """YouTube URL dan channel_id va uploader nomini oladi."""
    if url in _meta_cache:
        return _meta_cache[url]
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "extract_flat": "in_playlist",
        "playlistend": 1,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        meta = {
            "channel_id": info.get("channel_id") or info.get("id", ""),
            "uploader": (
                info.get("uploader")
                or info.get("channel")
                or info.get("title", "YouTube")
            ),
        }
    _meta_cache[url] = meta
    return meta


def get_latest_video(channel_id: str):
    """RSS feed orqali eng yangi video ma'lumotlarini qaytaradi."""
    feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    parsed = feedparser.parse(feed_url)
    if not parsed.entries:
        raise ValueError(f"Feed bo'sh: {channel_id}")
    entry = parsed.entries[0]
    return (
        entry.get("yt_videoid", ""),
        entry.get("title", ""),
        entry.get("summary", ""),
    )


def _monitor_loop(callback: Callable):
    last_seen = get_last_video_map()
    logger.info("Monitor sikli boshlandi.")

    while True:
        for url in get_channels():
            try:
                meta = resolve_channel(url)
            except Exception as exc:
                logger.warning(f"Kanal aniqlanmadi ({url}): {exc}")
                continue

            cid = meta["channel_id"]
            if not cid:
                continue

            try:
                video_id, title, description = get_latest_video(cid)
            except Exception as exc:
                logger.warning(f"Feed xatosi ({cid}): {exc}")
                continue

            if last_seen.get(cid) != video_id:
                logger.info(f"Yangi video: {title}")
                summary = summarize(title, description)
                callback({
                    "owner_name": meta["uploader"],
                    "title": title,
                    "summary": summary,
                    "url": f"https://youtu.be/{video_id}",
                })
                last_seen[cid] = video_id
                set_last_video(cid, video_id)

        time.sleep(CHECK_INTERVAL)


def start_monitor(callback: Callable) -> threading.Thread:
    """Background threadda monitorni ishga tushiradi."""
    t = threading.Thread(target=_monitor_loop, args=(callback,), daemon=True)
    t.start()
    return t
