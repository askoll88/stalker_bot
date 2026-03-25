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


LOCATIONS = {
    "city": Location(
        name="🏙️ Город",
        description="Заброшенный город-призрак. Руины зданий, ржавые машины...",
        connected_locations=["hospital", "market", "shelter"],
    ),
    "hospital": Location(
        name="🏥 Больница",
        description="Полуразрушенная больница. Внутри можно найти медикаменты и лечение.",
        connected_locations=["city"],
    ),
    "market": Location(
        name="🛒 Черный рынок",
        description="Подпольный рынок сталкеров. Здесь можно купить и продать вещи.",
        connected_locations=["city"],
    ),
    "shelter": Location(
        name="🔒 Убежище",
        description="Тайное убежище сталкеров. Пока закрыто для тебя.",
        connected_locations=["city"],
        shelter_unlocked=True,
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
