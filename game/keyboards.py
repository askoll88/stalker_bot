"""Клавиатуры для VK бота"""
import json
from typing import Optional
from vk_api.bot_longpoll import VkBotMessageEvent
from vk_api.bot_longpoll import VkBotMessageEvent

from game.locations import get_available_moves, get_location


def create_keyboard(buttons: list[list[dict]], one_time: bool = False) -> str:
    """Создать клавиатуру из списка кнопок"""
    keyboard = {
        "one_time": one_time,
        "buttons": buttons
    }
    return json.dumps(keyboard, ensure_ascii=False)


def create_hospital_keyboard() -> str:
    """Клавиатура больницы с предметами"""
    buttons = [
        # Ряд 1: Купить предметы
        [
            {
                "action": {"type": "text", "label": "🩹 Бинт (50₽)", "payload": json.dumps({"cmd": "buy", "item": "bandage"})},
                "color": "positive"
            },
            {
                "action": {"type": "text", "label": "💊 Аптечка (100₽)", "payload": json.dumps({"cmd": "buy", "item": "medkit"})},
                "color": "positive"
            }
        ],
        [
            {
                "action": {"type": "text", "label": "💉 Антирад (200₽)", "payload": json.dumps({"cmd": "buy", "item": "antirad"})},
                "color": "positive"
            }
        ],
        # Ряд 2: Лечение и возврат
        [
            {
                "action": {"type": "text", "label": "⚕️ Лечение (50₽)", "payload": json.dumps({"cmd": "heal"})},
                "color": "primary"
            }
        ],
        [
            {
                "action": {"type": "text", "label": "🔙 Главное меню", "payload": json.dumps({"cmd": "menu"})},
                "color": "secondary"
            }
        ]
    ]
    return create_keyboard(buttons)


def create_checkpoint_keyboard() -> str:
    """Клавиатура КПП с магазином и NPC"""
    buttons = [
        # Ряд 1: Магазин
        [
            {
                "action": {"type": "text", "label": "🔫 Оружие", "payload": json.dumps({"cmd": "shop", "category": "weapon"})},
                "color": "primary"
            },
            {
                "action": {"type": "text", "label": "🛡️ Броня", "payload": json.dumps({"cmd": "shop", "category": "armor"})},
                "color": "primary"
            }
        ],
        [
            {
                "action": {"type": "text", "label": "⚡ Энергетики", "payload": json.dumps({"cmd": "shop", "category": "energy"})},
                "color": "positive"
            },
            {
                "action": {"type": "text", "label": "💊 Аптечки", "payload": json.dumps({"cmd": "shop", "category": "heal"})},
                "color": "positive"
            }
        ],
        # Ряд 2: NPC
        [
            {
                "action": {"type": "text", "label": "👨‍🔬 Учёный", "payload": json.dumps({"cmd": "npc", "npc": "scientist"})},
                "color": "secondary"
            },
            {
                "action": {"type": "text", "label": "💂 Военный", "payload": json.dumps({"cmd": "npc", "npc": "military"})},
                "color": "secondary"
            },
            {
                "action": {"type": "text", "label": "🧔 Барыга", "payload": json.dumps({"cmd": "npc", "npc": "dealer"})},
                "color": "secondary"
            }
        ],
        # Ряд 3: Возврат
        [
            {
                "action": {"type": "text", "label": "🔙 Главное меню", "payload": json.dumps({"cmd": "menu"})},
                "color": "secondary"
            }
        ]
    ]
    return create_keyboard(buttons)


def create_location_keyboard(current_location: str, shelter_unlocked: bool = False) -> str:
    """Создать клавиатуру перемещения по локациям"""
    available_moves = get_available_moves(current_location, shelter_unlocked)

    # Фильтруем - убираем больницу и рынок (они теперь на главном экране)
    available_moves = [loc for loc in available_moves if loc not in ("hospital", "market")]

    if not available_moves:
        return create_main_keyboard()

    buttons = []
    for loc_id in available_moves:
        loc = get_location(loc_id)
        if loc:
            # Эмодзи + название локации
            label = loc.name.split()[0] + " " + loc.name.split()[1] if len(loc.name.split()) > 1 else loc.name
            buttons.append([{
                "action": {
                    "type": "text",
                    "label": label,
                    "payload": json.dumps({"cmd": "go", "loc": loc_id})
                },
                "color": "primary"
            }])

    # Всегда добавляем кнопку "Назад в меню"
    buttons.append([
        {
            "action": {"type": "text", "label": "🔙 Главное меню", "payload": json.dumps({"cmd": "menu"})},
            "color": "secondary"
        }
    ])

    return create_keyboard(buttons)


def create_main_keyboard() -> str:
    """Главное меню - основные команды"""
    buttons = [
        # Ряд 1: Больница, Рынок и КПП
        [
            {
                "action": {"type": "text", "label": "🏥 Больница", "payload": json.dumps({"cmd": "go", "loc": "hospital"})},
                "color": "positive"
            },
            {
                "action": {"type": "text", "label": "🛒 Рынок", "payload": json.dumps({"cmd": "go", "loc": "market"})},
                "color": "positive"
            },
            {
                "action": {"type": "text", "label": "🚧 КПП", "payload": json.dumps({"cmd": "go", "loc": "checkpoint"})},
                "color": "positive"
            }
        ],
        # Ряд 2: Статистика и Инвентарь
        [
            {
                "action": {"type": "text", "label": "📊 Статистика", "payload": json.dumps({"cmd": "stats"})},
                "color": "primary"
            },
            {
                "action": {"type": "text", "label": "🎒 Инвентарь", "payload": json.dumps({"cmd": "inventory"})},
                "color": "primary"
            }
        ],
        # Ряд 3: Помощь
        [
            {
                "action": {"type": "text", "label": "❓ Помощь", "payload": json.dumps({"cmd": "help"})},
                "color": "secondary"
            }
        ]
    ]
    return create_keyboard(buttons)


def create_empty_keyboard() -> str:
    """Пустая клавиатура (скрыть кнопки)"""
    return json.dumps({"one_time": True, "buttons": []}, ensure_ascii=False)


def get_payload(event: VkBotMessageEvent) -> Optional[dict]:
    """Получить payload из события VK"""
    try:
        return json.loads(event.obj.message.get("payload", "{}"))
    except (json.JSONDecodeError, TypeError):
        return None


def get_payload_from_message(message: dict) -> Optional[dict]:
    """Получить payload из словаря сообщения (event.obj.message)"""
    try:
        payload_str = message.get("payload", "")
        if payload_str:
            return json.loads(payload_str)
    except (json.JSONDecodeError, TypeError):
        pass
    return None

