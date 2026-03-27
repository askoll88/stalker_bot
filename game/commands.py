"""Обработка команд бота"""
import json

from game.player import get_player
from game.locations import LOCATIONS, get_available_moves, get_location
from game.keyboards import (
    create_main_keyboard, create_location_keyboard,
    create_hospital_keyboard, create_checkpoint_keyboard,
    create_checkpoint_shop_keyboard,
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

    # Команда /inventory - инвентарь
    if command == "/inventory" or command == "/inv":
        return handle_inventory(player)

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

    if cmd in ("статистика",):
        return player.get_stats_text(), create_main_keyboard()

    if cmd in ("лечение",):
        return handle_heal(player)

    if cmd in ("помощь",):
        return handle_help()

    if cmd in ("инвентарь",):
        return handle_inventory(player)

    if cmd in ("надеть",):
        item_id = payload.get("item", "")
        if item_id:
            return handle_equip(player, item_id)

    if cmd in ("снять",):
        item_type = payload.get("type", "")
        if item_type:
            return handle_unequip(player, item_type)

    if cmd in ("меню",):
        # Возврат в главное меню
        return "🏠 Главное меню\n\nВыбери действие:", create_main_keyboard()

    if cmd in ("рынок_закрыт",):
        return "🛒 Чёрный рынок\n\n🚫 Временно закрыт на реконструкцию.\n\nСкоро здесь появится новый ассортимент товаров!", create_main_keyboard()

    if cmd in ("купить",):
        item_id = payload.get("item", "")
        if item_id:
            return handle_buy(player, item_id)

    if cmd in ("магазин",):
        category = payload.get("category", "")
        if category:
            return handle_shop(player, category)

    if cmd in ("npc",):
        npc_id = payload.get("npc", "")
        if npc_id:
            return handle_npc(player, npc_id)

    if cmd in ("назад_кпп",):
        return "🚧 КПП\n\nТы на контрольно-пропускном пункте.", create_checkpoint_keyboard()

    if cmd in ("магазин_кпп",):
        return "🛒 МАГАЗИН - КПП\n\nВыбери товары:", create_checkpoint_shop_keyboard()

    if cmd in ("идти",):
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
        # Аптечки можно купить в больнице и на КПП
        if player.current_location not in ("hospital", "checkpoint"):
            return "🛒 Покупки доступны только в магазине.", create_main_keyboard()

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

    # Если выбрана категория "all" - показываем все товары
    if category == "all":
        from game.items import ITEMS
        items = list(ITEMS.values())
        text = "🛒 МАГАЗИН - ВСЕ ТОВАРЫ\n\n"
        for i, item in enumerate(items, 1):
            text += f"{i}. {item.name} - {item.price} руб.\n"
        text += "\n💡 Введи номер товара для покупки"

        buttons = [
            [{"action": {"type": "text", "label": "🔙 Назад", "payload": json.dumps({"cmd": "назад_кпп"})}, "color": "secondary"}]
        ]
        return text, create_keyboard(buttons)

    items = get_items_by_type(category)
    if not items:
        return "❓ Нет товаров в этой категории.", create_checkpoint_keyboard()

    # Формируем текст с номерами
    category_names = {
        "weapon": "🔫 ОРУЖИЕ",
        "armor": "🛡️ БРОНЯ",
        "energy": "⚡ ЭНЕРГЕТИКИ",
        "heal": "💊 АПТЕЧКИ",
        "antirad": "☢️ АНТИРАДЫ"
    }

    text = f"{category_names.get(category, category.upper())}\n\n"
    for i, item in enumerate(items, 1):
        text += f"{i}. {item.name} - {item.price} руб.\n"

    text += "\n💡 Введи номер товара для покупки"

    # Только кнопка назад
    buttons = [
        [{"action": {"type": "text", "label": "🔙 Назад", "payload": json.dumps({"cmd": "назад_кпп"})}, "color": "secondary"}]
    ]

    return text, create_keyboard(buttons)


def handle_npc(player, npc_id: str) -> tuple:
    """Взаимодействие с NPC"""
    # Старик - только в городе
    if npc_id == "old_man":
        if player.current_location != "city":
            return "🚫 Старик только в Городе.", create_main_keyboard()

        npc = get_npc(npc_id)
        if not npc:
            return "❓ Такого NPC нет.", create_main_keyboard()

        # Проверяем, получал ли игрок стартовый набор (по наличию нагана)
        from db.database import db
        inventory = db.get_inventory(player.vk_id)
        has_starter = any(item['item_id'] == 'nagan' for item in inventory)

        if has_starter:
            # Уже получал - показываем обычный диалог
            text = f"{npc.name}\n\n{npc.description}\n\n{npc.dialogue['default']}"
            return text, create_location_keyboard(player.current_location, player.shelter_unlocked)
        else:
            # Выдаём стартовый набор
            db.add_item(player.vk_id, "nagan", 1)
            db.add_item(player.vk_id, "leather_jacket", 1)
            db.update_player(player.vk_id, money=player.money + 100)
            player.reload()

            text = f"{npc.name}\n\n{npc.description}\n\n{npc.dialogue['start']}"
            keyboard = create_location_keyboard(player.current_location, player.shelter_unlocked)
            return text, keyboard

    # Остальные NPC - только на КПП
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


def handle_inventory(player) -> tuple:
    """Показать инвентарь игрока"""
    from db.database import db
    import json

    inventory = db.get_inventory(player.vk_id)
    equipped = db.get_equipped_items(player.vk_id)

    if not inventory:
        return "🎒 Инвентарь пуст!\n\nКупи оружие и броню в магазине на КПП.", create_main_keyboard()

    text = "🎒 ИНВЕНТАРЬ\n\n"

    # Экипировка
    text += player.get_equipped_text()
    text += "\n"

    # Оружие в инвентаре
    weapons = [item for item in inventory if item['type'] == 'weapon']
    if weapons:
        text += "🔫 ОРУЖИЕ В РЮКЗАКЕ:\n"
        for i, item in enumerate(weapons, 1):
            is_equipped = item['is_equipped']
            stats = item.get('stats')
            if stats:
                if isinstance(stats, str):
                    stats = json.loads(stats)
                damage = stats.get('damage', 0)
            else:
                damage = 0
            equip_status = " (надето)" if is_equipped else ""
            text += f"  {i}. {item['name']} (урон: {damage}){equip_status}\n"
        text += "\n"

    # Броня в инвентаре
    armors = [item for item in inventory if item['type'] == 'armor']
    if armors:
        text += "🛡️ БРОНЯ В РЮКЗАКЕ:\n"
        for i, item in enumerate(armors, 1):
            is_equipped = item['is_equipped']
            stats = item.get('stats')
            if stats:
                if isinstance(stats, str):
                    stats = json.loads(stats)
                defense = stats.get('defense', 0)
            else:
                defense = 0
            equip_status = " (надето)" if is_equipped else ""
            text += f"  {i}. {item['name']} (защита: {defense}){equip_status}\n"
        text += "\n"

    # Расходники
    consumables = [item for item in inventory if item['type'] in ('heal', 'energy', 'food', 'antirad')]
    if consumables:
        text += "💊 РАСХОДНИКИ:\n"
        for item in consumables:
            count = item['count']
            text += f"  • {item['name']} x{count}\n"

    text += "\n💡 Нажми на предмет, чтобы надеть/снять"

    # Создаём кнопки для экипировки
    buttons = []

    # Кнопки для оружия
    if weapons:
        weapon_buttons = []
        for item in weapons:
            is_equipped = item['is_equipped']
            label = f"🔫 {item['name']}"
            if is_equipped:
                label = f"❌ {label}"
            weapon_buttons.append({
                "action": {"type": "text", "label": label, "payload": json.dumps({"cmd": "надеть" if not is_equipped else "снять", "item": item['item_id'], "type": "weapon" if is_equipped else ""})},
                "color": "positive" if not is_equipped else "secondary"
            })
        buttons.append(weapon_buttons)

    # Кнопки для брони
    if armors:
        armor_buttons = []
        for item in armors:
            is_equipped = item['is_equipped']
            label = f"🛡️ {item['name']}"
            if is_equipped:
                label = f"❌ {label}"
            armor_buttons.append({
                "action": {"type": "text", "label": label, "payload": json.dumps({"cmd": "надеть" if not is_equipped else "снять", "item": item['item_id'], "type": "armor" if is_equipped else ""})},
                "color": "positive" if not is_equipped else "secondary"
            })
        buttons.append(armor_buttons)

    # Кнопка назад
    buttons.append([
        {"action": {"type": "text", "label": "🔙 Назад", "payload": json.dumps({"cmd": "меню"})}, "color": "secondary"}
    ])

    keyboard = create_keyboard(buttons)
    return text, keyboard


def handle_equip(player, item_id: str) -> tuple:
    """Экипировать предмет"""
    from db.database import db

    success, message = db.equip_item(player.vk_id, item_id)
    player.reload()

    if success:
        return f"✅ {message}\n\n{player.get_equipped_text()}", create_main_keyboard()
    else:
        return f"❌ {message}", create_main_keyboard()


def handle_unequip(player, item_type: str) -> tuple:
    """Снять экипированный предмет"""
    from db.database import db

    success, message = db.unequip_item(player.vk_id, item_type)
    player.reload()

    if success:
        return f"✅ {message}\n\n{player.get_equipped_text()}", create_main_keyboard()
    else:
        return f"❌ {message}", create_main_keyboard()


