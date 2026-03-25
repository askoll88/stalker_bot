"""Бот S.T.A.L.K.E.R. для ВК"""
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.ui_sdk import open_app_vk
import random
import sys
import os
import json

# Добавляем пути для импортов
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

# URL Mini App (из config.py)


def create_main_keyboard(shelter_unlocked: bool = False) -> VkKeyboard:
    """Главная клавиатура с кнопками"""
    keyboard = VkKeyboard(one_time=False)
    
    keyboard.add_button("📍 Локация", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("📊 Статистика", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("🎒 Инвентарь", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("⚔️ Атаковать", color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button("🏥 Больница", color=VkKeyboardColor.SECONDARY)
    keyboard.add_button("🛒 Черный рынок", color=VkKeyboardColor.SECONDARY)
    keyboard.add_line()
    
    if shelter_unlocked:
        keyboard.add_button("🔓 Убежище", color=VkKeyboardColor.POSITIVE)
    else:
        keyboard.add_button("🔒 Убежище", color=VkKeyboardColor.NEGATIVE)
    
    return keyboard


def create_location_keyboard(current_location: str, shelter_unlocked: bool = False) -> VkKeyboard:
    """Клавиатура для выбора локации"""
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
            
            keyboard.add_button(loc.name.split()[0] + " " + loc.name.split()[1] if len(loc.name.split()) > 1 else loc.name, color=color)
            
            if (i + 1) % 2 == 0 and i < len(available) - 1:
                keyboard.add_line()
    
    keyboard.add_line()
    keyboard.add_button("🔙 В город", color=VkKeyboardColor.NEGATIVE)

    return keyboard


def create_hospital_keyboard() -> VkKeyboard:
    """Клавиатура больницы"""
    keyboard = VkKeyboard(one_time=False)

    keyboard.add_button("💊 Лечение (50 руб)", color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button("🔙 В город", color=VkKeyboardColor.NEGATIVE)

    return keyboard


def create_market_keyboard() -> VkKeyboard:
    """Клавиатура черного рынка"""
    keyboard = VkKeyboard(one_time=False)

    keyboard.add_button("🔫 Оружие", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("🩹 Аптечки", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("🍞 Еда", color=VkKeyboardColor.SECONDARY)
    keyboard.add_button("📦 Патроны", color=VkKeyboardColor.SECONDARY)
    keyboard.add_line()
    keyboard.add_button("🔙 В город", color=VkKeyboardColor.NEGATIVE)

    return keyboard


def create_shelter_keyboard() -> VkKeyboard:
    """Клавиатура убежища"""
    keyboard = VkKeyboard(one_time=False)

    keyboard.add_button("🛏️ Отдохнуть", color=VkKeyboardColor.POSITIVE)
    keyboard.add_button("📦 Инвентарь", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("🔙 В город", color=VkKeyboardColor.NEGATIVE)

    return keyboard


def get_stats_message(player) -> str:
    """Формирует сообщение со статистикой персонажа"""
    exp_needed = EXP_TO_LEVEL * player['level']
    exp_progress = player['exp'] % exp_needed
    
    # Прогресс-бар
    bar_length = 10
    filled = int(exp_progress / exp_needed * bar_length)
    bar = "█" * filled + "░" * (bar_length - filled)

    return f"""📊 СТАТИСТИКА ПЕРСОНАЖА

👤 Имя: {player['name']}
🆙 Уровень: {player['level']} [{bar}]

❤️ Здоровье: {player['health']}/100
⚔️ Атака: {player['attack']}
🔋 Усталость: {player['fatigue']}/{MAX_FATIGUE}

💰 Деньги: {player['money']} руб.

📍 Локация: {get_location(player['current_location']).name if get_location(player['current_location']) else 'Неизвестно'}

✨ Опыт: {exp_progress}/{exp_needed}
🔓 Убежище: {'Открыто ✅' if player['shelter_unlocked'] else 'Закрыто 🔒'}"""


def get_inventory_message(player) -> str:
    """Формирует сообщение с инвентарём"""
    # Получаем инвентарь игрока
    inventory = db.get_inventory(player['vk_id'])

    if not inventory:
        return "🎒 Инвентарь пуст!"

    items_text = []
    for slot in inventory:
        if slot and slot.get('item_id'):
            item = db.get_item(slot['item_id'])
            if item:
                count = slot.get('count', 1)
                items_text.append(f"• {item['icon']} {item['name']} x{count}")

    if not items_text:
        return "🎒 Инвентарь пуст!"

    return "🎒 ИНВЕНТАРЬ\n\n" + "\n".join(items_text)


def send_message(vk, user_id: int, message: str, keyboard=None):
    """Отправка сообщения"""
    kwargs = {
        "user_id": user_id,
        "message": message,
        "random_id": random.randint(0, 2**31)
    }
    if keyboard:
        kwargs["keyboard"] = keyboard.get_keyboard()

    vk.messages.send(**kwargs)


def handle_player_action(vk, user_id: int, action: str, event=None):
    """Обработка действий игрока"""
    player = db.get_player(user_id)
    if not player:
        send_message(vk, user_id, "❌ Вы не зарегистрированы. Напишите /start")
        return

    # Проверка здоровья
    if player['health'] <= 0:
        send_message(vk, user_id, "💀 Вы погибли! Идите в больницу для воскрешения.",
                    keyboard=create_main_keyboard(player['shelter_unlocked']).get_keyboard())
        return
    
    if action == "stats":
        msg = get_stats_message(player)
        vk.messages.send(
            user_id=user_id,
            message=msg,
            keyboard=create_main_keyboard(player['shelter_unlocked']).get_keyboard(),
            random_id=random.randint(0, 2**31)
        )

    elif action == "inventory":
        # Ссылка на Mini App с ID пользователя
        app_url = f"{MINI_APP_URL}?vk_user_id={user_id}"

        # Формируем сообщение с кнопкой открытия Mini App
        message = f"🎒 ИНВЕНТАРЬ\n\nНажми кнопку ниже чтобы открыть инвентарь:"

        # Создаем клавиатуру с кнопкой Mini App
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_open_app_button(VK_APP_ID, "🎒 ОТКРЫТЬ ИНВЕНТАРЬ", VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button("🔙 Назад", color=VkKeyboardColor.NEGATIVE)

        vk.messages.send(
            user_id=user_id,
            message=message,
            keyboard=keyboard.get_keyboard(),
            random_id=random.randint(0, 2**31)
        )

    elif action == "location":
        loc_desc = get_location_description(player['current_location'], player['shelter_unlocked'])
        available = get_available_moves(player['current_location'], player['shelter_unlocked'])
        
        msg = f"{loc_desc}\n\n🚪 Куда пойти?\n\n{format_locations_list(available)}"
        
        vk.messages.send(
            user_id=user_id,
            message=msg,
            keyboard=create_location_keyboard(player['current_location'], player['shelter_unlocked']).get_keyboard(),
            random_id=random.randint(0, 2**31)
        )
    
    elif action == "hospital":
        move_to_location(vk, user_id, "hospital")
    
    elif action == "market":
        move_to_location(vk, user_id, "market")
    
    elif action == "shelter":
        move_to_location(vk, user_id, "shelter")
    
    elif action == "back":
        move_to_location(vk, user_id, "city")
    
    elif action == "heal":
        handle_heal(vk, user_id, player)

    elif action == "rest":
        handle_rest(vk, user_id, player)

    elif action == "attack":
        handle_attack(vk, user_id, player)

    elif action == "buy_weapon":
        handle_buy_item(vk, user_id, player, "ak74", 500)

    elif action == "buy_medkit":
        handle_buy_item(vk, user_id, player, "medkit", 50)

    elif action == "buy_food":
        handle_buy_item(vk, user_id, player, "bread", 20)

    elif action == "buy_ammo":
        handle_buy_item(vk, user_id, player, "ammo_5x45", 30)


def handle_heal(vk, user_id: int, player):
    """Лечение в больнице"""
    if player['current_location'] != "hospital":
        send_message(vk, user_id, "❌ Лечиться можно только в больнице!")
        return

    if player['health'] >= 100:
        send_message(vk, user_id, "✅ Вы полностью здоровы!",
                    keyboard=create_hospital_keyboard().get_keyboard())
        return

    if player['money'] >= HEAL_COST:
        new_health = min(100, player['health'] + 50)
        new_money = player['money'] - HEAL_COST
        db.update_player(user_id, health=new_health, money=new_money)

        send_message(vk, user_id, f"✅ Вы полечились!\n\n❤️ +50 здоровья\n💰 Потрачено: {HEAL_COST} руб.\n❤️ Здоровье: {new_health}/100",
                    keyboard=create_hospital_keyboard().get_keyboard())
    else:
        send_message(vk, user_id, f"❌ Не хватает денег! Нужно {HEAL_COST} руб.",
                    keyboard=create_hospital_keyboard().get_keyboard())


def handle_rest(vk, user_id: int, player):
    """Отдых в убежище"""
    if player['current_location'] != "shelter":
        send_message(vk, user_id, "❌ Отдыхать можно только в убежище!")
        return

    if player['fatigue'] == 0:
        send_message(vk, user_id, "✅ Вы полны сил! Отдыхать не нужно.",
                    keyboard=create_shelter_keyboard().get_keyboard())
        return

    # Снимаем усталость
    new_fatigue = max(0, player['fatigue'] - 50)
    db.update_player(user_id, fatigue=new_fatigue)

    send_message(vk, user_id, f"🛏️ Вы отдохнули в убежище!\n\n🔋 Усталость: {player['fatigue']} → {new_fatigue}",
                keyboard=create_shelter_keyboard().get_keyboard())


def handle_attack(vk, user_id: int, player):
    """Атака монстра/врага"""
    # Проверка усталости
    if player['fatigue'] >= MAX_FATIGUE:
        send_message(vk, user_id, "😴 Вы слишком устали! Отдохните перед боем.",
                    keyboard=create_main_keyboard(player['shelter_unlocked']).get_keyboard())
        return

    # Генерируем врага
    monsters = [
        {"name": "🐕 собака-мутант", "health": 30, "damage": 10, "exp": 20, "money": 15},
        {"name": "🧟 кровосос", "health": 50, "damage": 20, "exp": 40, "money": 30},
        {"name": "👹 бюрер", "health": 80, "damage": 30, "exp": 70, "money": 50},
    ]

    monster = random.choice(monsters)
    player_damage = player['attack'] + random.randint(-5, 10)
    monster_damage = monster['damage'] + random.randint(-3, 5)

    # Простой бой - один удар
    monster['health'] -= player_damage
    player['health'] -= monster_damage

    # Результат боя
    if monster['health'] <= 0:
        # Победа
        exp_gain = monster['exp']
        money_gain = monster['money']
        new_exp = player['exp'] + exp_gain
        new_money = player['money'] + money_gain
        new_fatigue = player['fatigue'] + 20

        # Проверка уровня
        level_up = False
        new_level = player['level']
        exp_needed = EXP_TO_LEVEL * player['level']

        if new_exp >= exp_needed:
            new_level += 1
            new_exp -= exp_needed
            level_up = True

        db.update_player(
            user_id,
            exp=new_exp,
            money=new_money,
            fatigue=new_fatigue,
            level=new_level,
            health=max(0, player['health'])
        )

        msg = f"⚔️ БОЙ С {monster['name']}\n\n"
        msg += f"Ты нанёс {player_damage} урона!\n"
        msg += f"Враг нанёс {monster_damage} урона!\n\n"
        msg += f"✅ ПОБЕДА!\n"
        msg += f"✨ +{exp_gain} опыта\n"
        msg += f"💰 +{money_gain} руб."

        if level_up:
            msg += f"\n\n🆙 УРОВЕНЬ UP! Теперь уровень {new_level}!"

        send_message(vk, user_id, msg,
                    keyboard=create_main_keyboard(player['shelter_unlocked']).get_keyboard())
    else:
        # Поражение
        new_fatigue = player['fatigue'] + 20
        db.update_player(user_id, health=max(0, player['health']), fatigue=new_fatigue)

        msg = f"⚔️ БОЙ С {monster['name']}\n\n"
        msg += f"Ты нанёс {player_damage} урона!\n"
        msg += f"Враг нанёс {monster_damage} урона!\n\n"
        msg += f"💀 ПОРАЖЕНИЕ\n"
        msg += f"❤️ Здоровье: {max(0, player['health'])}/100"

        send_message(vk, user_id, msg,
                    keyboard=create_main_keyboard(player['shelter_unlocked']).get_keyboard())


def handle_buy_item(vk, user_id: int, player, item_id: str, price: int):
    """Покупка предмета"""
    if player['current_location'] != "market":
        send_message(vk, user_id, "❌ Покупать можно только на Черном рынке!",
                    keyboard=create_market_keyboard().get_keyboard())
        return

    if player['money'] < price:
        send_message(vk, user_id, f"❌ Не хватает денег! Нужно {price} руб.",
                    keyboard=create_market_keyboard().get_keyboard())
        return

    # Добавляем предмет в инвентарь
    success = db.add_item(user_id, item_id, 1)

    if success:
        db.update_player(user_id, money=player['money'] - price)
        item = db.get_item(item_id)

        send_message(vk, user_id, f"✅ Куплено: {item['icon']} {item['name']}\n💰 Потрачено: {price} руб.",
                    keyboard=create_market_keyboard().get_keyboard())
    else:
        send_message(vk, user_id, "❌ Не удалось купить предмет!",
                    keyboard=create_market_keyboard().get_keyboard())


def move_to_location(vk, user_id: int, location_id: str):
    """Перемещение игрока"""
    player = db.get_player(user_id)
    if not player:
        return
    
    # Проверка доступа к убежищу
    if location_id == "shelter" and not player['shelter_unlocked']:
        send_message(vk, user_id, "🔒 Убежище заперто. Сначала нужно найти способ попасть внутрь.")
        return
    
    # Проверка связи между локациями
    current_loc = get_location(player['current_location'])
    if location_id not in current_loc.connected_locations:
        send_message(vk, user_id, "❌ Отсюда туда нельзя попасть!")
        return

    # Проверка усталости для перемещения
    if player['fatigue'] >= MAX_FATIGUE:
        send_message(vk, user_id, "😴 Вы слишком устали! Отдохните перед дорогой.",
                    keyboard=create_main_keyboard(player['shelter_unlocked']).get_keyboard())
        return

    # Добавляем усталость
    new_fatigue = player['fatigue'] + FATIGUE_PER_ACTION
    
    # Обновляем локацию
    db.update_player(user_id, current_location=location_id, fatigue=new_fatigue)
    
    # Показываем новую локацию с правильной клавиатурой
    player = db.get_player(user_id)
    loc_desc = get_location_description(location_id, player['shelter_unlocked'])

    # Выбираем клавиатуру для локации
    keyboard = None
    if location_id == "hospital":
        keyboard = create_hospital_keyboard()
    elif location_id == "market":
        keyboard = create_market_keyboard()
    elif location_id == "shelter":
        keyboard = create_shelter_keyboard()
    else:
        keyboard = create_location_keyboard(location_id, player['shelter_unlocked'])

    msg = f"{loc_desc}\n\n🔋 Усталость: {new_fatigue}/{MAX_FATIGUE}"

    vk.messages.send(
        user_id=user_id,
        message=msg,
        keyboard=keyboard.get_keyboard(),
        random_id=random.randint(0, 2**31)
    )


def main():
    """Главная функция бота"""
    vk_session = vk_api.VkApi(token=VK_TOKEN)
    vk = vk_session.get_api()
    longpoll = VkBotLongPoll(vk_session, GROUP_ID)
    
    print("🤖 Бот S.T.A.L.K.E.R. запущен!")
    
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            user_id = event.obj.message['from_id']
            text = event.obj.message.get('text', '').strip().lower()
            
            # Получаем имя пользователя
            try:
                user_info = vk.users.get(user_ids=user_id)[0]
                user_name = f"{user_info['first_name']} {user_info['last_name']}"
            except:
                user_name = "Stalker"
            
            # Команда /start
            if text == '/start' or text == 'start' or text == 'начать':
                if not db.player_exists(user_id):
                    db.create_player(user_id, user_name)
                    welcome_msg = f"""🌍 ДОБРО ПОЖАЛОВАТЬ В ЗОНУ, СТАЛКЕР!

Ты прибыл в заброшенный город. Твоё приключение начинается здесь.

📍 Ты находишься в Городе.
⚠️ Убежище пока закрыто — нужно найти способ попасть внутрь.

🎮 Используй кнопки для навигации!"""

                    vk.messages.send(
                        user_id=user_id,
                        message=welcome_msg,
                        keyboard=create_main_keyboard(False).get_keyboard(),
                        random_id=random.randint(0, 2**31)
                    )
                else:
                    player = db.get_player(user_id)
                    vk.messages.send(
                        user_id=user_id,
                        message=f"✅ С возвращением, сталкер {player['name']}!\n\n📍 Ты в: {get_location(player['current_location']).name}",
                        keyboard=create_main_keyboard(player['shelter_unlocked']).get_keyboard(),
                        random_id=random.randint(0, 2**31)
                    )
            
            # Обработка кнопок
            elif text == "📍 локация" or text == "локация":
                handle_player_action(vk, user_id, "location")
            
            elif text == "📊 статистика" or text == "статистика":
                handle_player_action(vk, user_id, "stats")
            
            elif text == "🎒 инвентарь" or text == "инвентарь":
                handle_player_action(vk, user_id, "inventory")

            elif text == "⚔️ атаковать" or text == "атаковать":
                handle_player_action(vk, user_id, "attack")

            elif "больница" in text:
                handle_player_action(vk, user_id, "hospital")
            
            elif "рынок" in text or "черный" in text:
                handle_player_action(vk, user_id, "market")
            
            elif "убежище" in text:
                handle_player_action(vk, user_id, "shelter")
            
            elif "лечение" in text or "лечиться" in text:
                handle_player_action(vk, user_id, "heal")

            elif "отдохнуть" in text:
                handle_player_action(vk, user_id, "rest")

            elif "назад" in text or "в город" in text:
                handle_player_action(vk, user_id, "back")
            
            elif "оружие" in text:
                handle_player_action(vk, user_id, "buy_weapon")

            elif "аптечк" in text:
                handle_player_action(vk, user_id, "buy_medkit")

            elif "еда" in text or "хлеб" in text:
                handle_player_action(vk, user_id, "buy_food")

            elif "патрон" in text:
                handle_player_action(vk, user_id, "buy_ammo")

            # Команда /help
            elif text == '/help':
                help_msg = """📖 КОМАНДЫ:

/start - Начать игру
/stats - Ваша статистика
/inventory - Открыть инвентарь

🎮 Игра в стиле S.T.A.L.K.E.R."""
                vk.messages.send(
                    user_id=user_id,
                    message=help_msg,
                    random_id=random.randint(0, 2**31)
                )


if __name__ == '__main__':
    main()
