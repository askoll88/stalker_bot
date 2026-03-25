# Bot config
import os
from dotenv import load_dotenv

load_dotenv()

# VK group token
VK_TOKEN = os.getenv("VK_TOKEN", "YOUR_VK_TOKEN_HERE")

# VK group ID
GROUP_ID = int(os.getenv("GROUP_ID", "0"))

# Mini App URL
MINI_APP_URL = "https://askoll88.github.io/stalker_bot/mini_app/"

# VK Mini App ID
VK_APP_ID = "54505998"

# PostgreSQL config
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "database": os.getenv("DB_NAME", "stalker_bot"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres")
}

# Game settings
INITIAL_HEALTH = 100
INITIAL_ATTACK = 10
INITIAL_FATIGUE = 0
INITIAL_EXP = 0
INITIAL_MONEY = 100
EXP_TO_LEVEL = 100
MAX_FATIGUE = 100
FATIGUE_PER_ACTION = 10
HEAL_COST = 50
