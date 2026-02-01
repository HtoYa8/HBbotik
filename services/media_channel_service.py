import json
import os
import re
from typing import Set

MEDIA_CHANNEL_FILE = "data/media_channel.json"

MEDIA_EXTENSIONS = (
    ".png", ".jpg", ".jpeg", ".gif",
    ".mp4", ".mov", ".webm"
)

# ---------- Работа с каналами ----------

def get_media_channels() -> Set[int]:
    """Получить все media-каналы"""
    if not os.path.exists(MEDIA_CHANNEL_FILE):
        return set()

    try:
        with open(MEDIA_CHANNEL_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return set(data.get("media_channels", []))
    except (json.JSONDecodeError, IOError):
        return set()

def save_media_channels(channels: Set[int]):
    os.makedirs("data", exist_ok=True)
    with open(MEDIA_CHANNEL_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {"media_channels": list(channels)},
            f,
            indent=2
        )

def add_media_channel(channel_id: int):
    channels = get_media_channels()
    channels.add(channel_id)
    save_media_channels(channels)

def remove_media_channel(channel_id: int):
    channels = get_media_channels()
    channels.discard(channel_id)
    save_media_channels(channels)

# ---------- Проверка медиа ----------

def is_media_attachment(message) -> bool:
    """Проверить, есть ли в сообщении фото или видео"""
    if not message.attachments:
        return False

    for attachment in message.attachments:
        filename = attachment.filename.lower()
        if filename.endswith(MEDIA_EXTENSIONS):
            return True

    return False

def has_media_or_link(message) -> bool:
    """Проверить, содержит ли сообщение медиа или ссылку"""
    if is_media_attachment(message):
        return True

    url_pattern = r'https?://[^\s]+'
    return bool(re.search(url_pattern, message.content))

def extract_text_without_links(text: str) -> str:
    """Удалить ссылки из текста"""
    url_pattern = r'https?://[^\s]+'
    return re.sub(url_pattern, '', text).strip()
