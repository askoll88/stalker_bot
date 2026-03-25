"""Обработка команд бота"""
import json

from game.player import get_player
from game.locations import LOCATIONS, get_available_moves, get_location
from game.keyboards import (
    create_main_keyboard, create_location_keyboard,
    create_hospital_keyboard, create_checkpoint_keyboard,
    get_payload, create_keyboard
)
from game.items import ITEMS, get_item, get_items_by_type
from game.npc import NPCS, get_npc
from config import INITIAL_HEALTH, HEAL_COST, MAX_FATIGUE, FATIGUE_PER_ACTION


def handle_command(vk_id: int, command: str, name: str = None, payload: dict = None) -> tuple:
    """Обработать команду игрока. Возвращает (текст, клавиатура)"""
    # Если есть payload из кнопки - обрабатываем его
    if payload:
        return handle_payload(vk_id, payload, name)

    command = command.strip().lower()
    player = get_player(vk_id, name)

    # Команда /start - начало игры
    if command == "/start":
        return handle_start(player)

    # Команда /help - помощь
    if command == "/help":
        return handle_help()

    # Команда /stats - статистика
    if command == "/stats":
        return player.get_stats_text(), create_main_keyboard()

    # Команда /go [локация] - перемещение
    if command.startswith("/go "):
        location_key = command[4:].strip()
        return handle_go(player, location_key)

    # Команда /heal - лечение
    if command == "/heal":
        return handle_heal(player)

    # Команда /unlock - открыть убежище (для тестирования)
    if command == "/unlock":
        player.unlock_shelter()
        return "🔓 Убежище открыто! Теперь ты можешь попасть внутрь.", create_main_keyboard()

    # Обработка цифр для быстрой покупки (если игрок в магазине)
    if command.isdigit() and player.current_location == "checkpoint":
        category = player.shop_category
        if not category:
            return "💡 Сначала выбери категорию товаров в магазине.", create_checkpoint_keyboard()

        items = get_items_by_type(category)
        num = int(command)

        if 1 <= num <= len(items):
            item = items[num - 1]
            return handle_buy(player, item.id)
        else:
            return f"❓ Товара под номером {num} нет. Выбери от 1 до {len(items)}.", create_checkpoint_keyboard()

    # Неизвестная команда
    return "❓ Неизвестная команда. Напиши /help для списка команд.", create_main_keyboard()


def handle_payload(vk_id: int, payload: dict, name: str = None) -> tuple:
    """Обработать нажатие кнопки"""
    cmd = payload.get("command", payload.get("cmd", ""))
    player = get_player(vk_id, name)

    if cmd in ("stats",):
        return player.get_stats_text(), create_main_keyboard()

    if cmd in ("heal",):
        return handle_heal(player)

    if cmd in ("help",):
        return handle_help()

    if cmd in ("inventory",):
        return "🎒 Инвентарь\n\nПусто! Посети Чёрный рынок для покупки снаряжения.", create_main_keyboard()

    if cmd in ("menu",):
        # Возврат в главное меню
        return "🏠 Главное меню\n\nВыбери действие:", create_main_keyboard()

    if cmd in ("buy", "buy_num"):
        item_id = payload.get("item", "")
        if item_id:
            return handle_buy(player, item_id)

    if cmd in ("shop",):
        category = payload.get("category", "")
        if category:
            return handle_shop(player, category)

    if cmd in ("npc",):
        npc_id = payload.get("npc", "")
        if npc_id:
            return handle_npc(player, npc_id)

    if cmd in ("back_to_checkpoint",):
        return "🚧 КПП\n\nТы на контрольно-пропускном пункте.", create_checkpoint_keyboard()

    if cmd in ("go",):
        loc = payload.get("loc", "")
        if loc:
            return handle_go(player, loc)

    return "❓ Неизвестное действие", create_main_keyboard()


def handle_start(player) -> tuple:
    """Обработать начало игры"""
    text = f"""🚪 ДОБРО ПОЖАЛОВАТЬ В ЗОНУ, СТАЛКЕР!

Ты очнулся на окраине заброшенного города. Голова гудит, в кармане только ржавый ПМ и немного денег.

Твоё убежище заперто. Нужно найти способ попасть внутрь...

📍 Ты находишься в: Город

Используй кнопки внизу для навигации!"""
    return text, create_main_keyboard()


def handle_help() -> tuple:
    """Показать помощь"""
    text = """📖 КОМАНДЫ:

/start - Начать игру
/stats - Твоя статистика
/loc - Текущая локация
/go [название] - Перейти в локацию
/heal - Лечение в больнице (50 руб.)
/help - Эта справка

🏙️ ЛОКАЦИИ:
• city - Город (хаб)
• hospital - Больница
• market - Черный рынок
• shelter - Убежище (требуется ключ)

⚠️ Следи за усталостью!"""
    return text, create_main_keyboard()


def handle_go(player, location_key: str) -> tuple:
    """Обработать перемещение"""
    # Нормализация названия локации
    location_map = {
        "город": "city",
        "city": "city",
        "больница": "hospital",
        "hospital": "hospital",
        "рынок": "market",
        "market": "market",
        "черный рынок": "market",
        "убежище": "shelter",
        "shelter": "shelter",
        "кпп": "checkpoint",
        "checkpoint": "checkpoint",
    }

    target = location_map.get(location_key.lower())
    if not target:
        return "❓ Неизвестная локация. Нажми кнопку 'Локации' для выбора.", create_location_keyboard(
            player.current_location, player.shelter_unlocked
        )

    # Проверка доступности локации
    available = get_available_moves(player.current_location, player.shelter_unlocked)
    
    if target not in available:
        return "🚫 Ты не можешь туда попасть. Выбери доступную локацию.", create_location_keyboard(
            player.current_location, player.shelter_unlocked
        )

    # Проверка усталости (только если локация не имеет флага no_fatigue)
    target_loc = get_location(target)
    if target_loc and not target_loc.no_fatigue:
        if player.fatigue >= MAX_FATIGUE:
            return "😴 Ты слишком устал! Отдохни в убежище или больнице.", create_location_keyboard(
                player.current_location, player.shelter_unlocked
            )

    # Перемещение
    if player.change_location(target):
        loc_name = LOCATIONS[target].name

        # Если локация с no_fatigue - добавим сообщение
        if target_loc and target_loc.no_fatigue:
            text = f"🚶 Ты пошёл в {loc_name} (без затрат энергии)\n\n{player.get_location_text()}"
        else:
            text = f"🚶 Ты пошёл в {loc_name}\n\n{player.get_location_text()}"

        # Для больницы - своя клавиатура с покупками
        if target == "hospital":
            keyboard = create_hospital_keyboard()
        # Для КПП - магазин и NPC
        elif target == "checkpoint":
            keyboard = create_checkpoint_keyboard()
        else:
            keyboard = create_location_keyboard(target, player.shelter_unlocked)

        return text, keyboard

    return "❌ Не удалось переместиться.", create_location_keyboard(
        player.current_location, player.shelter_unlocked
    )


def handle_buy(player, item_id: str) -> tuple:
    """Обработать покупку предмета"""
    if player.current_location not in ("hospital", "checkpoint"):
        return "🛒 Покупки доступны только в магазине.", create_main_keyboard()

    item = get_item(item_id)
    if not item:
        return "❓ Такого предмета нет.", create_checkpoint_keyboard() if player.current_location == "checkpoint" else create_hospital_keyboard()

    if player.money < item.price:
        return f"💸 Не хватает денег! {item.name} стоит {item.price} руб.\n💰 У тебя: {player.money} руб.", create_checkpoint_keyboard() if player.current_location == "checkpoint" else create_hospital_keyboard()

    # Покупаем предмет
    from db.database import db

    if item.type == "heal":
        if player.health >= INITIAL_HEALTH:
            return "❤️ У тебя полное здоровье!", create_checkpoint_keyboard() if player.current_location == "checkpoint" else create_hospital_keyboard()

        new_health = min(player.health + item.value, INITIAL_HEALTH)
        healed = new_health - player.health
        db.update_player(player.vk_id, money=player.money - item.price, health=new_health)
        player.reload()

        return f"✅ Куплено: {item.name}!\n❤️ Лечит: +{healed} HP\n💰 Потрачено: {item.price} руб.", create_checkpoint_keyboard() if player.current_location == "checkpoint" else create_hospital_keyboard()

    elif item.type == "antirad":
        return f"✅ Куплено: {item.name}!\n💰 Потрачено: {item.price} руб.\n\n⚠️ Радиация пока не активна.", create_checkpoint_keyboard() if player.current_location == "checkpoint" else create_hospital_keyboard()

    elif item.type == "weapon":
        db.update_player(player.vk_id, money=player.money - item.price)
        player.reload()
        return f"✅ Куплено: {item.name}!\n⚔️ Урон: {item.value}\n💰 Потрачено: {item.price} руб.\n\nДобавлено в инвентарь!", create_checkpoint_keyboard()

    elif item.type == "armor":
        db.update_player(player.vk_id, money=player.money - item.price)
        player.reload()
        return f"✅ Куплено: {item.name}!\n🛡️ Защита: {item.value}\n💰 Потрачено: {item.price} руб.\n\nНадето!", create_checkpoint_keyboard()

    elif item.type == "energy":
        if player.fatigue <= 0:
            return "⚡ Ты полон сил!", create_checkpoint_keyboard()

        new_fatigue = max(player.fatigue - item.value, 0)
        restored = player.fatigue - new_fatigue
        db.update_player(player.vk_id, money=player.money - item.price, fatigue=new_fatigue)
        player.reload()

        return f"✅ Куплено: {item.name}!\n⚡ Энергия: +{restored}\n💰 Потрачено: {item.price} руб.", create_checkpoint_keyboard()

    return "❓ Неизвестный тип предмета.", create_checkpoint_keyboard() if player.current_location == "checkpoint" else create_hospital_keyboard()


def handle_shop(player, category: str) -> tuple:
    """Показать товары определённой категории"""
    if player.current_location != "checkpoint":
        return "🛒 Магазин только на КПП.", create_main_keyboard()

    # Сохраняем текущую категорию
    from db.database import db
    db.update_player(player.vk_id, shop_category=category)
    player.shop_category = category

    items = get_items_by_type(category)
    if not items:
        return "❓ Нет товаров в этой категории.", create_checkpoint_keyboard()

    # Формируем текст с номерами
    category_names = {
        "weapon": "🔫 ОРУЖИЕ",
        "armor": "🛡️ БРОНЯ",
        "energy": "⚡ ЭНЕРГЕТИКИ",
        "heal": "💊 АПТЕЧКИ"
    }

    text = f"{category_names.get(category, category.upper())}\n\n"
    for i, item in enumerate(items, 1):
        text += f"{i}. {item.name} - {item.price} руб.\n"

    text += "\n💡 Введи номер товара для покупки"

    # Только кнопка назад
    buttons = [
        [{"action": {"type": "text", "label": "🔙 Назад", "payload": json.dumps({"cmd": "back_to_checkpoint"})}, "color": "secondary"}]
    ]

    return text, create_keyboard(buttons)


def handle_npc(player, npc_id: str) -> tuple:
    """Взаимодействие с NPC"""
    if player.current_location != "checkpoint":
        return "🚫 NPC только на КПП.", create_main_keyboard()

    npc = get_npc(npc_id)
    if not npc:
        return "❓ Такого NPC нет.", create_checkpoint_keyboard()

    text = f"{npc.name}\n\n{npc.description}\n\n{npc.dialogue['default']}"
    return text, create_checkpoint_keyboard()


def handle_heal(player) -> tuple:
    """Обработать лечение"""
    if player.current_location != "hospital":
        return "🏥 Лечение доступно только в больнице.", create_main_keyboard()

    if player.health >= INITIAL_HEALTH:
        return "❤️ Твоё здоровье уже полное!", create_hospital_keyboard()

    if player.money < HEAL_COST:
        return f"💸 Не хватает денег. Лечение стоит {HEAL_COST} руб.", create_hospital_keyboard()

    # Лечим
    from db.database import db
    db.update_player(player.vk_id,
        health=INITIAL_HEALTH,
        money=player.money - HEAL_COST
    )
    player.reload()

    return f"✅ Ты полностью исцелён!\n💰 Потрачено: {HEAL_COST} руб.\n❤️ Здоровье: {player.health}/{INITIAL_HEALTH}", create_hospital_keyboard()

