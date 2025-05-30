#  Руководство по созданию Telegram-бота для записи к мастеру ногтевого сервиса

##  Описание проекта

Данный проект представляет собой Telegram-бота, созданного с использованием библиотеки **Aiogram** (версия `2.25.2`).  
Бот предназначен для записи клиентов на услуги ногтевого сервиса к **одному мастеру**. Он предоставляет пользователю возможность:

- Выбрать услугу
- Выбрать удобную дату и время
- Подтвердить запись
- Вернуться в главное меню
- Перенести или отменить запись

Бот работает как цифровой помощник, позволяя клиенту легко взаимодействовать с мастером через Telegram, минимизируя ручную работу и ускоряя процесс записи.


## Этапы исследования и создания технологии

### 1. Изучение предметной области

- Анализ потребностей мастеров в автоматизации записи клиентов
- Сбор требований к функциональности: список услуг, временные слоты, подтверждение записи, возможность отмены или переноса
- Изучение существующих решений и ботов в сфере бьюти-индустрии

### 2. Проектирование логики взаимодействия

- Сценарии: `старт → выбор услуги → выбор даты и времени → подтверждение → главное меню`
- Добавлены возможности возврата в главное меню, отмены и переноса записи

### 3. Выбор инструментов

- Язык программирования: `Python 3.10+`
- Фреймворк: `Aiogram 2.25.2`
- Telegram Bot API
- Хранилище состояний: `MemoryStorage`

---

##  Установка и настройка

### 1. Регистрация бота через @BotFather

- Найти в Telegram бота `@BotFather`
- Отправить команду `/newbot`
- Задать имя и username
- Получить и сохранить токен API

### 2. Установка зависимостей

```bash
pip install aiogram==2.25.2
````

### 3. Структура проекта

```
project/
├── bot.py
├── config.py
└── handlers.py
```

### 4. Пример конфигурации (`config.py`)

```python
API_TOKEN = 'ВАШ_ТОКЕН_ЗДЕСЬ'
```

---

##  Реализация логики бота (`bot.py`)

### Импорт библиотек и инициализация

```python
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from config import API_TOKEN

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
```

### Состояния FSM

```python
class Booking(StatesGroup):
    service = State()
    date = State()
    time = State()
```

### Главное меню

```python
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Записаться", "Отменить запись", "Перенести запись")
    await message.answer("Привет! Я бот мастера ногтевого сервиса. Чем могу помочь?", reply_markup=keyboard)
```

### Выбор услуги

```python
@dp.message_handler(lambda message: message.text == "Записаться")
async def choose_service(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Маникюр", "Педикюр", "Наращивание")
    await message.answer("Выберите услугу:", reply_markup=keyboard)
    await Booking.service.set()
```

### Дальнейшие шаги

(Добавляется логика аналогично выбору услуги: выбор даты, времени и подтверждение.)

---

##  Иллюстрации

### 1. Структура состояний бота

```
[Главное меню] → [Выбор услуги] → [Выбор даты] → [Выбор времени] → [Подтверждение]
```

---

### 2. Пример взаимодействия пользователя

```
Пользователь: /start
Бот: Привет! Чем могу помочь?
Кнопки: [Записаться] [Отменить запись] [Перенести запись]
```

---

### 3. Схема логики FSM:

```text
StatesGroup: Booking
 ├── service
 ├── date
 └── time
```

---

##  Полный код и документация

Доступны в репозитории:
 [GitHub — Practice Telegram Bot](https://github.com/kekwinka/Practice/blob/main/src/main.py)

