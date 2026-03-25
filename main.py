"""Бот S.T.A.L.K.E.R. для ВК"""
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import random
import sys
import os

# Добавляем пути для импортов
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import VK_TOKEN, GROUP_ID, FATIGUE_PER_ACTION, EXP_TO_LEVEL
from db.database import db
from game.locations import (
    get_location_description, 
    get_available_moves, 
    format_locations_list,
    get_location
)


def create_main_keyboard(shelter_unlocked: bool = False) -> VkKeyboard:
    """Главная клавиатура с кнопками"""
    keyboard = VkKeyboard(one_time=False)
    
    keyboard.add_button("📍 Локация", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("📊 Статистика", color=VkKeyboardColor.PRIMARY)
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
    keyboard.add_button("🔙 Назад", color=VkKeyboardColor.NEGATIVE)
    
    return keyboard


def get_stats_message(player) -> str:
    """Формирует сообщение со статистикой персонажа"""
    exp_needed = EXP_TO_LEVEL * player['level']
    exp_progress = player['exp'] % exp_needed
    
    return f"""📊 СТАТИСТИКА ПЕРСОНАЖА

👤 Имя: {player['name']}
🆙 Уровень: {player['level']}

❤️ Здоровье: {player['health']}/100
⚔️ Атака: {player['attack']}
🔋 Усталость: {player['fatigue']}/100

💰 Деньги: {player['money']} руб.

📍 Локация: {get_location(player['current_location']).name if get_location(player['current_location']) else 'Неизвестно'}

✨ Опыт: {exp_progress}/{exp_needed}
🔓 Убежище: {'Открыто' if player['shelter_unlocked'] else 'Закрыто'}"""


def handle_player_action(vk, user_id: int, action: str):
    """Обработка действий игрока"""
    player = db.get_player(user_id)
    if not player:
        send_message(vk, user_id, "❌ Вы не зарегистрированы. Напишите /start")
        return
    
    # Проверка усталости
    if player['fatigue'] >= 100:
        send_message(vk, user_id, "😴 Вы слишком устали! Отдохните в убежище или больнице.")
        return
    
    # Проверка здоровья
    if player['health'] <= 0:
        send_message(vk, user_id, "💀 Вы погибли! Посетите больницу для воскрешения.")
        return
    
    if action == "stats":
        msg = get_stats_message(player)
        vk.messages.send(
            user_id=user_id,
            message=msg,
            keyboard=create_main_keyboard(player['shelter_unlocked']).get_keyboard(),
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
        # Лечение в больнице
        if player['current_location'] == "hospital":
            if player['money'] >= 50:
                new_health = min(100, player['health'] + 50)
                new_money = player['money'] - 50
                db.update_player(user_id, health=new_health, money=new_money)
                send_message(vk, user_id, "✅ Вы полечились! +50 здоровья. Потрачено: 50 руб.", keyboard=create_main_keyboard(player['shelter_unlocked']).get_keyboard())
            else:
                send_message(vk, user_id, "❌ Не хватает денег! Нужно 50 руб.", keyboard=create_main_keyboard(player['shelter_unlocked']).get_keyboard())
        else:
            send_message(vk, user_id, "❌ Лечиться можно только в больнице!")


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
    
    # Добавляем усталость
    new_fatigue = player['fatigue'] + FATIGUE_PER_ACTION
    
    # Обновляем локацию
    db.update_player(user_id, current_location=location_id, fatigue=new_fatigue)
    
    # Показываем новую локацию
    player = db.get_player(user_id)
    loc_desc = get_location_description(location_id, player['shelter_unlocked'])
    available = get_available_moves(location_id, player['shelter_unlocked'])
    
    msg = f"{loc_desc}\n\n🚪 Куда пойти?\n\n{format_locations_list(available)}"
    
    vk.messages.send(
        user_id=user_id,
        message=msg,
        keyboard=create_location_keyboard(location_id, player['shelter_unlocked']).get_keyboard(),
        random_id=random.randint(0, 2**31)
    )


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

Используй кнопки для навигации!"""
                    
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
                        message=f"✅ С возвращением, сталкер {player['name']}!\n\nТы в локации: {get_location(player['current_location']).name}",
                        keyboard=create_main_keyboard(player['shelter_unlocked']).get_keyboard(),
                        random_id=random.randint(0, 2**31)
                    )
            
            # Обработка кнопок
            elif text == "📍 локация" or text == "локация":
                handle_player_action(vk, user_id, "location")
            
            elif text == "📊 статистика" or text == "статистика":
                handle_player_action(vk, user_id, "stats")
            
            elif "больница" in text:
                handle_player_action(vk, user_id, "hospital")
            
            elif "рынок" in text or "черный" in text:
                handle_player_action(vk, user_id, "market")
            
            elif "убежище" in text:
                handle_player_action(vk, user_id, "shelter")
            
            elif "назад" in text:
                handle_player_action(vk, user_id, "back")
            
            # Команда /help
            elif text == '/help':
                help_msg = """📖 КОМАНДЫ:

/start - Начать игру
/stats - Показать статистику
/go [локация] - Перейти к локации

🎮 Игра в стиле S.T.A.L.K.E.R."""
                vk.messages.send(
                    user_id=user_id,
                    message=help_msg,
                    random_id=random.randint(0, 2**31)
                )


if __name__ == '__main__':
    main()
