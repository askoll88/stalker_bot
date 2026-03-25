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
                "action": {"type": "text", "label": "🩹 Бинт (50₽)", "payload": json.dumps({"cmd": "купить", "item": "bandage"})},
                "color": "positive"
            },
            {
                "action": {"type": "text", "label": "💊 Аптечка (100₽)", "payload": json.dumps({"cmd": "купить", "item": "medkit"})},
                "color": "positive"
            }
        ],
        [
            {
                "action": {"type": "text", "label": "🚑 Мед. аптечка (50₽)", "payload": json.dumps({"cmd": "купить", "item": "medicine_kit"})},
                "color": "positive"
            },
            {
                "action": {"type": "text", "label": "💉 Антирад (200₽)", "payload": json.dumps({"cmd": "купить", "item": "antirad"})},
                "color": "positive"
            }
        ],
        # Ряд 2: Лечение и возврат
        [
            {
                "action": {"type": "text", "label": "⚕️ Лечение (50₽)", "payload": json.dumps({"cmd": "лечение"})},
                "color": "primary"
            }
        ],
        [
            {
                "action": {"type": "text", "label": "🔙 В город", "payload": json.dumps({"cmd": "меню"})},
                "color": "secondary"
            }
        ]
    ]
    return create_keyboard(buttons)


def create_checkpoint_keyboard() -> str:
    """Клавиатура КПП с кнопкой магазина и NPC"""
    buttons = [
        # Ряд 1: Магазин
        [
            {
                "action": {"type": "text", "label": "🛒 МАГАЗИН", "payload": json.dumps({"cmd": "магазин_кпп"})},
                "color": "primary"
            }
        ],
        # Ряд 2: NPC
        [
            {
                "action": {"type": "text", "label": "👨‍🔬 Учёный", "payload": json.dumps({"cmd": "npc", "npc": "scientist"})},
                "color": "default"
            },
            {
                "action": {"type": "text", "label": "💂 Военный", "payload": json.dumps({"cmd": "npc", "npc": "military"})},
                "color": "default"
            },
            {
                "action": {"type": "text", "label": "🧔 Барыга", "payload": json.dumps({"cmd": "npc", "npc": "dealer"})},
                "color": "default"
            }
        ],
        # Ряд 3: Возврат
        [
            {
                "action": {"type": "text", "label": "🔙 В город", "payload": json.dumps({"cmd": "меню"})},
                "color": "secondary"
            }
        ]
    ]
    return create_keyboard(buttons)


def create_checkpoint_shop_keyboard() -> str:
    """Клавиатура магазина на КПП с товарами"""
    buttons = [
        # Ряд 1: Оружие
        [
            {
                "action": {"type": "text", "label": "🔫 ПМ (500₽)", "payload": json.dumps({"cmd": "купить", "item": "pm"})},
                "color": "positive"
            },
            {
                "action": {"type": "text", "label": "🔫 АК-74 (2500₽)", "payload": json.dumps({"cmd": "купить", "item": "ak74"})},
                "color": "positive"
            }
        ],
        [
            {
                "action": {"type": "text", "label": "🔫 MP5 (3000₽)", "payload": json.dumps({"cmd": "купить", "item": "mp5"})},
                "color": "positive"
            },
            {
                "action": {"type": "text", "label": "🔫 СВД (8000₽)", "payload": json.dumps({"cmd": "купить", "item": "svd"})},
                "color": "positive"
            }
        ],
        # Ряд 2: Броня
        [
            {
                "action": {"type": "text", "label": "🦺 Бронежилет (800₽)", "payload": json.dumps({"cmd": "купить", "item": "vest"})},
                "color": "primary"
            },
            {
                "action": {"type": "text", "label": "🧥 Бронекостюм (3000₽)", "payload": json.dumps({"cmd": "купить", "item": "stalker_armor"})},
                "color": "primary"
            }
        ],
        [
            {
                "action": {"type": "text", "label": "🛡️ Военный костюм (7000₽)", "payload": json.dumps({"cmd": "купить", "item": "military_armor"})},
                "color": "primary"
            }
        ],
        # Ряд 3: Энергетики
        [
            {
                "action": {"type": "text", "label": "⚡ Энергетик (30₽)", "payload": json.dumps({"cmd": "купить", "item": "energy_drink"})},
                "color": "positive"
            },
            {
                "action": {"type": "text", "label": "⚡ Бутылка (70₽)", "payload": json.dumps({"cmd": "купить", "item": "energy_bottle"})},
                "color": "positive"
            }
        ],
        # Ряд 4: Аптечки и Антирады
        [
            {
                "action": {"type": "text", "label": "🩹 Бинт (50₽)", "payload": json.dumps({"cmd": "купить", "item": "bandage"})},
                "color": "secondary"
            },
            {
                "action": {"type": "text", "label": "💊 Аптечка (100₽)", "payload": json.dumps({"cmd": "купить", "item": "medkit"})},
                "color": "secondary"
            }
        ],
        [
            {
                "action": {"type": "text", "label": "💉 Антирад (200₽)", "payload": json.dumps({"cmd": "купить", "item": "antirad"})},
                "color": "secondary"
            }
        ],
        # Ряд 5: Назад к КПП
        [
            {
                "action": {"type": "text", "label": "🔙 Назад", "payload": json.dumps({"cmd": "назад_кпп"})},
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
                    "payload": json.dumps({"cmd": "идти", "loc": loc_id})
                },
                "color": "primary"
            }])

    # Всегда добавляем кнопку "Назад в меню"
    buttons.append([
        {
            "action": {"type": "text", "label": "🔙 В город", "payload": json.dumps({"cmd": "меню"})},
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
                "action": {"type": "text", "label": "🏥 Больница", "payload": json.dumps({"cmd": "идти", "loc": "hospital"})},
                "color": "positive"
            },
            {
                "action": {"type": "text", "label": "🛒 Черный рынок", "payload": json.dumps({"cmd": "рынок_закрыт"})},
                "color": "positive"
            },
            {
                "action": {"type": "text", "label": "🚧 КПП", "payload": json.dumps({"cmd": "идти", "loc": "checkpoint"})},
                "color": "positive"
            }
        ],
        # Ряд 2: Статистика и Инвентарь
        [
            {
                "action": {"type": "text", "label": "📊 Статистика", "payload": json.dumps({"cmd": "статистика"})},
                "color": "primary"
            },
            {
                "action": {"type": "text", "label": "🎒 Инвентарь", "payload": json.dumps({"cmd": "инвентарь"})},
                "color": "primary"
            }
        ],
        # Ряд 3: Помощь
        [
            {
                "action": {"type": "text", "label": "❓ Помощь", "payload": json.dumps({"cmd": "помощь"})},
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
