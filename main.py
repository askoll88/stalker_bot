import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import random
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    VK_TOKEN, GROUP_ID, FATIGUE_PER_ACTION, EXP_TO_LEVEL,
    HEAL_COST, MAX_FATIGUE, MINI_APP_URL, VK_APP_ID
)
from db.database import db
from game.locations import (
    get_location_description,
    get_available_moves,
    format_locations_list,
    get_location
)


def create_main_keyboard(shelter_unlocked=False):
    """Главная клавиатура"""
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("📊 Статистика", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("🎒 Инвентарь", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("🏥 Больница", color=VkKeyboardColor.SECONDARY)
    keyboard.add_button("🛒 Черный рынок", color=VkKeyboardColor.SECONDARY)
    keyboard.add_button("🚧 КПП", color=VkKeyboardColor.SECONDARY)
    keyboard.add_line()
    if shelter_unlocked:
        keyboard.add_button("🔓 Убежище", color=VkKeyboardColor.POSITIVE)
    else:
        keyboard.add_button("🔒 Убежище", color=VkKeyboardColor.NEGATIVE)
    return keyboard


def create_location_keyboard(current_location, shelter_unlocked=False):
    """Клавиатура перемещения"""
    keyboard = VkKeyboard(one_time=False)
    available = get_available_moves(current_location, shelter_unlocked)
    for i, loc_id in enumerate(available):
        loc = get_location(loc_id)
        if loc:
            color = VkKeyboardColor.PRIMARY
            if loc_id == "hospital":
                color = VkKeyboardColor.SECONDARY
            elif loc_id == "market":
                color = VkKeyboardColor.SECONDARY
            elif loc_id == "shelter":
                color = VkKeyboardColor.POSITIVE
            keyboard.add_button(loc.name, color=color)
            if (i + 1) % 2 == 0 and i < len(available) - 1:
                keyboard.add_line()
    keyboard.add_line()
    keyboard.add_button("🔙 В город", color=VkKeyboardColor.NEGATIVE)
    return keyboard


def create_hospital_keyboard():
    """Клавиатура больницы"""
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("💊 Лечение (50₽)", color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button("🔙 В город", color=VkKeyboardColor.NEGATIVE)
    return keyboard


def create_market_keyboard():
    """Клавиатура рынка (временно пустая)"""
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("🔙 В город", color=VkKeyboardColor.NEGATIVE)
    return keyboard


def create_shelter_keyboard():
    """Клавиатура убежища"""
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("😴 Отдохнуть", color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button("🔙 В город", color=VkKeyboardColor.NEGATIVE)
    return keyboard


def create_checkpoint_keyboard():
    """Клавиатура КПП с магазином"""
    keyboard = VkKeyboard(one_time=False)
    # Ряд 1: Кнопка Магазин с payload
    keyboard.add_button("🛒 МАГАЗИН", color=VkKeyboardColor.PRIMARY,
                       payload=json.dumps({"cmd": "магазин_кпп"}))
    keyboard.add_line()
    # Ряд 2: NPC
    keyboard.add_button("👨‍🔬 Учёный", color=VkKeyboardColor.SECONDARY,
                       payload=json.dumps({"cmd": "npc", "npc": "scientist"}))
    keyboard.add_button("💂 Военный", color=VkKeyboardColor.SECONDARY,
                       payload=json.dumps({"cmd": "npc", "npc": "military"}))
    keyboard.add_button("🧔 Барыга", color=VkKeyboardColor.SECONDARY,
                       payload=json.dumps({"cmd": "npc", "npc": "dealer"}))
    keyboard.add_line()
    # Ряд 3: Возврат
    keyboard.add_button("🔙 В город", color=VkKeyboardColor.NEGATIVE,
                       payload=json.dumps({"cmd": "меню"}))
    return keyboard


def create_checkpoint_shop_keyboard():
    """Главное меню магазина на КПП - выбор категорий"""
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("🔫 Оружие", color=VkKeyboardColor.POSITIVE,
                       payload=json.dumps({"cmd": "категория", "cat": "weapon"}))
    keyboard.add_button("🛡️ Броня", color=VkKeyboardColor.PRIMARY,
                       payload=json.dumps({"cmd": "категория", "cat": "armor"}))
    keyboard.add_line()
    keyboard.add_button("⚡ Энергетики", color=VkKeyboardColor.POSITIVE,
                       payload=json.dumps({"cmd": "категория", "cat": "energy"}))
    keyboard.add_button("💊 Аптечки", color=VkKeyboardColor.SECONDARY,
                       payload=json.dumps({"cmd": "категория", "cat": "medkit"}))
    keyboard.add_line()
    keyboard.add_button("💉 Антирады", color=VkKeyboardColor.SECONDARY,
                       payload=json.dumps({"cmd": "категория", "cat": "antirad"}))
    keyboard.add_line()
    keyboard.add_button("🔙 Назад", color=VkKeyboardColor.NEGATIVE,
                       payload=json.dumps({"cmd": "назад_кпп"}))
    return keyboard


def create_shop_weapon_keyboard():
    """Клавиатура оружия в магазине"""
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("🔫 ПМ (500₽)", color=VkKeyboardColor.POSITIVE,
                       payload=json.dumps({"cmd": "купить", "item": "pm"}))
    keyboard.add_button("🔫 АК-74 (2500₽)", color=VkKeyboardColor.POSITIVE,
                       payload=json.dumps({"cmd": "купить", "item": "ak74"}))
    keyboard.add_line()
    keyboard.add_button("🔫 MP5 (3000₽)", color=VkKeyboardColor.POSITIVE,
                       payload=json.dumps({"cmd": "купить", "item": "mp5"}))
    keyboard.add_button("🔫 СВД (8000₽)", color=VkKeyboardColor.POSITIVE,
                       payload=json.dumps({"cmd": "купить", "item": "svd"}))
    keyboard.add_line()
    keyboard.add_button("🔙 Назад", color=VkKeyboardColor.NEGATIVE,
                       payload=json.dumps({"cmd": "магазин_кпп"}))
    return keyboard


def create_shop_armor_keyboard():
    """Клавиатура брони в магазине"""
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("🦺 Бронежилет (800₽)", color=VkKeyboardColor.PRIMARY,
                       payload=json.dumps({"cmd": "купить", "item": "vest"}))
    keyboard.add_button("🧥 Сталкер (3000₽)", color=VkKeyboardColor.PRIMARY,
                       payload=json.dumps({"cmd": "купить", "item": "stalker_armor"}))
    keyboard.add_line()
    keyboard.add_button("🛡️ Военный (7000₽)", color=VkKeyboardColor.PRIMARY,
                       payload=json.dumps({"cmd": "купить", "item": "military_armor"}))
    keyboard.add_line()
    keyboard.add_button("🔙 Назад", color=VkKeyboardColor.NEGATIVE,
                       payload=json.dumps({"cmd": "магазин_кпп"}))
    return keyboard


def create_shop_energy_keyboard():
    """Клавиатура энергетиков в магазине"""
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("⚡ Энергетик (30₽)", color=VkKeyboardColor.POSITIVE,
                       payload=json.dumps({"cmd": "купить", "item": "energy_drink"}))
    keyboard.add_button("⚡ Бутылка (70₽)", color=VkKeyboardColor.POSITIVE,
                       payload=json.dumps({"cmd": "купить", "item": "energy_bottle"}))
    keyboard.add_line()
    keyboard.add_button("🔙 Назад", color=VkKeyboardColor.NEGATIVE,
                       payload=json.dumps({"cmd": "магазин_кпп"}))
    return keyboard


def create_shop_medkit_keyboard():
    """Клавиатура аптечек в магазине"""
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("🩹 Бинт (50₽)", color=VkKeyboardColor.SECONDARY,
                       payload=json.dumps({"cmd": "купить", "item": "bandage"}))
    keyboard.add_button("💊 Аптечка (100₽)", color=VkKeyboardColor.SECONDARY,
                       payload=json.dumps({"cmd": "купить", "item": "medkit"}))
    keyboard.add_line()
    keyboard.add_button("🔙 Назад", color=VkKeyboardColor.NEGATIVE,
                       payload=json.dumps({"cmd": "магазин_кпп"}))
    return keyboard


def create_shop_antirad_keyboard():
    """Клавиатура антирадов в магазине"""
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("💉 Антирад (200₽)", color=VkKeyboardColor.SECONDARY,
                       payload=json.dumps({"cmd": "купить", "item": "antirad"}))
    keyboard.add_line()
    keyboard.add_button("🔙 Назад", color=VkKeyboardColor.NEGATIVE,
                       payload=json.dumps({"cmd": "магазин_кпп"}))
    return keyboard


def get_stats_message(player):
    """Получить сообщение со статистикой"""
    exp_needed = EXP_TO_LEVEL * player['level']
    exp_progress = player['exp'] % exp_needed
    bar_length = 10
    filled = int(exp_progress / exp_needed * bar_length)
    bar = "█" * filled + "░" * (bar_length - filled)
    return f"""📊 СТАТИСТИКА

👤 Имя: {player['name']}
⬆️ Уровень: {player['level']} [{bar}]

❤️ Здоровье: {player['health']}/100
⚔️ Атака: {player['attack']}
🔋 Усталость: {player['fatigue']}/{MAX_FATIGUE}

💰 Деньги: {player['money']} руб.

📍 Локация: {get_location(player['current_location']).name if get_location(player['current_location']) else 'Неизвестно'}

📈 Опыт: {exp_progress}/{exp_needed}
🔐 Убежище: {'Открыто' if player['shelter_unlocked'] else 'Закрыто'}"""


def send_message(vk, user_id, message, keyboard=None):
    """Отправить сообщение"""
    kwargs = {"user_id": user_id, "message": message, "random_id": random.randint(0, 2**31)}
    if keyboard:
        # Принимает как объект клавиатуры, так и готовую строку
        if hasattr(keyboard, 'get_keyboard'):
            kwargs["keyboard"] = keyboard.get_keyboard()
        else:
            kwargs["keyboard"] = keyboard
    vk.messages.send(**kwargs)


def handle_player_action(vk, user_id, action):
    """Обработать действие игрока"""
    player = db.get_player(user_id)
    if not player:
        send_message(vk, user_id, "Ты не зарегистрирован. Напиши /start")
        return

    if player['health'] <= 0:
        send_message(vk, user_id, "Ты погиб! Иди в больницу.",
                    keyboard=create_main_keyboard(player['shelter_unlocked']).get_keyboard())
        return

    if action == "статистика":
        msg = get_stats_message(player)
        vk.messages.send(user_id=user_id, message=msg,
                        keyboard=create_main_keyboard(player['shelter_unlocked']).get_keyboard(),
                        random_id=random.randint(0, 2**31))

    elif action == "инвентарь":
        message = "🎒 ИНВЕНТАРЬ\nНажми кнопку ниже чтобы открыть:"
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_open_app_button(VK_APP_ID, "ОТКРЫТЬ ИНВЕНТАРЬ", VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button("Назад", color=VkKeyboardColor.NEGATIVE)
        vk.messages.send(user_id=user_id, message=message,
                        keyboard=keyboard.get_keyboard(),
                        random_id=random.randint(0, 2**31))

    elif action == "локация":
        loc_desc = get_location_description(player['current_location'], player['shelter_unlocked'])
        available = get_available_moves(player['current_location'], player['shelter_unlocked'])
        msg = f"{loc_desc}\n\n📍 Куда идти:\n\n{format_locations_list(available)}"
        vk.messages.send(user_id=user_id, message=msg,
                        keyboard=create_location_keyboard(player['current_location'], player['shelter_unlocked']).get_keyboard(),
                        random_id=random.randint(0, 2**31))

    elif action == "больница":
        move_to_location(vk, user_id, "hospital")
    elif action == "рынок":
        move_to_location(vk, user_id, "market")
    elif action == "убежище":
        move_to_location(vk, user_id, "shelter")
    elif action == "кпп":
        move_to_location(vk, user_id, "checkpoint")
    elif action == "назад":
        move_to_location(vk, user_id, "city")
    elif action == "лечение":
        handle_heal(vk, user_id, player)
    elif action == "отдых":
        handle_rest(vk, user_id, player)
    elif action == "бой":
        handle_attack(vk, user_id, player)
    elif action == "купить_оружие":
        handle_buy_item(vk, user_id, player, "ak74", 500)
    elif action == "купить_аптечку":
        handle_buy_item(vk, user_id, player, "medkit", 50)
    elif action == "купить_еду":
        handle_buy_item(vk, user_id, player, "bread", 20)
    elif action == "купить_патроны":
        handle_buy_item(vk, user_id, player, "ammo_5x45", 30)
    elif action == "купить_броню":
        handle_buy_item(vk, user_id, player, "vest", 800)


def handle_heal(vk, user_id, player):
    """Обработка лечения"""
    if player['current_location'] != "hospital":
        send_message(vk, user_id, "Лечиться можно только в больнице!")
        return
    if player['health'] >= 100:
        send_message(vk, user_id, "Ты полностью здоров!",
                    keyboard=create_hospital_keyboard().get_keyboard())
        return
    if player['money'] >= HEAL_COST:
        new_health = min(100, player['health'] + 50)
        new_money = player['money'] - HEAL_COST
        db.update_player(user_id, health=new_health, money=new_money)
        send_message(vk, user_id, f"Ты вылечился! +50 здоровья. Потрачено: {HEAL_COST} руб.",
                    keyboard=create_hospital_keyboard().get_keyboard())
    else:
        send_message(vk, user_id, f"Не хватает денег! Нужно {HEAL_COST} руб.",
                    keyboard=create_hospital_keyboard().get_keyboard())


def handle_rest(vk, user_id, player):
    """Обработка отдыха"""
    if player['current_location'] != "shelter":
        send_message(vk, user_id, "Отдыхать можно только в убежище!")
        return
    if player['fatigue'] == 0:
        send_message(vk, user_id, "Ты полон сил!",
                    keyboard=create_shelter_keyboard().get_keyboard())
        return
    new_fatigue = max(0, player['fatigue'] - 50)
    db.update_player(user_id, fatigue=new_fatigue)
    send_message(vk, user_id, f"Ты отдохнул! Усталость: {player['fatigue']} → {new_fatigue}",
                keyboard=create_shelter_keyboard().get_keyboard())


def handle_attack(vk, user_id, player):
    """Обработка боя"""
    if player['fatigue'] >= MAX_FATIGUE:
        send_message(vk, user_id, "Ты слишком устал! Отдохни перед боем.",
                    keyboard=create_main_keyboard(player['shelter_unlocked']).get_keyboard())
        return

    monsters = [
        {"name": "Собака-мутант", "health": 30, "damage": 10, "exp": 20, "money": 15},
        {"name": "Кровосос", "health": 50, "damage": 20, "exp": 40, "money": 30},
        {"name": "Бюрер", "health": 80, "damage": 30, "exp": 70, "money": 50},
    ]

    monster = random.choice(monsters)
    player_damage = player['attack'] + random.randint(-5, 10)
    monster_damage = monster['damage'] + random.randint(-3, 5)

    monster['health'] -= player_damage
    player['health'] -= monster_damage

    if monster['health'] <= 0:
        exp_gain = monster['exp']
        money_gain = monster['money']
        new_exp = player['exp'] + exp_gain
        new_money = player['money'] + money_gain
        new_fatigue = player['fatigue'] + 20

        level_up = False
        new_level = player['level']
        exp_needed = EXP_TO_LEVEL * player['level']

        if new_exp >= exp_needed:
            new_level += 1
            new_exp -= exp_needed
            level_up = True

        db.update_player(user_id, exp=new_exp, money=new_money, fatigue=new_fatigue,
                        level=new_level, health=max(0, player['health']))

        msg = f"⚔️ БОЙ С {monster['name']}\n\nТы нанёс {player_damage} урона!\nВраг нанёс {monster_damage} урона!\n\nПОБЕДА! +{exp_gain} опыта +{money_gain} руб."
        if level_up:
            msg += f"\n\n⬆️ УРОВЕНЬ UP! Теперь уровень {new_level}!"
        send_message(vk, user_id, msg,
                    keyboard=create_main_keyboard(player['shelter_unlocked']).get_keyboard())
    else:
        new_fatigue = player['fatigue'] + 20
        db.update_player(user_id, health=max(0, player['health']), fatigue=new_fatigue)
        msg = f"⚔️ БОЙ С {monster['name']}\n\nТы нанёс {player_damage} урона!\nВраг нанёс {monster_damage} урона!\n\nПОРАЖЕНИЕ"
        send_message(vk, user_id, msg,
                    keyboard=create_main_keyboard(player['shelter_unlocked']).get_keyboard())


def handle_buy_item(vk, user_id, player, item_id, price):
    """Обработка покупки предмета"""
    if player['current_location'] != "market":
        send_message(vk, user_id, "Покупать можно только на Черном рынке!",
                    keyboard=create_market_keyboard())
        return
    if player['money'] < price:
        send_message(vk, user_id, f"Не хватает денег! Нужно {price} руб.",
                    keyboard=create_market_keyboard())
        return
    success = db.add_item(user_id, item_id, 1)
    if success:
        db.update_player(user_id, money=player['money'] - price)
        item = db.get_item(item_id)
        send_message(vk, user_id, f"Куплено: {item['name']}. Потрачено: {price} руб.",
                    keyboard=create_market_keyboard())
    else:
        send_message(vk, user_id, "Не удалось купить предмет!",
                    keyboard=create_market_keyboard())


def move_to_location(vk, user_id, location_id):
    """Переместиться в локацию"""
    player = db.get_player(user_id)
    if not player:
        return

    if location_id == "shelter" and not player['shelter_unlocked']:
        send_message(vk, user_id, "Убежище заперто.")
        return

    current_loc = get_location(player['current_location'])
    if location_id not in current_loc.connected_locations:
        send_message(vk, user_id, "Туда нельзя попасть отсюда!")
        return

    if player['fatigue'] >= MAX_FATIGUE:
        send_message(vk, user_id, "Ты слишком устал!",
                    keyboard=create_main_keyboard(player['shelter_unlocked']).get_keyboard())
        return

    new_fatigue = player['fatigue'] + FATIGUE_PER_ACTION
    db.update_player(user_id, current_location=location_id, fatigue=new_fatigue)

    player = db.get_player(user_id)
    loc_desc = get_location_description(location_id, player['shelter_unlocked'])

    keyboard = None
    if location_id == "city":
        keyboard = create_main_keyboard(player['shelter_unlocked'])
    elif location_id == "hospital":
        keyboard = create_hospital_keyboard()
    elif location_id == "market":
        keyboard = create_market_keyboard()
    elif location_id == "shelter":
        keyboard = create_shelter_keyboard()
    elif location_id == "checkpoint":
        keyboard = create_checkpoint_keyboard()
    else:
        keyboard = create_location_keyboard(location_id, player['shelter_unlocked'])

    msg = f"{loc_desc}\n\n🔋 Усталость: {new_fatigue}/{MAX_FATIGUE}"
    vk.messages.send(user_id=user_id, message=msg,
                    keyboard=keyboard.get_keyboard(),
                    random_id=random.randint(0, 2**31))


def main():
    print("Запуск S.T.A.L.K.E.R. бота...")

    vk_session = vk_api.VkApi(token=VK_TOKEN)
    vk = vk_session.get_api()
    longpoll = VkBotLongPoll(vk_session, GROUP_ID)

    print("Бот S.T.A.L.K.E.R. запущен!")

    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            user_id = event.obj.message['from_id']
            text = event.obj.message.get('text', '').strip().lower()
            payload = event.obj.message.get('payload', '')

            # Обработка payload из кнопок
            if payload:
                try:
                    import json
                    payload_data = json.loads(payload)
                    cmd = payload_data.get('cmd', '')
                    item = payload_data.get('item', '')
                    loc = payload_data.get('loc', '')
                    npc = payload_data.get('npc', '')

                    player = db.get_player(user_id)

                    if cmd == "магазин_кпп":
                        send_message(vk, user_id, "🛒 МАГАЗИН - КПП\n\nВыбери категорию:",
                                    keyboard=create_checkpoint_shop_keyboard())
                        continue
                    elif cmd == "категория":
                        cat = payload_data.get('cat', '')
                        if cat == "weapon":
                            send_message(vk, user_id, "🔫 ОРУЖИЕ\n\nВыбери товар:",
                                        keyboard=create_shop_weapon_keyboard())
                        elif cat == "armor":
                            send_message(vk, user_id, "🛡️ БРОНЯ\n\nВыбери товар:",
                                        keyboard=create_shop_armor_keyboard())
                        elif cat == "energy":
                            send_message(vk, user_id, "⚡ ЭНЕРГЕТИКИ\n\nВыбери товар:",
                                        keyboard=create_shop_energy_keyboard())
                        elif cat == "medkit":
                            send_message(vk, user_id, "💊 АПТЕЧКИ\n\nВыбери товар:",
                                        keyboard=create_shop_medkit_keyboard())
                        elif cat == "antirad":
                            send_message(vk, user_id, "💉 АНТИРАДЫ\n\nВыбери товар:",
                                        keyboard=create_shop_antirad_keyboard())
                        continue
                    elif cmd == "назад_кпп":
                        send_message(vk, user_id, "🚧 КПП\n\nТы на контрольно-пропускном пункте.",
                                    keyboard=create_checkpoint_keyboard())
                        continue
                    elif cmd == "купить" and item:
                        handle_player_action(vk, user_id, f"купить_{item}")
                        continue
                    elif cmd == "идти" and loc:
                        move_to_location(vk, user_id, loc)
                        continue
                    elif cmd == "npc" and npc:
                        handle_player_action(vk, user_id, f"npc_{npc}")
                        continue
                    elif cmd == "меню":
                        player = db.get_player(user_id)
                        send_message(vk, user_id, "🏠 Главное меню\n\nВыбери действие:",
                                    keyboard=create_main_keyboard(player['shelter_unlocked']).get_keyboard())
                        continue
                    elif cmd == "рынок_закрыт":
                        player = db.get_player(user_id)
                        send_message(vk, user_id, "🛒 Чёрный рынок\n\n🚫 Временно закрыт на реконструкцию.\n\nСкоро здесь появится новый ассортимент товаров!",
                                    keyboard=create_main_keyboard(player['shelter_unlocked']).get_keyboard())
                        continue
                except (json.JSONDecodeError, KeyError):
                    pass

            try:
                user_info = vk.users.get(user_ids=user_id)[0]
                user_name = f"{user_info['first_name']} {user_info['last_name']}"
            except:
                user_name = "Stalker"

            if text == '/start' or text == 'start' or text == 'начать':
                if not db.player_exists(user_id):
                    db.create_player(user_id, user_name)
                    welcome_msg = "🌍 ДОБРО ПОЖАЛОВАТЬ В ЗОНУ, СТАЛКЕР!\n\nТы прибыл в заброшенный город. Твоё приключение начинается здесь.\n\nТы находишься в Городе.\nУбежище заперто — найди способ попасть внутрь.\n\nИспользуй кнопки для навигации!"
                    vk.messages.send(user_id=user_id, message=welcome_msg,
                                    keyboard=create_main_keyboard(False).get_keyboard(),
                                    random_id=random.randint(0, 2**31))
                else:
                    player = db.get_player(user_id)
                    vk.messages.send(user_id=user_id,
                                    message=f"С возвращением, сталкер {player['name']}! Ты в: {get_location(player['current_location']).name}",
                                    keyboard=create_main_keyboard(player['shelter_unlocked']).get_keyboard(),
                                    random_id=random.randint(0, 2**31))

            elif text == "локация":
                handle_player_action(vk, user_id, "локация")
            elif text == "статистика":
                handle_player_action(vk, user_id, "статистика")
            elif text == "инвентарь":
                handle_player_action(vk, user_id, "инвентарь")
            elif text == "бой":
                handle_player_action(vk, user_id, "бой")
            elif "больница" in text:
                handle_player_action(vk, user_id, "больница")
            elif "рынок" in text:
                player = db.get_player(user_id)
                send_message(vk, user_id, "🛒 Чёрный рынок\n\n🚫 Временно закрыт на реконструкцию.\n\nСкоро здесь появится новый ассортимент товаров!",
                           keyboard=create_main_keyboard(player['shelter_unlocked']).get_keyboard())
            elif "кпп" in text:
                handle_player_action(vk, user_id, "кпп")
            elif "убежище" in text:
                handle_player_action(vk, user_id, "убежище")
            elif "лечение" in text or "лечиться" in text:
                handle_player_action(vk, user_id, "лечение")
            elif "отдохнуть" in text or "отдых" in text:
                handle_player_action(vk, user_id, "отдых")
            elif "назад" in text or "в город" in text:
                handle_player_action(vk, user_id, "назад")
            elif "оружие" in text:
                handle_player_action(vk, user_id, "купить_оружие")
            elif "аптечка" in text:
                handle_player_action(vk, user_id, "купить_аптечку")
            elif "еда" in text or "хлеб" in text:
                handle_player_action(vk, user_id, "купить_еду")
            elif "патрон" in text:
                handle_player_action(vk, user_id, "купить_патроны")
            elif text == '/help' or text == 'помощь':
                help_msg = "📋 КОМАНДЫ:\n/start - Начать игру\n/статистика - Твоя статистика\n/инвентарь - Открыть инвентарь"
                vk.messages.send(user_id=user_id, message=help_msg,
                                random_id=random.randint(0, 2**31))


if __name__ == '__main__':
    main()
