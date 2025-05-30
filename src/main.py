from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
import asyncio
from datetime import datetime, timedelta

API_TOKEN = '7792032422:AAGUJAbT7VOt_E3zHdCG-tWkGbqRXckpbxY'
ADMIN_ID = 856435420

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

appointments = []  # Список записей

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

    # Сохраняем запись
    appointments.append({
        'user_id': message.from_user.id,
        'user_name': message.from_user.full_name,
        'service': data['service'],
        'day': data['day'],
        'time': datetime.strptime(f"{data['day']} {data['time']}", "%A %H:%M")  # Пример, нужно подогнать под реальные даты
    })

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
        text += f"{i+1}. {a['user_name']} — {a['service']} — {a['time'].strftime('%A %H:%M')}\n"
    await message.answer(text)

# Напоминания
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

# Запуск
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(notify_upcoming_appointments())
    executor.start_polling(dp, skip_updates=True)

