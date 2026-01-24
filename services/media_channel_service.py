import json
import os
import re

MEDIA_CHANNEL_FILE = "data/media_channel.json"

def get_media_channel_id() -> int | None:
    if not os.path.exists(MEDIA_CHANNEL_FILE):
        return None
    
    try:
        with open(MEDIA_CHANNEL_FILE, 'r') as f:
            data = json.load(f)
            return data.get("channel_id")
    except (json.JSONDecodeError, IOError):
        return None

def set_media_channel(channel_id: int):
    os.makedirs("data", exist_ok=True)
    with open(MEDIA_CHANNEL_FILE, 'w') as f:
        json.dump({"channel_id": channel_id}, f)

def is_media_attachment(message) -> bool:
    if not message.attachments:
        return False
    
    for attachment in message.attachments:
        if attachment.content_type and (
            attachment.content_type.startswith('image/') or
            attachment.content_type.startswith('video/') or
            attachment.content_type.startswith('audio/')
        ):
            return True
    
    return False

def has_media_or_link(message) -> bool:
    """Проверить, содержит ли сообщение медиа или ссылку"""
    # Проверяем медиа-файлы
    if is_media_attachment(message):
        return True
    
    # Проверяем ссылки в тексте
    url_pattern = r'https?://[^\s]+'
    if re.search(url_pattern, message.content):
        return True
    
    return False

def extract_text_without_links(text: str) -> str:
    """Отделить текст от ссылок"""
    url_pattern = r'https?://[^\s]+'
    # Удаляем ссылки и лишние пробелы
    text_without_links = re.sub(url_pattern, '', text).strip()
    return text_without_links
