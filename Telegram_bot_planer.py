from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F
from aiogram.types import CallbackQuery
import asyncio

# Список стран для выбора
countries = {
    "Испания": ["Барселона", "Мадрид", "Валенсия"],
    "Италия": ["Рим", "Венеция", "Флоренция"],
    "Франция": ["Париж", "Ницца", "Лион"],
    "Греция": ["Афины", "Санторини", "Крит"],
    "Таиланд": ["Бангкок", "Пхукет", "Ко Самуи"],
}

# Инициализация бота и диспетчера
API_TOKEN = "Api_Token"  # Укажите свой токен
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Стартовая команда
@dp.message(F.text == "/start")
async def start(message: types.Message):
    await message.answer(
        "Привет! Я помогу тебе выбрать курорт. Выбери страну:",
        reply_markup=generate_country_keyboard(),
    )

# Генерация клавиатуры для выбора страны
def generate_country_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for country in countries.keys():
        keyboard.button(text=country, callback_data=country)
    return keyboard.as_markup()

# Обработка выбора страны
@dp.callback_query(F.data.in_(countries.keys()))
async def country_selection(callback_query: CallbackQuery):
    country_name = callback_query.data
    keyboard = InlineKeyboardBuilder()
    for city in countries[country_name]:
        keyboard.button(text=city, callback_data=f"{country_name}-{city}")

    await callback_query.message.edit_text(
        text=f"Вы выбрали {country_name}. Теперь выбери курорт:",
        reply_markup=keyboard.as_markup(),
    )

# Обработка выбора города
@dp.callback_query(F.data.contains("-"))
async def city_selection(callback_query: CallbackQuery):
    country_name, city_name = callback_query.data.split("-")
    await callback_query.message.edit_text(
        text=f"Вы выбрали курорт {city_name} в {country_name}. Отличный выбор!"
    )

# Основная функция для запуска бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
