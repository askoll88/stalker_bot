"""S.T.A.L.K.E.R. Bot for VK"""
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import random
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


def create_main_keyboard(shelter_unlocked: bool = False) -> VkKeyboard:
    keyboard = VkKeyboard(one_time=False)
    
    keyboard.add_button("📍 Location", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("📊 Stats", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("🎒 Inventory", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("⚔️ Attack", color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button("🏥 Hospital", color=VkKeyboardColor.SECONDARY)
    keyboard.add_button("🛒 Market", color=VkKeyboardColor.SECONDARY)
    keyboard.add_line()
    
    if shelter_unlocked:
        keyboard.add_button("🔓 Shelter", color=VkKeyboardColor.POSITIVE)
    else:
        keyboard.add_button("🔒 Shelter", color=VkKeyboardColor.NEGATIVE)
    
    return keyboard


def create_location_keyboard(current_location: str, shelter_unlocked: bool = False) -> VkKeyboard:
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
            
            name_parts = loc.name.split()
            btn_text = name_parts[0] + " " + name_parts[1] if len(name_parts) > 1 else loc.name
            keyboard.add_button(btn_text, color=color)
            
            if (i + 1) % 2 == 0 and i < len(available) - 1:
                keyboard.add_line()
    
    keyboard.add_line()
    keyboard.add_button("🔙 To City", color=VkKeyboardColor.NEGATIVE)
    
    return keyboard


def create_hospital_keyboard() -> VkKeyboard:
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("💊 Heal (50 rub)", color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button("🔙 To City", color=VkKeyboardColor.NEGATIVE)
    return keyboard


def create_market_keyboard() -> VkKeyboard:
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("🔫 Weapons", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("🩹 Medkits", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("🍞 Food", color=VkKeyboardColor.SECONDARY)
    keyboard.add_button("📦 Ammo", color=VkKeyboardColor.SECONDARY)
    keyboard.add_line()
    keyboard.add_button("🔙 To City", color=VkKeyboardColor.NEGATIVE)
    return keyboard


def create_shelter_keyboard() -> VkKeyboard:
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("🛏️ Rest", color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button("🔙 To City", color=VkKeyboardColor.NEGATIVE)
    return keyboard


def get_stats_message(player) -> str:
    exp_needed = EXP_TO_LEVEL * player['level']
    exp_progress = player['exp'] % exp_needed
    
    bar_length = 10
    filled = int(exp_progress / exp_needed * bar_length)
    bar = "█" * filled + "░" * (bar_length - filled)
    
    return f"""📊 PLAYER STATS

👤 Name: {player['name']}
🆙 Level: {player['level']} [{bar}]

❤️ Health: {player['health']}/100
⚔️ Attack: {player['attack']}
🔋 Fatigue: {player['fatigue']}/{MAX_FATIGUE}

💰 Money: {player['money']} rub

📍 Location: {get_location(player['current_location']).name if get_location(player['current_location']) else 'Unknown'}

✨ Exp: {exp_progress}/{exp_needed}
🔓 Shelter: {'Open ✅' if player['shelter_unlocked'] else 'Locked 🔒'}"""


def send_message(vk, user_id: int, message: str, keyboard=None):
    kwargs = {
        "user_id": user_id,
        "message": message,
        "random_id": random.randint(0, 2**31)
    }
    if keyboard:
        kwargs["keyboard"] = keyboard.get_keyboard()
    
    vk.messages.send(**kwargs)


def handle_player_action(vk, user_id: int, action: str):
    player = db.get_player(user_id)
    if not player:
        send_message(vk, user_id, "❌ You are not registered. Write /start")
        return
    
    if player['health'] <= 0:
        send_message(vk, user_id, "💀 You died! Go to hospital to revive.",
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
        message = "🎒 INVENTORY\n\nClick button below to open inventory:"
        
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_open_app_button(VK_APP_ID, "🎒 OPEN INVENTORY", VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button("🔙 Back", color=VkKeyboardColor.NEGATIVE)
        
        vk.messages.send(
            user_id=user_id,
            message=message,
            keyboard=keyboard.get_keyboard(),
            random_id=random.randint(0, 2**31)
        )
    
    elif action == "location":
        loc_desc = get_location_description(player['current_location'], player['shelter_unlocked'])
        available = get_available_moves(player['current_location'], player['shelter_unlocked'])
        
        msg = f"{loc_desc}\n\n🚪 Where to go?\n\n{format_locations_list(available)}"
        
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
    if player['current_location'] != "hospital":
        send_message(vk, user_id, "❌ You can heal only at hospital!")
        return
    
    if player['health'] >= 100:
        send_message(vk, user_id, "✅ You are fully healthy!",
                    keyboard=create_hospital_keyboard().get_keyboard())
        return
    
    if player['money'] >= HEAL_COST:
        new_health = min(100, player['health'] + 50)
        new_money = player['money'] - HEAL_COST
        db.update_player(user_id, health=new_health, money=new_money)
        
        send_message(vk, user_id, f"✅ You healed!\n\n❤️ +50 health\n💰 Spent: {HEAL_COST} rub\n❤️ Health: {new_health}/100",
                    keyboard=create_hospital_keyboard().get_keyboard())
    else:
        send_message(vk, user_id, f"❌ Not enough money! Need {HEAL_COST} rub.",
                    keyboard=create_hospital_keyboard().get_keyboard())


def handle_rest(vk, user_id: int, player):
    if player['current_location'] != "shelter":
        send_message(vk, user_id, "❌ You can rest only at shelter!")
        return
    
    if player['fatigue'] == 0:
        send_message(vk, user_id, "✅ You are full of energy! No need to rest.",
                    keyboard=create_shelter_keyboard().get_keyboard())
        return
    
    new_fatigue = max(0, player['fatigue'] - 50)
    db.update_player(user_id, fatigue=new_fatigue)
    
    send_message(vk, user_id, f"🛏️ You rested in shelter!\n\n🔋 Fatigue: {player['fatigue']} → {new_fatigue}",
                keyboard=create_shelter_keyboard().get_keyboard())


def handle_attack(vk, user_id: int, player):
    if player['fatigue'] >= MAX_FATIGUE:
        send_message(vk, user_id, "😴 You are too tired! Rest before fighting.",
                    keyboard=create_main_keyboard(player['shelter_unlocked']).get_keyboard())
        return
    
    monsters = [
        {"name": "🐕 mutant dog", "health": 30, "damage": 10, "exp": 20, "money": 15},
        {"name": "🧟 bloodsucker", "health": 50, "damage": 20, "exp": 40, "money": 30},
        {"name": "👹 burer", "health": 80, "damage": 30, "exp": 70, "money": 50},
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
        
        db.update_player(
            user_id,
            exp=new_exp,
            money=new_money,
            fatigue=new_fatigue,
            level=new_level,
            health=max(0, player['health'])
        )
        
        msg = f"⚔️ FIGHT WITH {monster['name']}\n\n"
        msg += f"You dealt {player_damage} damage!\n"
        msg += f"Enemy dealt {monster_damage} damage!\n\n"
        msg += f"✅ VICTORY!\n"
        msg += f"✨ +{exp_gain} exp\n"
        msg += f"💰 +{money_gain} rub"
        
        if level_up:
            msg += f"\n\n🆙 LEVEL UP! Now level {new_level}!"
        
        send_message(vk, user_id, msg,
                    keyboard=create_main_keyboard(player['shelter_unlocked']).get_keyboard())
    else:
        new_fatigue = player['fatigue'] + 20
        db.update_player(user_id, health=max(0, player['health']), fatigue=new_fatigue)
        
        msg = f"⚔️ FIGHT WITH {monster['name']}\n\n"
        msg += f"You dealt {player_damage} damage!\n"
        msg += f"Enemy dealt {monster_damage} damage!\n\n"
        msg += f"💀 DEFEAT\n"
        msg += f"❤️ Health: {max(0, player['health'])}/100"
        
        send_message(vk, user_id, msg,
                    keyboard=create_main_keyboard(player['shelter_unlocked']).get_keyboard())


def handle_buy_item(vk, user_id: int, player, item_id: str, price: int):
    if player['current_location'] != "market":
        send_message(vk, user_id, "❌ You can buy only at Black Market!",
                    keyboard=create_market_keyboard().get_keyboard())
        return
    
    if player['money'] < price:
        send_message(vk, user_id, f"❌ Not enough money! Need {price} rub.",
                    keyboard=create_market_keyboard().get_keyboard())
        return
    
    success = db.add_item(user_id, item_id, 1)
    
    if success:
        db.update_player(user_id, money=player['money'] - price)
        item = db.get_item(item_id)
        
        send_message(vk, user_id, f"✅ Bought: {item['icon']} {item['name']}\n💰 Spent: {price} rub",
                    keyboard=create_market_keyboard().get_keyboard())
    else:
        send_message(vk, user_id, "❌ Could not buy item!",
                    keyboard=create_market_keyboard().get_keyboard())


def move_to_location(vk, user_id: int, location_id: str):
    player = db.get_player(user_id)
    if not player:
        return
    
    if location_id == "shelter" and not player['shelter_unlocked']:
        send_message(vk, user_id, "🔒 Shelter is locked. Find a way to get inside.")
        return
    
    current_loc = get_location(player['current_location'])
    if location_id not in current_loc.connected_locations:
        send_message(vk, user_id, "❌ You can't go there from here!")
        return
    
    if player['fatigue'] >= MAX_FATIGUE:
        send_message(vk, user_id, "😴 You are too tired! Rest before traveling.",
                    keyboard=create_main_keyboard(player['shelter_unlocked']).get_keyboard())
        return
    
    new_fatigue = player['fatigue'] + FATIGUE_PER_ACTION
    db.update_player(user_id, current_location=location_id, fatigue=new_fatigue)
    
    player = db.get_player(user_id)
    loc_desc = get_location_description(location_id, player['shelter_unlocked'])
    
    keyboard = None
    if location_id == "hospital":
        keyboard = create_hospital_keyboard()
    elif location_id == "market":
        keyboard = create_market_keyboard()
    elif location_id == "shelter":
        keyboard = create_shelter_keyboard()
    else:
        keyboard = create_location_keyboard(location_id, player['shelter_unlocked'])
    
    msg = f"{loc_desc}\n\n🔋 Fatigue: {new_fatigue}/{MAX_FATIGUE}"
    
    vk.messages.send(
        user_id=user_id,
        message=msg,
        keyboard=keyboard.get_keyboard(),
        random_id=random.randint(0, 2**31)
    )


def main():
    print("Starting S.T.A.L.K.E.R. Bot...")
    
    vk_session = vk_api.VkApi(token=VK_TOKEN)
    vk = vk_session.get_api()
    longpoll = VkBotLongPoll(vk_session, GROUP_ID)
    
    print("Bot S.T.A.L.K.E.R. started!")
    
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            user_id = event.obj.message['from_id']
            text = event.obj.message.get('text', '').strip().lower()
            
            try:
                user_info = vk.users.get(user_ids=user_id)[0]
                user_name = f"{user_info['first_name']} {user_info['last_name']}"
            except:
                user_name = "Stalker"
            
            if text == '/start' or text == 'start' or text == 'begin':
                if not db.player_exists(user_id):
                    db.create_player(user_id, user_name)
                    welcome_msg = f"""🌍 WELCOME TO THE ZONE, STALKER!

You arrived at an abandoned city. Your adventure starts here.

📍 You are in the City.
⚠️ Shelter is locked - find a way to get inside.

Use buttons for navigation!"""
                    
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
                        message=f"✅ Welcome back, stalker {player['name']}!\n\n📍 You are in: {get_location(player['current_location']).name}",
                        keyboard=create_main_keyboard(player['shelter_unlocked']).get_keyboard(),
                        random_id=random.randint(0, 2**31)
                    )
            
            elif text == "📍 location" or text == "location":
                handle_player_action(vk, user_id, "location")
            
            elif text == "📊 stats" or text == "stats":
                handle_player_action(vk, user_id, "stats")
            
            elif text == "🎒 inventory" or text == "inventory":
                handle_player_action(vk, user_id, "inventory")
            
            elif text == "⚔️ attack" or text == "attack":
                handle_player_action(vk, user_id, "attack")
            
            elif "hospital" in text:
                handle_player_action(vk, user_id, "hospital")
            
            elif "market" in text or "black" in text:
                handle_player_action(vk, user_id, "market")
            
            elif "shelter" in text:
                handle_player_action(vk, user_id, "shelter")
            
            elif "heal" in text:
                handle_player_action(vk, user_id, "heal")
            
            elif "rest" in text:
                handle_player_action(vk, user_id, "rest")
            
            elif "back" in text or "to city" in text:
                handle_player_action(vk, user_id, "back")
            
            elif "weapon" in text:
                handle_player_action(vk, user_id, "buy_weapon")
            
            elif "medkit" in text:
                handle_player_action(vk, user_id, "buy_medkit")
            
            elif "food" in text or "bread" in text:
                handle_player_action(vk, user_id, "buy_food")
            
            elif "ammo" in text:
                handle_player_action(vk, user_id, "buy_ammo")
            
            elif text == '/help':
                help_msg = """📖 COMMANDS:

/start - Start game
/stats - Your stats
/inventory - Open inventory

🎮 S.T.A.L.K.E.R. style game"""
                vk.messages.send(
                    user_id=user_id,
                    message=help_msg,
                    random_id=random.randint(0, 2**31)
                )


if __name__ == '__main__':
    main()
