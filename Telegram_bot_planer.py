from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F
from aiogram.types import CallbackQuery
import asyncio

# Список стран и городов для выбора
countries = {
    "Турция": ["Анталья", "Стамбул", "Чешме"],
    "ОАЭ": ["Абу-Даби", "Аджман", "Шарджа"],
    "Куба": ["Камагуэй", "Лос-Канарреос", "Ольгин"],
    "Греция": ["Афины", "Санторини", "Крит"],
    "Таиланд": ["Бангкок", "Пхукет", "Ко Самуи"],
}

# Словарь с URL-адресами для каждого города
city_urls = {
    "Анталья": "https://tourvisor.ru/search.php#tvtourid=4693245657",
    "Стамбул": "=08.02.2025&s_j_date_to=17.02.2025&s_adults=2&s_flyfrom=1&s_country=2&s_currency=0&s_city=Стамбул",
    "Чешме": "Путёвки не найдены",
    "Абу-Даби": "https://tourvisor.ru/search.php?s_city=Барселона#tvtourid=4690386369",
    "Аджман": "https://tourvisor.ru/search.php?s_city=Барселона#tvtourid=4690387350",
    "Шарджа": "https://tourvisor.ru/search.php?s_city=Барселона#tvtourid=4690388556",
    "Камагуэй": "https://tourvisor.ru/search.php?s_city=%D0%9A%D0%B0%D0%BC%D0%B0%D0%B3%D1%83%D1%8D%D0%B9#tvtourid=4690376112",
    "Лос-Канарреос": "https://tourvisor.ru/search.php#tvtourid=4693220649",
    "Ольгин": "https:/`/tourvisor.ru/search.php?s_city=Барселона#tvtourid=4690382349",
    "Афины": "https://tourvisor.ru/search.php#tvtourid=4693233792",
    "Санторини": "Путёвки не найдены",
    "Крит": "https://tourvisor.ru/search.php#tvtourid=4693241637",
    "Бангкок": "Путёвки не найдены",
    "Пхукет": "08.02.2025&s_j_date_to=17.02.2025&s_adults=2&s_flyfrom=1&s_country=2&s_currency=0&s_city=Пхукет",
    "Ко Самуи": "https://tourvisor.ru/search.php#tvtourid=4693357236",
}

# Инициализация бота и диспетчера
API_TOKEN = "7783295762:AAHwh0C2DgalOVEvqzOnyDI9PekMtWGwwqw"  # Укажите свой токен
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
        keyboard.button(text=country, callback_data=f"country-{country}")
    keyboard.adjust(2)  # Adjust the number of buttons per row
    return keyboard.as_markup()


# Обработка выбора страны
@dp.callback_query(F.data.startswith("country-"))
async def country_selection(callback_query: CallbackQuery):
    country_name = callback_query.data.split("-")[1]
    keyboard = InlineKeyboardBuilder()
    for city in countries[country_name]:
        keyboard.button(text=city, callback_data=f"city-{country_name}-{city}")
    keyboard.button(text="Назад", callback_data="back-to-countries")
    keyboard.adjust(2)  # Adjust the number of buttons per row
    await callback_query.message.edit_text(
        text=f"Вы выбрали {country_name}. Теперь выбери курорт:",
        reply_markup=keyboard.as_markup(),
    )


# Обработка выбора города
@dp.callback_query(F.data.startswith("city-"))
async def city_selection(callback_query: CallbackQuery):
    _, country_name, city_name = callback_query.data.split("-")

    # Получаем ссылку на сайт с турами для выбранного города
    tour_link = city_urls.get(city_name, "Ссылка не найдена")

    # Отправляем ссылку пользователю
    await callback_query.message.edit_text(
        text=f"Вы выбрали курорт {city_name} в {country_name}. Вот ссылка на доступные туры:\n\n{tour_link}",
        disable_web_page_preview=True,  # Отключаем предпросмотр ссылки
    )


# Обработка нажатия на кнопку "Назад"
@dp.callback_query(F.data == "back-to-countries")
async def back_to_countries(callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        "Выбери страну:",
        reply_markup=generate_country_keyboard(),
    )


# Основная функция для запуска бота
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
