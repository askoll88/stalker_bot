"""Database working with PostgreSQL"""
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
        """Connect to database"""
        self.conn = psycopg2.connect(**DB_CONFIG)
        self.conn.autocommit = True

    def init_tables(self):
        """Create tables"""
        with self.conn.cursor() as cur:
            # Players table
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
            
            # Items table
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
            
            # Player inventory table
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
        """Add items to database"""
        items = [
            # Medicine
            ("medkit", "Medkit", "Standard medkit. Restores 50 HP.", "🩹", "consumable", 50, 
             '{"health": 50}', None),
            ("bandage", "Bandage", "Simple bandage. Restores 20 HP.", "🩹", "consumable", 25, 
             '{"health": 20}', None),
            ("energy_drink", "Energy Drink", "Reduces fatigue by 30.", "⚡", "consumable", 30, 
             '{"fatigue": -30}', None),
            
            # Food
            ("bread", "Bread", "Satisfying bread. Reduces fatigue by 20.", "🍞", "food", 20, 
             '{"fatigue": -20}', None),
            ("water", "Water", "Bottle of clean water.", "💧", "food", 10, 
             '{"fatigue": -10}', None),
            
            # Weapons
            ("pm", "PM Pistol", "Makarov pistol. Compact and reliable.", "🔫", "weapon", 200, 
             None, '{"damage": 15, "fireRate": 5}'),
            ("ak74", "AK-74", "Kalashnikov rifle. Classic.", "🔫", "weapon", 500, 
             None, '{"damage": 35, "fireRate": 10}'),
            ("tos", "TOS-34", "Flamethrower. Destroys everything.", "🔥", "weapon", 1200, 
             None, '{"damage": 60, "fireRate": 3}'),
            
            # Armor
            ("armor_vest", "Armor Vest", "Standard armor. Defense +30.", "🦺", "armor", 300, 
             None, '{"defense": 30}'),
            ("stalker_armor", "Stalker Suit", "Special suit. Defense +50.", "🥋", "armor", 800, 
             None, '{"defense": 50, "radiation": -10}'),
            
            # Ammo
            ("ammo_9x18", "Ammo 9x18", "Magazine for PM. 12 rounds.", "📦", "ammo", 30, 
             None, None),
            ("ammo_5x45", "Ammo 5.45", "Magazine for AK-74. 30 rounds.", "📦", "ammo", 60, 
             None, None),
            
            # Artifacts
            ("artifact_blood", "Blood of Stone", "Artifact 'Blood'. Regen +5.", "💎", "artifact", 500, 
             None, '{"healthRegen": 5}'),
            ("artifact_eye", "Eye", "Artifact 'Eye'. Night vision.", "👁️", "artifact", 400, 
             None, '{"vision": 10}'),
            ("artifact_meat", "Meat", "Edible artifact.", "🫀", "artifact", 150, 
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
        """Get player by VK ID"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM players WHERE vk_id = %s", (vk_id,))
            return cur.fetchone()

    def create_player(self, vk_id: int, name: str):
        """Create new player"""
        from config import INITIAL_HEALTH, INITIAL_ATTACK, INITIAL_MONEY
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                INSERT INTO players (vk_id, name, health, attack, money, current_location)
                VALUES (%s, %s, %s, %s, %s, 'city')
                RETURNING *
            """, (vk_id, name, INITIAL_HEALTH, INITIAL_ATTACK, INITIAL_MONEY))
            return cur.fetchone()

    def update_player(self, vk_id: int, **kwargs):
        """Update player data"""
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
        """Check if player exists"""
        with self.conn.cursor() as cur:
            cur.execute("SELECT 1 FROM players WHERE vk_id = %s", (vk_id,))
            return cur.fetchone() is not None

    def get_item(self, item_id: str):
        """Get item by ID"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM items WHERE id = %s", (item_id,))
            return cur.fetchone()

    def get_inventory(self, vk_id: int):
        """Get player inventory"""
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
        """Add item to inventory"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Check if item already exists
            cur.execute("""
                SELECT * FROM player_inventory 
                WHERE vk_id = %s AND item_id = %s AND is_equipped = FALSE
            """, (vk_id, item_id))
            existing = cur.fetchone()
            
            if existing:
                # Increase count
                cur.execute("""
                    UPDATE player_inventory 
                    SET count = count + %s
                    WHERE id = %s
                """, (count, existing['id']))
            else:
                # Find free slot
                cur.execute("""
                    SELECT COALESCE(MAX(slot_number), -1) + 1 as next_slot 
                    FROM player_inventory WHERE vk_id = %s
                """, (vk_id,))
                next_slot = cur.fetchone()['next_slot']
                
                if next_slot >= 16:
                    return False  # Inventory full
                
                # Add new item
                cur.execute("""
                    INSERT INTO player_inventory (vk_id, item_id, slot_number, count)
                    VALUES (%s, %s, %s, %s)
                """, (vk_id, item_id, next_slot, count))
            
            return True

    def remove_item(self, vk_id: int, item_id: str, count: int = 1) -> bool:
        """Remove item from inventory"""
        with self.conn.cursor() as cur:
            cur.execute("""
                UPDATE player_inventory 
                SET count = count - %s
                WHERE vk_id = %s AND item_id = %s AND is_equipped = FALSE
                AND count >= %s
            """, (count, vk_id, item_id, count))
            
            if cur.rowcount > 0:
                # Delete if 0
                cur.execute("""
                    DELETE FROM player_inventory 
                    WHERE vk_id = %s AND item_id = %s AND count <= 0
                """, (vk_id, item_id))
                return True
            return False


db = Database()
