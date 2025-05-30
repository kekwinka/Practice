from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text

API_TOKEN = '7792032422:AAGUJAbT7VOt_E3zHdCG-tWkGbqRXckpbxY'

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

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
