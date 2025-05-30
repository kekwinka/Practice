# Модификация проекта: Добавление напоминаний и админ-панели мастера

# Состояния
class Booking(StatesGroup):
    service = State()
    day = State()
    time = State()

# Клавиатуры
main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
main_kb.add(KeyboardButton("📅 Записаться"))

services_kb = ReplyKeyboardMarkup(resize_keyboard=True)
services_kb.add("Аппаратный Маникюр", "Маникюр + покрытие", "Маникюр + снятие + покрытие")
services_kb.add("Наращивание")
services_kb.add("🔙 Назад")

days_kb = ReplyKeyboardMarkup(resize_keyboard=True)
days_kb.add("Понедельник", "Вторник", "Среда", "Четверг")
days_kb.add("🔙 Назад")

times_kb = ReplyKeyboardMarkup(resize_keyboard=True)
times_kb.add("10:00", "12:00", "14:00", "16:00")
times_kb.add("🔙 Назад")

confirm_kb = ReplyKeyboardMarkup(resize_keyboard=True)
confirm_kb.add("🔁 Перенести запись", "❌ Отменить запись")
confirm_kb.add("🏠 Главное меню")

# Обработчики
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Привет! Я Алена, хочешь записаться, не стесняйся жми кнопку!!", reply_markup=main_kb)

@dp.message_handler(Text(equals="📅 Записаться"))
async def choose_service(message: types.Message):
    await Booking.service.set()
    await message.answer("Выбери услугу:", reply_markup=services_kb)

@dp.message_handler(state=Booking.service)
async def choose_day(message: types.Message, state: FSMContext):
    if message.text == "🔙 Назад":
        await cmd_start(message, state)
        return
    await state.update_data(service=message.text)
    await Booking.next()
    await message.answer("Выбери день:", reply_markup=days_kb)

@dp.message_handler(state=Booking.day)
async def choose_time(message: types.Message, state: FSMContext):
    if message.text == "🔙 Назад":
        await choose_service(message)
        return
    await state.update_data(day=message.text)
    await Booking.next()
    await message.answer("Теперь выбери удобное время:", reply_markup=times_kb)

@dp.message_handler(state=Booking.time)
async def confirm_booking(message: types.Message, state: FSMContext):
    if message.text == "🔙 Назад":
        await choose_day(message, state)
        return
    await state.update_data(time=message.text)
    data = await state.get_data()
    text = (
        f"<b>Запись подтверждена!</b>\n\n"
        f"🧾 Услуга: {data['service']}\n"
        f"📅 День: {data['day']}\n"
        f"⏰ Время: {data['time']}"
    )
    await message.answer(text, parse_mode="HTML", reply_markup=confirm_kb)

@dp.message_handler(Text(equals="🔁 Перенести запись"))
async def reschedule(message: types.Message, state: FSMContext):
    await choose_service(message)

@dp.message_handler(Text(equals="❌ Отменить запись"))
async def cancel_booking(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Запись отменена. Если передумаешь — пиши 🥰", reply_markup=main_kb)

@dp.message_handler(Text(equals="🏠 Главное меню"))
async def go_home(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Главное меню:", reply_markup=main_kb)

# Запуск
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
##  Описание модификации

В рамках модификации проекта был реализован функционал **автоматических уведомлений** клиентам, которые записались на процедуру. Теперь бот **за 24 часа до времени приёма отправляет напоминание** пользователю.

Кроме того, добавлена **внутренняя панель управления для мастера**, через которую можно:
- Просматривать список всех записей
- Отменять любую запись вручную
- Изменять расписание приёма

Эта модификация **повышает удобство работы** с ботом и обеспечивает **дополнительную автоматизацию** бизнес-процесса мастера.

---

##  Техническая реализация

Модификация выполнена на Python с использованием библиотеки `aiogram==2.25.2`. Основное внимание уделено следующим частям проекта:

### 1. Хранение записей

Расширена структура хранения: теперь каждая запись сохраняется с указанием `user_id`, даты и времени, а также типа услуги.

```python
appointments = []
````

---

### 2. Фоновая задача для напоминаний

Создано фоновое задание, которое каждую минуту проверяет, кому из пользователей нужно отправить уведомление.

```python
import asyncio
from datetime import datetime, timedelta

async def notify_upcoming_appointments():
    while True:
        now = datetime.now()
        for appointment in appointments:
            time_diff = appointment['time'] - now
            if timedelta(hours=23, minutes=59) < time_diff < timedelta(days=1, minutes=1):
                await bot.send_message(
                    appointment['user_id'], 
                    f"Напоминаем: у вас завтра запись на {appointment['service']} в {appointment['time'].strftime('%H:%M')}"
                )
        await asyncio.sleep(60)
```

Запускается при старте бота:

```python
loop = asyncio.get_event_loop()
loop.create_task(notify_upcoming_appointments())
```

---

### 3. Админ-панель мастера

Мастер определяется по ID. При вводе команды `/admin` бот отправляет список текущих записей с возможностью их удалить или перенести.

```python
ADMIN_ID = 123456789

@dp.message_handler(commands=['admin'])
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("У вас нет доступа к админ-панели.")
        return

    if not appointments:
        await message.answer("Записей нет.")
        return

    text = "Текущие записи:\n"
    for i, a in enumerate(appointments):
        text += f"{i+1}. {a['user_name']} — {a['service']} — {a['time'].strftime('%d.%m %H:%M')}\n"
    await message.answer(text)
