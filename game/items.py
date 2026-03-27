"""Предметы в игре"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Item:
    id: str
    name: str
    description: str
    price: int
    type: str  # "heal", "antirad", "weapon", "armor", "energy", "other"
    value: int  # Количество HP для лечения или снижения радиации, или урона/защиты


# Словарь всех предметов
ITEMS = {
    # Больница
    "bandage": Item(
        id="bandage",
        name="🩹 Бинт",
        description="Простой бинт для перевязки ран.",
        price=50,
        type="heal",
        value=30
    ),
    "medkit": Item(
        id="medkit",
        name="💊 Аптечка",
        description="Полная аптечка с лекарствами.",
        price=100,
        type="heal",
        value=60
    ),
    "medicine_kit": Item(
        id="medicine_kit",
        name="🚑 Мед. аптечка",
        description="Полная медицинская аптечка. Восстанавливает 100 HP.",
        price=50,
        type="heal",
        value=100
    ),
    "antirad": Item(
        id="antirad",
        name="💉 Антирад",
        description="Препарат для выведения радиации.",
        price=200,
        type="antirad",
        value=50
    ),

    # Оружие (КПП)
    "pm": Item(
        id="pm",
        name="🔫 ПМ",
        description="Пистолет Макарова. Надёжный, но слабый.",
        price=500,
        type="weapon",
        value=15  # Урон
    ),
    "ak74": Item(
        id="ak74",
        name="🔫 АК-74",
        description="Автомат Калашникова. Надёжная штурмовая винтовка.",
        price=2500,
        type="weapon",
        value=40
    ),
    "mp5": Item(
        id="mp5",
        name="🔫 MP5",
        description="Немецкий пистолет-пулемёт. Точный и быстрый.",
        price=3000,
        type="weapon",
        value=35
    ),
    "svd": Item(
        id="svd",
        name="🔫 СВД",
        description="Снайперская винтовка Драгунова. Точный снайперский инструмент.",
        price=8000,
        type="weapon",
        value=80
    ),

    # Броня (КПП)
    "vest": Item(
        id="vest",
        name="🦺 Бронежилет",
        description="Простой бронежилет. Защищает от лёгкого оружия.",
        price=800,
        type="armor",
        value=20  # Защита
    ),
    "stalker_armor": Item(
        id="stalker_armor",
        name="🧥 Бронекостюм сталкера",
        description="Самодельный костюм сталкера. Хорошая защита.",
        price=3000,
        type="armor",
        value=50
    ),
    "military_armor": Item(
        id="military_armor",
        name="🛡️ Военный бронекостюм",
        description="Армейский бронекостюм. Отличная защита.",
        price=7000,
        type="armor",
        value=80
    ),

    # Энергетики (КПП)
    "energy_drink": Item(
        id="energy_drink",
        name="⚡ Энергетик",
        description="Энергетический напиток. Восстанавливает 20 энергии.",
        price=30,
        type="energy",
        value=20
    ),
    "energy_bottle": Item(
        id="energy_bottle",
        name="⚡ Бутылка энергетика",
        description="Большая бутылка. Восстанавливает 50 энергии.",
        price=70,
        type="energy",
        value=50
    ),

    # Стартовые предметы (выдаёт Старик)
    "nagan": Item(
        id="nagan",
        name="🔫 Наган",
        description="Старый револьвер. Надёжный, но слабый.",
        price=0,
        type="weapon",
        value=5  # Урон
    ),
    "leather_jacket": Item(
        id="leather_jacket",
        name="🧥 Кожаная куртка",
        description="Потрёпанная кожаная куртка. Лёгкая защита.",
        price=0,
        type="armor",
        value=10  # Защита
    ),
}


def get_item(item_id: str) -> Optional[Item]:
    """Получить предмет по ID"""
    return ITEMS.get(item_id)


def get_items_by_type(item_type: str) -> list[Item]:
    """Получить все предметы определённого типа"""
    return [item for item in ITEMS.values() if item.type == item_type]


def get_shop_items(location: str) -> list[Item]:
    """Получить предметы для магазина определённой локации"""
    if location == "hospital":
        return [ITEMS["bandage"], ITEMS["medkit"], ITEMS["antirad"]]
    elif location == "checkpoint":
        # Оружие + броня + энергетики + аптечки
        return [
            ITEMS["pm"], ITEMS["ak74"], ITEMS["mp5"], ITEMS["svd"],
            ITEMS["vest"], ITEMS["stalker_armor"], ITEMS["military_armor"],
            ITEMS["energy_drink"], ITEMS["energy_bottle"],
            ITEMS["bandage"], ITEMS["medkit"]
        ]
    return []


def format_shop_items(items: list[Item]) -> str:
    """Форматировать список предметов для магазина"""
    if not items:
        return "Нет предметов в продаже"

    result = []
    for item in items:
        result.append(f"{item.name} - {item.price} руб.\n   {item.description}")

    return "\n\n".join(result)
