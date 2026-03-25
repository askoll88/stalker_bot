"""Работа с базой данных PostgreSQL"""
import psycopg2
from psycopg2.extras import RealDictCursor
from config import DB_CONFIG


class Database:
    def __init__(self):
        self.conn = None
        self.connect()
        self.init_tables()

    def connect(self):
        """Подключение к БД"""
        self.conn = psycopg2.connect(**DB_CONFIG)
        self.conn.autocommit = True

    def init_tables(self):
        """Создание таблиц"""
        with self.conn.cursor() as cur:
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


db = Database()
