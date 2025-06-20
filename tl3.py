                                                                                                                                                                                                                                                                         tl3.py                                                                                                                                                                                                                                                                                    
import asyncio
import subprocess
import sys
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from data import get_data, count_free_numbers  # Импортируем функции из data.py

TOKEN = ""

# Создаём бота и диспетчер
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Создаем клавиатуру с кнопками
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="1️⃣ 1")],  # Первая кнопка (работает)
        [KeyboardButton(text="2️⃣ 2")],  # Вторая кнопка (запуск data1.py)
    ],
    resize_keyboard=True
)

# Обработчик команды /start
async def start_command(message: types.Message):
    await message.answer("⬇️ Выберите действие:", reply_markup=keyboard)

# Обработчик кнопки "1️⃣ 1" (основной скрипт)
async def button_1_response(message: types.Message):
    data = get_data()  # Получаем данные
    country_counts = count_free_numbers(data)  # Подсчитываем количество номеров
    result_message = "\n".join([f"{country}: {count}" for country, count in country_counts.items()])  # Формируем сообщение
    await message.answer(f"📊:\n{result_message}")

# Обработчик кнопки "2️⃣ 2" (запуск data1.py)
async def button_2_response(message: types.Message):
    # Запускаем data1.py через sys.executable, чтобы избежать проблем с путями
    result = subprocess.run([sys.executable, "data1.py"], capture_output=True, text=True)
    output = result.stdout.strip()

    # Если есть вывод от скрипта, отправляем его
    if output:
        await message.answer(f"📊 Данные из data1.py:\n{output}")

# Регистрируем обработчики
dp.message(Command("start"))(start_command)
dp.message(lambda message: message.text == "1️⃣ 1")(button_1_response)
dp.message(lambda message: message.text == "2️⃣ 2")(button_2_response)

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
