"""Класс игрока и игровая логика"""
import json
from db.database import db
from game.locations import (
    get_location_description, 
    get_available_moves, 
    format_locations_list,
    LOCATIONS,
    get_location
)
from config import (
    INITIAL_HEALTH, INITIAL_ATTACK, INITIAL_FATIGUE,
    INITIAL_EXP, EXP_TO_LEVEL, MAX_FATIGUE, FATIGUE_PER_ACTION
)


class Player:
    def __init__(self, vk_id: int, name: str = None):
        self.vk_id = vk_id
        self.data = self._load_or_create(name)

    def _load_or_create(self, name: str = None) -> dict:
        """Загрузить игрока или создать нового"""
        player = db.get_player(self.vk_id)
        if player:
            return player
        return db.create_player(self.vk_id, name or f"Stalker_{self.vk_id}")

    def reload(self):
        """Перезагрузить данные из БД"""
        self.data = db.get_player(self.vk_id)

    @property
    def health(self) -> int:
        return self.data["health"]

    @property
    def attack(self) -> int:
        return self.data["attack"]

    @property
    def fatigue(self) -> int:
        return self.data["fatigue"]

    @property
    def exp(self) -> int:
        return self.data["exp"]

    @property
    def level(self) -> int:
        return self.data["level"]

    @property
    def money(self) -> int:
        return self.data["money"]

    @property
    def current_location(self) -> str:
        return self.data["current_location"]

    @property
    def shelter_unlocked(self) -> bool:
        return self.data["shelter_unlocked"]

    @property
    def shop_category(self) -> str:
        return self.data.get("shop_category")

    @shop_category.setter
    def shop_category(self, value: str):
        """Установить текущую категорию магазина"""
        self.data["shop_category"] = value

    @property
    def equipped_weapon(self) -> str:
        return self.data.get("equipped_weapon")

    @property
    def equipped_armor(self) -> str:
        return self.data.get("equipped_armor")

    @property
    def exp_to_next_level(self) -> int:
        """Опыт до следующего уровня"""
        return EXP_TO_LEVEL * self.level - self.exp

    def add_fatigue(self, amount: int = FATIGUE_PER_ACTION):
        """Добавить усталость"""
        new_fatigue = min(self.fatigue + amount, MAX_FATIGUE)
        db.update_player(self.vk_id, fatigue=new_fatigue)
        self.reload()

    def heal(self, amount: int = None):
        """Лечение игрока"""
        if amount is None:
            amount = INITIAL_HEALTH - self.health
        
        new_health = min(self.health + amount, INITIAL_HEALTH)
        healed = new_health - self.health
        db.update_player(self.vk_id, health=new_health)
        self.reload()
        return healed

    def take_damage(self, damage: int):
        """Получить урон"""
        new_health = max(self.health - damage, 0)
        db.update_player(self.vk_id, health=new_health)
        self.reload()
        return new_health

    def add_exp(self, amount: int):
        """Добавить опыт и проверить повышение уровня"""
        new_exp = self.exp + amount
        new_level = self.level
        leveled_up = False

        # Проверка на повышение уровня
        while new_exp >= EXP_TO_LEVEL * new_level:
            new_exp -= EXP_TO_LEVEL * new_level
            new_level += 1
            leveled_up = True

        db.update_player(self.vk_id, exp=new_exp, level=new_level)
        self.reload()
        return leveled_up

    def unlock_shelter(self):
        """Открыть убежище"""
        db.update_player(self.vk_id, shelter_unlocked=True)
        self.reload()

    def change_location(self, new_location: str) -> bool:
        """Переместиться в новую локацию"""
        available = get_available_moves(self.current_location, self.shelter_unlocked)
        
        if new_location not in available:
            return False

        db.update_player(self.vk_id, current_location=new_location)
        self.add_fatigue()
        self.reload()
        return True

    def set_location(self, new_location: str) -> None:
        """Установить локацию без проверок и без затрат усталости (для кнопки 'В город')"""
        db.update_player(self.vk_id, current_location=new_location)
        self.reload()

    def get_stats_text(self) -> str:
        """Получить текст статистики персонажа"""
        # Получаем бонусы от экипировки
        total_attack, total_defense = self.attack()
        weapon_bonus = total_attack - INITIAL_ATTACK
        armor_bonus = total_defense

        # Формируем строку экипировки
        equip_text = ""
        if self.equipped_weapon:
            from db.database import db
            item = db.get_item(self.equipped_weapon)
            if item:
                stats = item.get('stats')
                if stats:
                    if isinstance(stats, str):
                        stats = json.loads(stats)
                    damage = stats.get('damage', 0)
                else:
                    damage = 0
                equip_text += f"\n🔫 Оружие: {item['name']} (+{damage} урона)"

        if self.equipped_armor:
            from db.database import db
            item = db.get_item(self.equipped_armor)
            if item:
                stats = item.get('stats')
                if stats:
                    if isinstance(stats, str):
                        stats = json.loads(stats)
                    defense = stats.get('defense', 0)
                else:
                    defense = 0
                equip_text += f"\n🛡️ Броня: {item['name']} (+{defense} защиты)"

        if not equip_text:
            equip_text = "\n⚠️ Нет экипировки"

        return f"""📊 СТАТИСТИКА ПЕРСОНАЖА

👤 Имя: {self.data['name']}
⬆️ Уровень: {self.level}
💰 Деньги: {self.money} руб.

❤️ Здоровье: {self.health}/{INITIAL_HEALTH}
⚔️ Атака: {total_attack} ({INITIAL_ATTACK} + {weapon_bonus}){weapon_bonus > 0 and f' от оружия' or ''}
🛡️ Защита: {total_defense} ({armor_bonus} от брони)
🔋 Усталость: {self.fatigue}/{MAX_FATIGUE}

📈 Опыт: {self.exp}/{EXP_TO_LEVEL * self.level}
⏳ До следующего уровня: {self.exp_to_next_level} XP

🎒 ЭКИПИРОВКА:{equip_text}"""

    def get_location_text(self) -> str:
        """Получить текст текущей локации"""
        desc = get_location_description(self.current_location, self.shelter_unlocked)
        available = get_available_moves(self.current_location, self.shelter_unlocked)
        
        moves_text = format_locations_list(available)
        
        return f"{desc}\n\n📍 Куда идти:\n{moves_text}"

    def attack(self) -> tuple:
        """Атаковать - вернуть урон и защиту"""
        base_damage = INITIAL_ATTACK
        base_defense = 0

        # Базовый урон от оружия
        weapon_damage = 0
        if self.equipped_weapon:
            from db.database import db
            item = db.get_item(self.equipped_weapon)
            if item and item.get('stats'):
                stats = item['stats']
                if isinstance(stats, str):
                    stats = json.loads(stats)
                weapon_damage = stats.get('damage', 0)

        # Защита от брони
        armor_defense = 0
        if self.equipped_armor:
            from db.database import db
            item = db.get_item(self.equipped_armor)
            if item and item.get('stats'):
                stats = item['stats']
                if isinstance(stats, str):
                    stats = json.loads(stats)
                armor_defense = stats.get('defense', 0)

        total_damage = base_damage + weapon_damage
        total_defense = base_defense + armor_defense

        return total_damage, total_defense

    def get_equipped_text(self) -> str:
        """Получить текст об экипировке"""
        text = "🎒 ЭКИПИРОВКА\n\n"

        if self.equipped_weapon:
            from db.database import db
            item = db.get_item(self.equipped_weapon)
            if item:
                stats = item.get('stats')
                if stats:
                    if isinstance(stats, str):
                        stats = json.loads(stats)
                    damage = stats.get('damage', 0)
                else:
                    damage = 0
                text += f"🔫 Оружие: {item['name']} (урон: {damage})\n"
            else:
                text += f"🔫 Оружие: {self.equipped_weapon}\n"
        else:
            text += "🔫 Оружие: нет\n"

        if self.equipped_armor:
            from db.database import db
            item = db.get_item(self.equipped_armor)
            if item:
                stats = item.get('stats')
                if stats:
                    if isinstance(stats, str):
                        stats = json.loads(stats)
                    defense = stats.get('defense', 0)
                else:
                    defense = 0
                text += f"🛡️ Броня: {item['name']} (защита: {defense})\n"
            else:
                text += f"🛡️ Броня: {self.equipped_armor}\n"
        else:
            text += "🛡️ Броня: нет\n"

        return text


def get_player(vk_id: int, name: str = None) -> Player:
    """Получить объект игрока"""
    return Player(vk_id, name)
