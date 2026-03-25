` tags with the edit from the `<edit>` tags. Looking at the format, I need to find where the edit snippets go in the original code.

The edit shows:
```
// S.T.A.L.K.E.R. - Инвентарь Mini App

const app = {
    // API URL бота
    apiUrl: 'https://your-domain.com/api',

    // Данные игрока
    player: {
...
```

This replaces the entire code block. Looking at the original code:
- It starts with `// S.T.A.L.K.E.R. - Инвентарь Mini App`
- Then `const app = {`
- Then `// Данные игрока`
- Then `player: {`

The edit adds:
1. A new `apiUrl` property at the beginning of `app`
2. Changes `// Данные игрока` to still be there, but adds `apiUrl` before it
3. Updates the `items` object with more items and prices
4. Completely rewrites the methods

Looking at the edit more carefully:
- It adds `apiUrl: 'https://your-domain.com/api',` after `const app = {`
- It changes `// Данные игрока` to still have `player:` after it
- It adds new items to the `items` object with prices
- It rewrites `init()`, `getVKUser()` is replaced with `getVKIdFromURL()` and `loadData()`
- It adds new methods like `loadFromAPI()`, `useItem()`, `useItemLocal()`
- It modifies `renderInventory()`, `showItemModal()` to add usage buttons

Wait, I need to look at this more carefully. The edit seems to be a complete replacement. Let me check if the edit is a full replacement or partial.

Looking at the edit:
```
// S.T.A.L.K.E.R. - Инвентарь Mini App

const app = {
    // API URL бота
    apiUrl: 'https://your-domain.com/api',


```

I see the edit is inserting the `apiUrl` property right after the app object declaration, before the player data. This suggests a partial merge where I'm adding new properties and methods to the existing structure. The edit maintains the original code's core functionality while expanding its capabilities with API integration and additional item management.

The key changes involve:
- Adding an API endpoint
- Updating item definitions with pricing
- Replacing initialization and user retrieval methods
- Introducing new methods for data loading and item usage

This approach allows for seamless integration of new features without completely rewriting the existing code.

```


<code>
// S.T.A.L.K.E.R. - Инвентарь Mini App

const app = {
    // API URL бота
    apiUrl: 'https://your-domain.com/api',

    // Данные игрока
    player: {
        vk_id: null,
        name: 'Stalker',
        level: 1,
        health: 100,
        maxHealth: 100,
        fatigue: 0,
        maxFatigue: 100,
        money: 100
    },

    // Инвентарь (слоты)
    inventory: [],

    // Предметы (fallback если нет API)
    items: {
        'medkit': {
            id: 'medkit',
            name: 'Аптечка',
            icon: '🩹',
            description: 'Стандартная медицинская аптечка. Восстанавливает 50 здоровья.',
            type: 'consumable',
            price: 50,
            effect: { health: 50 }
        },
        'bandage': {
            id: 'bandage',
            name: 'Бинт',
            icon: '🩹',
            description: 'Простой бинт. Восстанавливает 20 здоровья.',
            type: 'consumable',
            price: 25,
            effect: { health: 20 }
        },
        'energy_drink': {
            id: 'energy_drink',
            name: 'Энергетик',
            icon: '⚡',
            description: 'Энергетический напиток. Снижает усталость на 30.',
            type: 'consumable',
            price: 30,
            effect: { fatigue: -30 }
        },
        'bread': {
            id: 'bread',
            name: 'Хлеб',
            icon: '🍞',
            description: 'Чёрствый хлеб. Сытно и дешево.',
            type: 'food',
            price: 20,
            effect: { fatigue: -20 }
        },
        'water': {
            id: 'water',
            name: 'Вода',
            icon: '💧',
            description: 'Бутылка чистой воды.',
            type: 'food',
            price: 10,
            effect: { fatigue: -10 }
        },
        'ammo_5x45': {
            id: 'ammo_5x45',
            name: 'Патроны 5.45',
            icon: '📦',
            description: 'Магазин патронов 5.45x39 для автомата.',
            type: 'ammo',
            price: 60,
            count: 30
        },
        'ammo_9x18': {
            id: 'ammo_9x18',
            name: 'Патроны 9x18',
            icon: '📦',
            description: 'Магазин патронов 9x18 для пистолета.',
            type: 'ammo',
            price: 30,
            count: 12
        },
        'pm': {
            id: 'pm',
            name: 'ПМ',
            icon: '🔫',
            description: 'Пистолет Макарова. Лёгкий и компактный.',
            type: 'weapon',
            price: 200,
            stats: { damage: 15, fireRate: 5 }
        },
        'ak74': {
            id: 'ak74',
            name: 'АК-74',
            icon: '🔫',
            description: 'Автомат Калашникова. Надёжная классика.',
            type: 'weapon',
            price: 500,
            stats: { damage: 35, fireRate: 10 }
        },
        'tos': {
            id: 'tos',
            name: 'ТОС-34',
            icon: '🔥',
            description: 'Огнемёт. Уничтожает всё живое.',
            type: 'weapon',
            price: 1200,
            stats: { damage: 60, fireRate: 3 }
        },
        'armor_vest': {
            id: 'armor_vest',
            name: 'Бронежилет',
            icon: '🦺',
            description: 'Стандартный бронежилет. Защищает от пуль.',
            type: 'armor',
            price: 300,
            stats: { defense: 30 }
        },
        'stalker_armor': {
            id: 'stalker_armor',
            name: 'Комбинезон сталкера',
            icon: '🥋',
            description: 'Спецкостюм сталкера. Защита +50.',
            type: 'armor',
            price: 800,
            stats: { defense: 50, radiation: -10 }
        },
        'artifact_blood': {
            id: 'artifact_blood',
            name: 'Кровь камня',
            icon: '💎',
            description: 'Артефакт аномалии «Кровь». Ускоряет регенерацию.',
            type: 'artifact',
            price: 500,
            stats: { healthRegen: 5 }
        },
        'artifact_eye': {
            id: 'artifact_eye',
            name: 'Око',
            icon: '👁️',
            description: 'Артефакт «Око». Светится в темноте.',
            type: 'artifact',
            price: 400,
            stats: { vision: 10 }
        },
        'artifact_meat': {
            id: 'artifact_meat',
            name: 'Мясо',
            icon: '🫀',
            description: 'Съедобный артефакт. Восстанавливает силы.',
            type: 'artifact',
            price: 150,
            effect: { fatigue: -40, health: 10 }
        }
    },

    // Инициализация
    init() {
        console.log('S.T.A.L.K.E.R. Inventory App init');
        
        // Получаем VK ID из URL
        this.getVKIdFromURL();

        // Пытаемся получить данные
        this.loadData();

        // Показываем главный экран после загрузки
        setTimeout(() => {
            this.showMainScreen();
        }, 800);
    },

    // Получить VK ID из URL параметров
    getVKIdFromURL() {
        const params = new URLSearchParams(window.location.search);
        const vkUserId = params.get('vk_user_id');
        if (vkUserId) {
            this.player.vk_id = parseInt(vkUserId);
            console.log('VK User ID:', this.player.vk_id);
        }
    },

    // Загрузка данных с API или локально
    async loadData() {
        if (this.player.vk_id) {
            try {
                // Пытаемся загрузить с API
                await this.loadFromAPI();
            } catch (e) {
                console.log('API not available, using test data');
                this.loadTestData();
            }
        } else {
            // Тестовый режим
            this.loadTestData();
        }
    },

    // Загрузка с API бота
    async loadFromAPI() {
        const response = await fetch(`${this.apiUrl}/player/${this.player.vk_id}`);
        if (!response.ok) throw new Error('API error');

        const data = await response.json();

        this.player = {
            vk_id: data.vk_id,
            name: data.name,
            level: data.level,
            health: data.health,
            maxHealth: 100,
            fatigue: data.fatigue,
            maxFatigue: 100,
            money: data.money
        };

        // Загружаем инвентарь
        if (data.inventory) {
            this.inventory = data.inventory.map(item => ({
                itemId: item.item_id,
                count: item.count
            }));

            // Дополняем до 16 слотов
            while (this.inventory.length < 16) {
                this.inventory.push(null);
            }
        } else {
            this.loadTestData();
        }
    },

    // Тестовые данные для разработки
    loadTestData() {
        this.player = {
            vk_id: 123456,
            name: 'Stalker_01',
            level: 3,
            health: 75,
            maxHealth: 100,
            fatigue: 35,
            maxFatigue: 100,
            money: 450
        };

        // Заполняем инвентарь тестовыми предметами
        this.inventory = [
            { itemId: 'medkit', count: 3 },
            { itemId: 'bandage', count: 5 },
            { itemId: 'energy_drink', count: 2 },
            { itemId: 'bread', count: 4 },
            { itemId: 'ammo_5x45', count: 2 },
            { itemId: 'ammo_9x18', count: 1 },
            { itemId: 'ak74', count: 1 },
            null, null, null, null, null,
            { itemId: 'artifact_blood', count: 1 }
        ];

        // Дополняем до 16 слотов
        while (this.inventory.length < 16) {
            this.inventory.push(null);
        }

        this.render();
    },

    // Показать главный экран
    showMainScreen() {
        document.getElementById('loading').classList.add('hidden');
        document.getElementById('main').classList.remove('hidden');
        this.render();
    },

    // Обновить данные
    refreshData() {
        // Анимация загрузки
        const btn = event.target;
        btn.textContent = '⏳ Загрузка...';
        
        setTimeout(async () => {
            btn.textContent = '🔄 Обновить';
            await this.loadData();
        }, 500);
    },

    // Использовать предмет
    async useItem(itemId) {
        const item = this.items[itemId];
        if (!item) return;

        // Проверяем эффект
        if (item.effect) {
            if (item.effect.health && this.player.health >= this.player.maxHealth) {
                alert('Здоровье уже полное!');
                return;
            }
            if (item.effect.fatigue && this.player.fatigue <= 0) {
                alert('Вы не устали!');
                return;
            }
        }

        // Пытаемся использовать через API
        if (this.player.vk_id) {
            try {
                const response = await fetch(`${this.apiUrl}/use_item`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        vk_id: this.player.vk_id,
                        item_id: itemId
                    })
                });

                if (response.ok) {
                    const result = await response.json();
                    this.player = result.player;
                    this.render();
                    alert(result.message);
                } else {
                    alert('Не удалось использовать предмет');
                }
            } catch (e) {
                // Локальное использование для теста
                this.useItemLocal(itemId);
            }
        } else {
            this.useItemLocal(itemId);
        }
    },

    // Локальное использование предмета (для теста)
    useItemLocal(itemId) {
        const item = this.items[itemId];
        if (!item) return;

        let message = '';

        // Применяем эффект
        if (item.effect) {
            if (item.effect.health) {
                const oldHealth = this.player.health;
                this.player.health = Math.min(this.player.maxHealth, this.player.health + item.effect.health);
                message += `❤️ +${this.player.health - oldHealth} здоровья\n`;
            }
            if (item.effect.fatigue) {
                const oldFatigue = this.player.fatigue;
                this.player.fatigue = Math.max(0, this.player.fatigue + item.effect.fatigue);
                message += `🔋 ${this.player.fatigue - oldFatigue} усталости\n`;
            }
        }

        // Удаляем предмет из инвентаря
        const slotIndex = this.inventory.findIndex(slot => slot && slot.itemId === itemId);
        if (slotIndex !== -1) {
            this.inventory[slotIndex].count--;
            if (this.inventory[slotIndex].count <= 0) {
                this.inventory[slotIndex] = null;
            }
        }

        this.render();
        alert(`✅ Использовано: ${item.name}\n\n${message}`);
    },

    // Рендерить интерфейс
    render() {
        this.renderStats();
        this.renderInventory();
        this.renderEquipment();
    },

    // Рендер статистики
    renderStats() {
        document.getElementById('player-name').textContent = this.player.name;
        document.getElementById('player-level').textContent = `Lv.${this.player.level}`;
        
        document.getElementById('health-value').textContent = `${this.player.health}/${this.player.maxHealth}`;
        document.getElementById('health-bar').style.width = `${(this.player.health / this.player.maxHealth) * 100}%`;
        
        document.getElementById('fatigue-value').textContent = `${this.player.fatigue}/${this.player.maxFatigue}`;
        document.getElementById('fatigue-bar').style.width = `${(this.player.fatigue / this.player.maxFatigue) * 100}%`;
        
        document.getElementById('money-value').textContent = this.player.money;
    },

    // Рендер инвентаря
    renderInventory() {
        const grid = document.getElementById('inventory-grid');
        grid.innerHTML = '';

        for (let i = 0; i < 16; i++) {
            const slot = document.createElement('div');
            slot.className = 'inv-slot';
            
            const item = this.inventory[i];
            if (item && this.items[item.itemId]) {
                const itemData = this.items[item.itemId];
                slot.innerHTML = `
                    <span>${itemData.icon}</span>
                    ${item.count > 1 ? `<span class="count">${item.count}</span>` : ''}
                `;
                slot.onclick = () => this.showItemModal(item.itemId);
            } else {
                slot.className += ' empty';
                slot.innerHTML = '-';
            }
            
            grid.appendChild(slot);
        }
    },

    // Рендер экипировки
    renderEquipment() {
        // Пока пусто - можно будет добавить экипированные предметы
        document.getElementById('slot-weapon').textContent = this.items['ak74']?.icon || '-';
        document.getElementById('slot-armor').textContent = this.items['armor_vest']?.icon || '-';
        document.getElementById('slot-medkit').textContent = this.items['medkit']?.icon || '-';
        document.getElementById('slot-food').textContent = this.items['bread']?.icon || '-';
    },

    // Показать модальное окно предмета
    showItemModal(itemId) {
        const item = this.items[itemId];
        if (!item) return;

        document.getElementById('modal-title').textContent = item.name;
        document.getElementById('modal-icon').textContent = item.icon;
        document.getElementById('modal-desc').textContent = item.description;

        // Показываем статы
        let statsHtml = '';

        if (item.price) {
            statsHtml += `<div>💰 Цена: ${item.price} руб.</div>`;
        }

        if (item.stats) {
            if (item.stats.damage) statsHtml += `<div>⚔️ Урон: ${item.stats.damage}</div>`;
            if (item.stats.defense) statsHtml += `<div>🛡️ Защита: ${item.stats.defense}</div>`;
            if (item.stats.fireRate) statsHtml += `<div>🔥 Скорость: ${item.stats.fireRate}</div>`;
        }
        if (item.effect) {
            if (item.effect.health) statsHtml += `<div>❤️ Лечение: +${item.effect.health}</div>`;
            if (item.effect.fatigue) statsHtml += `<div>🔋 Усталость: ${item.effect.fatigue > 0 ? '+' : ''}${item.effect.fatigue}</div>`;
        }
        
        document.getElementById('modal-stats').innerHTML = statsHtml || '<div>Обычный предмет</div>';

        // Кнопка использования для расходуемых предметов
        const footer = document.querySelector('.modal-footer');
        if (item.type === 'consumable' || item.type === 'food') {
            footer.innerHTML = `
                <button class="btn btn-primary" onclick="app.useItem('${itemId}')">✅ Использовать</button>
                <button class="btn btn-secondary" onclick="app.closeModal()">Закрыть</button>
            `;
        } else {
            footer.innerHTML = `
                <button class="btn btn-secondary" onclick="app.closeModal()">Закрыть</button>
            `;
        }

        document.getElementById('item-modal').classList.remove('hidden');
    },

    // Закрыть модальное окно
    closeModal() {
        document.getElementById('item-modal').classList.add('hidden');
    },

    // Открыть диалог инвентаря
    openItemDialog() {
        // Здесь можно открыть более подробный инвентарь
        alert('Полный инвентарь скоро будет доступен!');
    }
};

// Запуск при загрузке
document.addEventListener('DOMContentLoaded', () => {
    app.init();
});
