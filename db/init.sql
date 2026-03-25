-- Создание базы данных для S.T.A.L.K.E.R. бота

-- Создаем базу данных (выполнить в psql)
-- CREATE DATABASE stalker_bot;

-- Таблица игроков
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
);
