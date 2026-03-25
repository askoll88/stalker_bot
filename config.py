"""Конфигурация бота"""
import os
from dotenv import load_dotenv

load_dotenv()

# Токен VK группы
VK_TOKEN = os.getenv("VK_TOKEN", "YOUR_VK_TOKEN_HERE")

# ID группы VK
GROUP_ID = int(os.getenv("GROUP_ID", "0"))

# URL Mini App
MINI_APP_URL = "https://askoll88.github.io/stalker_bot/mini_app/"

# VK Mini App ID (получить в vk.com/apps?act=manage)
VK_APP_ID = os.getenv("VK_APP_ID", "0")

# Настройки базы данных PostgreSQL
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "database": os.getenv("DB_NAME", "stalker_bot"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres")
}

# Настройки игры
INITIAL_HEALTH = 100
INITIAL_ATTACK = 10
INITIAL_FATIGUE = 0
INITIAL_EXP = 0
INITIAL_MONEY = 100
EXP_TO_LEVEL = 100
MAX_FATIGUE = 100
FATIGUE_PER_ACTION = 10
HEAL_COST = 50
