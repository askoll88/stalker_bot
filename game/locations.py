"""Локации игры S.T.A.L.K.E.R."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Location:
    name: str
    description: str
    connected_locations: list[str]
    required_level: int = 1
    shelter_unlocked: bool = False
    image_id: Optional[str] = None  # photo_id для VK вложения


LOCATIONS = {
    "city": Location(
        name="🏙️ Город",
        description="Заброшенный город-призрак. Руины зданий, ржавые машины, тишина...\n\n👴 Здесь живёт старожил — Старик. Может рассказать о городе и помочь с экипировкой.",
        connected_locations=["hospital", "shelter", "checkpoint"],
    ),
    "hospital": Location(
        name="🏥 Больница",
        description="Полуразрушенная больница. Здесь можно найти медикаменты и лечение.",
        connected_locations=["city"],
    ),
    "market": Location(
        name="🛒 Черный рынок",
        description="🚫 Временно закрыт на реконструкцию.\n\nСкоро здесь появится новый ассортимент товаров!",
        connected_locations=["city"],
    ),
    "shelter": Location(
        name="🔒 Убежище",
        description="Тайное убежище сталкеров. Пока закрыто для тебя.",
        connected_locations=["city"],
        shelter_unlocked=True,
    ),
    "checkpoint": Location(
        name="🚧 КПП",
        description="Контрольно-пропускной пункт. Военные давно покинули эти места, но здесь обосновался торговец.\n\n🛒 МАГАЗИН:\n• 🔫 Оружие (ПМ, АК-74, MP5, СВД)\n• 🛡️ Броня (Бронежилет, Сталкер, Военный)\n• ⚡ Энергетики\n• 💊 Аптечки и бинты\n• ☢️ Антирады",
        connected_locations=["city"],
    ),
}


def get_location(location_id: str) -> Optional[Location]:
    return LOCATIONS.get(location_id)


def get_location_description(location_id: str, shelter_unlocked: bool = False) -> str:
    loc = get_location(location_id)
    if not loc:
        return "Неизвестная локация"

    if location_id == "shelter" and not shelter_unlocked:
        return "🔒 Убежище\n\nТы стоишь перед массивной металлической дверью. Она заперта.\nНужно найти способ попасть внутрь..."

    return f"{loc.name}\n\n{loc.description}"


def get_available_moves(current_location: str, shelter_unlocked: bool = False) -> list[str]:
    loc = get_location(current_location)
    if not loc:
        return []

    available = []
    for loc_id in loc.connected_locations:
        if loc_id == "shelter" and not shelter_unlocked:
            continue
        available.append(loc_id)

    return available


def format_locations_list(locations: list[str]) -> str:
    if not locations:
        return "Некуда идти"

    result = []
    for loc_id in locations:
        loc = get_location(loc_id)
        if loc:
            result.append(f"• {loc.name}")

    return "\n".join(result)


def load_images_from_db():
    """Загрузить изображения локаций из БД"""
    from db.database import db
    from game.media import get_image

    for loc_id in LOCATIONS:
        photo_id = get_image('location', loc_id)
        if photo_id:
            LOCATIONS[loc_id].image_id = photo_id
            print(f"✅ Загружено изображение для {loc_id}: {photo_id}")

