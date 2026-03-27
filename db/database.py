import psycopg2
from psycopg2.extras import RealDictCursor
from config import DB_CONFIG


class Database:
    def __init__(self):
        self.conn = None
        self.connect()
        self.init_tables()
        self.init_items()

    def connect(self):
        self.conn = psycopg2.connect(**DB_CONFIG)
        self.conn.autocommit = True

    def init_tables(self):
        with self.conn.cursor() as cur:
            cur.execute("""CREATE TABLE IF NOT EXISTS players (
                vk_id BIGINT PRIMARY KEY, name VARCHAR(100),
                health INTEGER DEFAULT 100, attack INTEGER DEFAULT 10,
                fatigue INTEGER DEFAULT 0, exp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1, money INTEGER DEFAULT 100,
                current_location VARCHAR(50) DEFAULT 'city',
                shelter_unlocked BOOLEAN DEFAULT FALSE,
                equipped_weapon VARCHAR(50) DEFAULT NULL,
                equipped_armor VARCHAR(50) DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

            cur.execute("""CREATE TABLE IF NOT EXISTS items (
                id VARCHAR(50) PRIMARY KEY, name VARCHAR(100),
                description TEXT, icon VARCHAR(20), type VARCHAR(50),
                price INTEGER DEFAULT 0, effect JSONB, stats JSONB)""")

            cur.execute("""CREATE TABLE IF NOT EXISTS player_inventory (
                id SERIAL PRIMARY KEY, vk_id BIGINT REFERENCES players(vk_id),
                item_id VARCHAR(50) REFERENCES items(id),
                slot_number INTEGER DEFAULT 0, count INTEGER DEFAULT 1,
                is_equipped BOOLEAN DEFAULT FALSE)""")

    def init_items(self):
        items = [
            ("medkit", "Аптечка", "Восстанавливает 50 HP", "medkit", "consumable", 50, '{"health":50}', None),
            ("medkit_large", "Медицинская аптечка", "Восстанавливает 100 HP", "medkit_lg", "consumable", 50, '{"health":100}', None),
            ("bandage", "Бинт", "Восстанавливает 20 HP", "bandage", "consumable", 25, '{"health":20}', None),
            ("energy_drink", "Энергетик", "Снижает усталость", "energy", "consumable", 30, '{"fatigue":-30}', None),
            ("bread", "Хлеб", "Снижает усталость", "bread", "food", 20, '{"fatigue":-20}', None),
            ("water", "Вода", "Бутылка воды", "water", "food", 10, '{"fatigue":-10}', None),
            ("pm", "ПМ", "Пистолет Макарова", "pm", "weapon", 200, None, '{"damage":15}'),
            ("ak74", "АК-74", "Автомат Калашникова", "ak74", "weapon", 500, None, '{"damage":35}'),
            ("armor_vest", "Бронежилет", "Защита +30", "armor", "armor", 300, None, '{"defense":30}'),
            ("ammo_9x18", "Патроны 9x18", "12 штук", "ammo9", "ammo", 30, None, None),
            ("ammo_5x45", "Патроны 5.45", "30 штук", "ammo5", "ammo", 60, None, None),
            ("nagan", "Наган", "Стартовый револьвер", "nagan", "weapon", 0, None, '{"damage":5}'),
            ("leather_jacket", "Кожаная куртка", "Стартовая броня", "jacket", "armor", 0, None, '{"defense":10}'),
        ]
        for item in items:
            with self.conn.cursor() as cur:
                cur.execute("""INSERT INTO items VALUES (%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT(id) DO NOTHING""", item)

    def get_player(self, vk_id):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM players WHERE vk_id=%s", (vk_id,))
            return cur.fetchone()

    def create_player(self, vk_id, name):
        from config import INITIAL_HEALTH, INITIAL_ATTACK, INITIAL_MONEY
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""INSERT INTO players (vk_id,name,health,attack,money,current_location)
                VALUES (%s,%s,%s,%s,%s,'city') RETURNING *""", (vk_id, name, INITIAL_HEALTH, INITIAL_ATTACK, INITIAL_MONEY))
            return cur.fetchone()

    def update_player(self, vk_id, **kwargs):
        if not kwargs:
            return
        set_clause = ",".join([f"{k}=%s" for k in kwargs.keys()])
        values = list(kwargs.values()) + [vk_id]
        with self.conn.cursor() as cur:
            cur.execute(f"UPDATE players SET {set_clause},last_activity=CURRENT_TIMESTAMP WHERE vk_id=%s", values)

    def player_exists(self, vk_id):
        with self.conn.cursor() as cur:
            cur.execute("SELECT 1 FROM players WHERE vk_id=%s", (vk_id,))
            return cur.fetchone() is not None

    def get_item(self, item_id):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM items WHERE id=%s", (item_id,))
            return cur.fetchone()

    def get_inventory(self, vk_id):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""SELECT pi.*,i.name,i.icon,i.type,i.effect,i.stats FROM player_inventory pi
                JOIN items i ON pi.item_id=i.id WHERE pi.vk_id=%s ORDER BY pi.slot_number""", (vk_id,))
            return cur.fetchall()

    def add_item(self, vk_id, item_id, count=1):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM player_inventory WHERE vk_id=%s AND item_id=%s AND is_equipped=FALSE", (vk_id, item_id))
            existing = cur.fetchone()
            if existing:
                cur.execute("UPDATE player_inventory SET count=count+%s WHERE id=%s", (count, existing['id']))
            else:
                cur.execute("SELECT COALESCE(MAX(slot_number),-1)+1 AS next_slot FROM player_inventory WHERE vk_id=%s", (vk_id,))
                result = cur.fetchone()
                next_slot = result['next_slot'] if result else 0
                if next_slot >= 16:
                    return False
                cur.execute("INSERT INTO player_inventory (vk_id,item_id,slot_number,count) VALUES (%s,%s,%s,%s)", (vk_id, item_id, next_slot, count))
            return True

    def remove_item(self, vk_id, item_id, count=1):
        with self.conn.cursor() as cur:
            cur.execute("UPDATE player_inventory SET count=count-%s WHERE vk_id=%s AND item_id=%s AND is_equipped=FALSE AND count>=%s", (count, vk_id, item_id, count))
            if cur.rowcount > 0:
                cur.execute("DELETE FROM player_inventory WHERE vk_id=%s AND item_id=%s AND count<=0", (vk_id, item_id))
                return True
            return False

    def equip_item(self, vk_id, item_id):
        """Экипировать предмет (надеть)"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Проверяем, есть ли предмет в инвентаре
            cur.execute("SELECT * FROM player_inventory WHERE vk_id=%s AND item_id=%s AND count>0", (vk_id, item_id))
            item_row = cur.fetchone()
            if not item_row:
                return False, "Предмет не найден в инвентаре"

            # Получаем информацию о предмете
            cur.execute("SELECT * FROM items WHERE id=%s", (item_id,))
            item_info = cur.fetchone()
            if not item_info:
                return False, "Предмет не найден в базе"

            item_type = item_info['type']

            if item_type == "weapon":
                # Снимаем текущее оружие
                cur.execute("UPDATE player_inventory SET is_equipped=FALSE WHERE vk_id=%s AND item_id IN (SELECT id FROM items WHERE type='weapon')", (vk_id,))
                # Надеваем новое
                cur.execute("UPDATE player_inventory SET is_equipped=TRUE WHERE vk_id=%s AND item_id=%s", (vk_id, item_id))
                # Обновляем поле в players
                cur.execute("UPDATE players SET equipped_weapon=%s WHERE vk_id=%s", (item_id, vk_id))
                return True, f"Надето оружие: {item_info['name']}"

            elif item_type == "armor":
                # Снимаем текущую броню
                cur.execute("UPDATE player_inventory SET is_equipped=FALSE WHERE vk_id=%s AND item_id IN (SELECT id FROM items WHERE type='armor')", (vk_id,))
                # Надеваем новую
                cur.execute("UPDATE player_inventory SET is_equipped=TRUE WHERE vk_id=%s AND item_id=%s", (vk_id, item_id))
                # Обновляем поле в players
                cur.execute("UPDATE players SET equipped_armor=%s WHERE vk_id=%s", (item_id, vk_id))
                return True, f"Надето: {item_info['name']}"

            return False, "Предмет нельзя экипировать"

    def unequip_item(self, vk_id, item_type: str):
        """Снять экипированный предмет"""
        with self.conn.cursor() as cur:
            if item_type == "weapon":
                cur.execute("UPDATE player_inventory SET is_equipped=FALSE WHERE vk_id=%s AND item_id IN (SELECT id FROM items WHERE type='weapon')", (vk_id,))
                cur.execute("UPDATE players SET equipped_weapon=NULL WHERE vk_id=%s", (vk_id,))
                return True, "Оружие снято"
            elif item_type == "armor":
                cur.execute("UPDATE player_inventory SET is_equipped=FALSE WHERE vk_id=%s AND item_id IN (SELECT id FROM items WHERE type='armor')", (vk_id,))
                cur.execute("UPDATE players SET equipped_armor=NULL WHERE vk_id=%s", (vk_id,))
                return True, "Броня снята"
            return False, "Неизвестный тип"

    def get_equipped_items(self, vk_id):
        """Получить экипированные предметы игрока"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""SELECT pi.*, i.name, i.type, i.stats FROM player_inventory pi
                JOIN items i ON pi.item_id = i.id 
                WHERE pi.vk_id = %s AND pi.is_equipped = TRUE""", (vk_id,))
            return cur.fetchall()


db = Database()
