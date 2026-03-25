"""Работа с базой данных PostgreSQL"""
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
        """Подключение к БД"""
        self.conn = psycopg2.connect(**DB_CONFIG)
        self.conn.autocommit = True

    def init_tables(self):
        """Создание таблиц"""
        with self.conn.cursor() as cur:
            # Таблица игроков
            cur.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    vk_id BIGINT PRIMARY KEY,
                    name VARCHAR(100),
                    health INTEGER DEFAULT 100,
                    attack INTEGER DEFAULT 10,
                    fatigue INTEGER DEFAULT 0,
                    exp INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 1,
                    money INTEGER DEFAULT 100,
                    current_location VARCHAR(50) DEFAULT 'city',
                    shelter_unlocked BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Таблица предметов
            cur.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id VARCHAR(50) PRIMARY KEY,
                    name VARCHAR(100),
                    description TEXT,
                    icon VARCHAR(10),
                    type VARCHAR(50),
                    price INTEGER DEFAULT 0,
                    effect JSONB,
                    stats JSONB
                )
            """)

            # Таблица инвентаря игроков
            cur.execute("""
                CREATE TABLE IF NOT EXISTS player_inventory (
                    id SERIAL PRIMARY KEY,
                    vk_id BIGINT REFERENCES players(vk_id),
                    item_id VARCHAR(50) REFERENCES items(id),
                    slot_number INTEGER DEFAULT 0,
                    count INTEGER DEFAULT 1,
                    is_equipped BOOLEAN DEFAULT FALSE
                )
            """)

    def init_items(self):
        """Добавление предметов в БД"""
        items = [
            # Медицина
            ("medkit", "Аптечка", "Стандартная мед. аптечка. Восстанавливает 50 HP.", "🩹", "consumable", 50,
             '{"health": 50}', None),
            ("bandage", "Бинт", "Простой бинт. Восстанавливает 20 HP.", "🩹", "consumable", 25,
             '{"health": 20}', None),
            ("energy_drink", "Энергетик", "Снижает усталость на 30.", "⚡", "consumable", 30,
             '{"fatigue": -30}', None),

            # Еда
            ("bread", "Хлеб", "Сытный хлеб. Снижает усталость на 20.", "🍞", "food", 20,
             '{"fatigue": -20}', None),
            ("water", "Вода", "Бутылка воды.", "💧", "food", 10,
             '{"fatigue": -10}', None),

            # Оружие
            ("pm", "Пистолет ПМ", "Пистолет Макарова. Компактный и надёжный.", "🔫", "weapon", 200,
             None, '{"damage": 15, "fireRate": 5}'),
            ("ak74", "АК-74", "Автомат Калашникова. Классика сталкера.", "🔫", "weapon", 500,
             None, '{"damage": 35, "fireRate": 10}'),
            ("tos", "ТОС-34", "Огнемёт. Уничтожает всё живое.", "🔥", "weapon", 1200,
             None, '{"damage": 60, "fireRate": 3}'),

            # Броня
            ("armor_vest", "Бронежилет", "Стандартный бронежилет. Защита +30.", "🦺", "armor", 300,
             None, '{"defense": 30}'),
            ("stalker_armor", "Комбинезон сталкера", "Спецкостюм сталкера. Защита +50.", "🥋", "armor", 800,
             None, '{"defense": 50, "radiation": -10}'),

            # Патроны
            ("ammo_9x18", "Патроны 9x18", "Магазин для ПМ. 12 штук.", "📦", "ammo", 30,
             None, None),
            ("ammo_5x45", "Патроны 5.45", "Магазин для АК-74. 30 штук.", "📦", "ammo", 60,
             None, None),

            # Артефакты
            ("artifact_blood", "Кровь камня", "Артефакт «Кровь». Регенерация +5.", "💎", "artifact", 500,
             None, '{"healthRegen": 5}'),
            ("artifact_eye", "Око", "Артефакт «Око». Ночное зрение.", "👁️", "artifact", 400,
             None, '{"vision": 10}'),
            ("artifact_meat", "Мясо", "Съедобный артефакт.", "🫀", "artifact", 150,
             '{"fatigue": -40, "health": 10}', None),
        ]

        for item in items:
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO items (id, name, description, icon, type, price, effect, stats)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                """, item)

    def get_player(self, vk_id: int):
        """Получить игрока по VK ID"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM players WHERE vk_id = %s", (vk_id,))
            return cur.fetchone()

    def create_player(self, vk_id: int, name: str):
        """Создать нового игрока"""
        from config import INITIAL_HEALTH, INITIAL_ATTACK, INITIAL_MONEY
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                INSERT INTO players (vk_id, name, health, attack, money, current_location)
                VALUES (%s, %s, %s, %s, %s, 'city')
                RETURNING *
            """, (vk_id, name, INITIAL_HEALTH, INITIAL_ATTACK, INITIAL_MONEY))
            return cur.fetchone()

    def update_player(self, vk_id: int, **kwargs):
        """Обновить данные игрока"""
        if not kwargs:
            return
        set_clause = ", ".join([f"{key} = %s" for key in kwargs.keys()])
        values = list(kwargs.values())
        values.append(vk_id)
        with self.conn.cursor() as cur:
            cur.execute(f"""
                UPDATE players 
                SET {set_clause}, last_activity = CURRENT_TIMESTAMP
                WHERE vk_id = %s
            """, values)

    def player_exists(self, vk_id: int) -> bool:
        """Проверить существование игрока"""
        with self.conn.cursor() as cur:
            cur.execute("SELECT 1 FROM players WHERE vk_id = %s", (vk_id,))
            return cur.fetchone() is not None

    def get_item(self, item_id: str):
        """Получить предмет по ID"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM items WHERE id = %s", (item_id,))
            return cur.fetchone()

    def get_inventory(self, vk_id: int):
        """Получить инвентарь игрока"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT pi.*, i.name, i.icon, i.type, i.effect, i.stats
                FROM player_inventory pi
                JOIN items i ON pi.item_id = i.id
                WHERE pi.vk_id = %s
                ORDER BY pi.slot_number
            """, (vk_id,))
            return cur.fetchall()

    def add_item(self, vk_id: int, item_id: str, count: int = 1) -> bool:
        """Добавить предмет в инвентарь"""
        # Проверяем, есть ли уже такой предмет
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM player_inventory 
                WHERE vk_id = %s AND item_id = %s AND is_equipped = FALSE
            """, (vk_id, item_id))
            existing = cur.fetchone()

            if existing:
                # Увеличиваем количество
                cur.execute("""
                    UPDATE player_inventory 
                    SET count = count + %s
                    WHERE id = %s
                """, (count, existing['id']))
            else:
                # Находим свободный слот
                cur.execute("""
                    SELECT COALESCE(MAX(slot_number), -1) + 1 as next_slot 
                    FROM player_inventory WHERE vk_id = %s
                """, (vk_id,))
                next_slot = cur.fetchone()['next_slot']

                if next_slot >= 16:
                    return False  # Инвентарь полон

                # Добавляем новый предмет
                cur.execute("""
                    INSERT INTO player_inventory (vk_id, item_id, slot_number, count)
                    VALUES (%s, %s, %s, %s)
                """, (vk_id, item_id, next_slot, count))

            return True

    def remove_item(self, vk_id: int, item_id: str, count: int = 1) -> bool:
        """Удалить предмет из инвентаря"""
        with self.conn.cursor() as cur:
            cur.execute("""
                UPDATE player_inventory 
                SET count = count - %s
                WHERE vk_id = %s AND item_id = %s AND is_equipped = FALSE
                AND count >= %s
            """, (count, vk_id, item_id, count))

            if cur.rowcount > 0:
                # Удаляем если 0
                cur.execute("""
                    DELETE FROM player_inventory 
                    WHERE vk_id = %s AND item_id = %s AND count <= 0
                """, (vk_id, item_id))
                return True
            return False


db = Database()
