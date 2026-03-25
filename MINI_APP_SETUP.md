# 🚀 ЗАПУСК MINI APP VK

## Вариант 1: GitHub Pages (бесплатно)

### 1. Загрузи на GitHub
```bash
# Создай репозиторий на GitHub и пушни:
git init
git add .
git commit -m "S.T.A.L.K.E.R. Mini App"
git remote add origin https://github.com/YOUR_USERNAME/stalker-bot.git
git push -u origin master
```

### 2. Включи GitHub Pages
- Репозиторий → Settings → Pages
- Source: **main branch**
- Save

### 3. Получишь ссылку типа:
```
https://твой-никнейм.github.io/stalker-bot/mini_app/
```

---

## Вариант 2: Создание Mini App в VK

### 1. Перейди в VK Developer
https://vk.com/apps?act=manage

### 2. Нажми "Создать приложение"
- Название: **S.T.A.L.K.E.R. Инвентарь**
- Тип: **Mini App**
- Платформа: **Веб-сайт**

### 3. В настройках:
- **Адрес сайта:** `https://твой-хостинг/mini_app/`
- **Базовый домен:** `твой-хостинг.com`

### 4. Получи App ID

---

## Вариант 3: Локальный тест (ngrok)

```bash
# Установи ngrok
# Скачай с https://ngrok.com/

# Запусти простой сервер в папке mini_app:
cd mini_app
python -m http.server 8000

# В другом терминале:
ngrok http 8000

# Получишь HTTPS ссылку — её можно использовать как Mini App URL
```

---

## После получения ссылки:

1. Обнови `.env` файл:
```env
MINI_APP_URL=https://твой-хостинг/mini_app/
```

2. В боте нажмут "Инвентарь" → получат ссылку на Mini App

---

## Тест без хостинга

Пока нет хостинга, открой файл напрямую:
```
stalker_bot/mini_app/index.html
```

Работает в браузере с тестовыми данными!
