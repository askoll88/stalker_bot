"""Работа с медиафайлами (изображениями) для бота"""
import os
import requests
from typing import Optional
from vk_api import VkApi

# Импортируем БД
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.database import db


# Папка для хранения изображений (как резервная копия)
MEDIA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "media")
IMAGES_DIR = os.path.join(MEDIA_DIR, "images")
os.makedirs(IMAGES_DIR, exist_ok=True)


def get_image(type_: str, id_: str) -> Optional[str]:
    """Получить photo_id для изображения из БД

    Returns:
        str: photo_id для attachment (photo123_456) или None
    """
    try:
        media = db.get_media(type_, id_)
        if media and media.get('photo_id'):
            print(f"📷 Загружено изображение: {type_}/{id_} -> {media['photo_id']}")
            return media['photo_id']
        print(f"📷 Нет изображения: {type_}/{id_}")
    except Exception as e:
        print(f"❌ Ошибка загрузки изображения {type_}/{id_}: {e}")
    return None


def get_attachment(type_: str, id_: str) -> Optional[str]:
    """Получить строку вложения для VK

    Returns:
        str: "photo{owner_id}_{photo_id}" или None
    """
    photo_id = get_image(type_, id_)
    if photo_id:
        result = f"photo{photo_id}"
        print(f"📷 get_attachment({type_}, {id_}) -> {result}")
        return result
    print(f"📷 get_attachment({type_}, {id_}) -> None")
    return None


def set_image(type_: str, id_: str, photo_id: str, image_data: bytes = None) -> bool:
    """Сохранить изображение в БД

    Args:
        type_: 'location' или 'npc'
        id_: id объекта
        photo_id: VK photo_id
        image_data: бинарные данные (опционально)

    Returns:
        bool: успех сохранения
    """
    return db.set_media(type_, id_, photo_id, image_data)


def get_image_path(type_: str, id_: str) -> str:
    """Получить путь к файлу изображения (для резервного копирования)"""
    return os.path.join(IMAGES_DIR, f"{type_}_{id_}.jpg")


def upload_photo_to_vk(vk_session, photo_path: str) -> Optional[str]:
    """Загрузить фото на сервер VK и вернуть photo_id для attachment
    
    Returns:
        str: photo_id в формате {owner_id}_{photo_id} или None при ошибке
    """
    try:
        vk = vk_session.get_api()
        
        # Получаем URL сервера загрузки
        upload_url = vk.photos.getMessagesUploadServer()['upload_url']
        
        # Загружаем файл
        with open(photo_path, 'rb') as f:
            files = {'photo': f}
            response = requests.post(upload_url, files=files)
        
        if response.status_code != 200:
            print(f"Ошибка загрузки: {response.status_code}")
            return None
        
        upload_data = response.json()
        
        # Сохраняем фото
        saved_photo = vk.photos.saveMessagesPhoto(
            server=upload_data['server'],
            photo=upload_data['photo'],
            hash=upload_data['hash']
        )[0]
        
        # Формируем photo_id для attachment
        photo_id = f"{saved_photo['owner_id']}_{saved_photo['id']}"
        return photo_id
        
    except Exception as e:
        print(f"Ошибка загрузки фото: {e}")
        return None


def save_uploaded_photo(photo_data: bytes, type_: str, id_: str) -> bool:
    """Сохранить загруженное фото локально (резервная копия)

    Args:
        photo_data: байты изображения
        type_: тип (location/npc)
        id_: id локации или NPC
        
    Returns:
        bool: успех сохранения
    """
    try:
        path = get_image_path(type_, id_)
        with open(path, 'wb') as f:
            f.write(photo_data)
        return True
    except Exception as e:
        print(f"Ошибка сохранения фото: {e}")
        return False


def get_image_bytes(type_: str, id_: str) -> Optional[bytes]:
    """Получить байты изображения из файла"""
    try:
        path = get_image_path(type_, id_)
        if os.path.exists(path):
            with open(path, 'rb') as f:
                return f.read()
    except Exception as e:
        print(f"Ошибка чтения фото: {e}")
    return None


def load_all_media_to_cache():
    """Загрузить все изображения из БД в кэш (для обратной совместимости)

    Returns:
        dict: словарь {('location'/'npc', id): photo_id}
    """
    all_media = db.get_all_media()
    cache = {}
    for media in all_media:
        key = (media['type'], media['object_id'])
        if media['photo_id']:
            cache[key] = media['photo_id']
    return cache


def list_available_images() -> list:
    """Список доступных изображений"""
    all_media = db.get_all_media()
    result = []

    # Известные объекты
    known = {
        'location': ['city', 'hospital', 'market', 'shelter', 'checkpoint'],
        'npc': ['old_man', 'scientist', 'military', 'dealer']
    }

    for type_ in ['location', 'npc']:
        for id_ in known.get(type_, []):
            # Ищем в БД
            media = next((m for m in all_media if m['type'] == type_ and m['object_id'] == id_), None)
            if media and media.get('photo_id'):
                result.append(f"✅ {type_}/{id_}")
            else:
                result.append(f"❌ {type_}/{id_}")

    return result
