import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
import aiohttp
from datetime import datetime, timedelta
import json

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token='api-key')
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# API токен Travelpayouts
TRAVELPAYOUTS_TOKEN = "17ec4f9d498f71ae1b580ec256fe782c"
TRAVELPAYOUTS_MARKER = "605715" # Ваш маркер партнера

# Состояния FSM
class TourStates(StatesGroup):
    choosing_country = State()
    choosing_city = State()
    choosing_dates = State()
    choosing_hotel = State()

# Базовые данные о направлениях с описаниями
DESTINATIONS = {
    "Турция 🇹🇷": {
        "code": "TR",
        "description": "Страна с богатой историей, прекрасными пляжами и системой «все включено»",
        "cities": {
            "Анталья": {
                "code": "AYT",
                "description": "☀️ Популярный курорт с песчаными пляжами и роскошными отелями",
                "temp": "🌡️ +30°C летом, +15°C зимой",
                "flight": "⏰ Перелет: ~4 часа"
            },
            "Стамбул": {
                "code": "IST",
                "description": "🕌 Город на стыке Европы и Азии с богатым культурным наследием",
                "temp": "🌡️ +25°C летом, +8°C зимой",
                "flight": "⏰ Перелет: ~3.5 часа"
            },
            "Бодрум": {
                "code": "BJV",
                "description": "⛵ Элитный курорт с живописной набережной и яхт-клубами",
                "temp": "🌡️ +28°C летом, +12°C зимой",
                "flight": "⏰ Перелет: ~4 часа"
            },
            "Алания": {
                "code": "GZP",
                "description": "🏖️ Курорт с красивыми пляжами и доступными ценами",
                "temp": "🌡️ +32°C летом, +16°C зимой",
                "flight": "⏰ Перелет: ~4 часа"
            },
            "Кемер": {
                "code": "AYT",
                "description": "🌲 Курорт в окружении гор и соснового леса",
                "temp": "🌡️ +29°C летом, +14°C зимой",
                "flight": "⏰ Перелет: ~4 часа"
            }
        }
    },
    "ОАЭ 🇦🇪": {
        "code": "AE",
        "description": "Роскошный отдых в стране небоскребов и восточной сказки",
        "cities": {
            "Дубай": {
                "code": "DXB",
                "description": "🌆 Город будущего с самыми высокими небоскребами",
                "temp": "🌡️ +40°C летом, +25°C зимой",
                "flight": "⏰ Перелет: ~5.5 часов"
            },
            "Абу-Даби": {
                "code": "AUH",
                "description": "🕌 Столица ОАЭ с роскошными отелями и мечетями",
                "temp": "🌡️ +38°C летом, +24°C зимой",
                "flight": "⏰ Перелет: ~5.5 часов"
            },
            "Шарджа": {
                "code": "SHJ",
                "description": "🏺 Культурная столица ОАЭ с множеством музеев",
                "temp": "🌡️ +37°C летом, +23°C зимой",
                "flight": "⏰ Перелет: ~5.5 часов"
            }
        }
    },
    "Таиланд 🇹🇭": {
        "code": "TH",
        "description": "Страна улыбок, экзотической природы и древних храмов",
        "cities": {
            "Пхукет": {
                "code": "HKT",
                "description": "🏝️ Крупнейший остров с белоснежными пляжами",
                "temp": "🌡️ +32°C круглый год",
                "flight": "⏰ Перелет: ~9 часов"
            },
            "Бангкок": {
                "code": "BKK",
                "description": "🌆 Столица с храмами и ночными рынками",
                "temp": "🌡️ +33°C круглый год",
                "flight": "⏰ Перелет: ~8.5 часов"
            },
            "Паттайя": {
                "code": "UTP",
                "description": "🎉 Курорт с активной ночной жизнью",
                "temp": "🌡️ +31°C круглый год",
                "flight": "⏰ Перелет: ~9 часов"
            }
        }
    },
    "Египет 🇪🇬": {
        "code": "EG",
        "description": "Страна пирамид, круглогодичного солнца и Красного моря",
        "cities": {
            "Хургада": {
                "code": "HRG",
                "description": "🐠 Популярный курорт с отличным снорклингом",
                "temp": "🌡️ +35°C летом, +22°C зимой",
                "flight": "⏰ Перелет: ~5 часов"
            },
            "Шарм-эль-Шейх": {
                "code": "SSH",
                "description": "🏊‍♂️ Курорт с коралловыми рифами и дайвингом",
                "temp": "🌡️ +34°C летом, +21°C зимой",
                "flight": "⏰ Перелет: ~5.5 часов"
            },
            "Эль-Гуна": {
                "code": "HRG",
                "description": "⛵ Элитный курорт на островах с каналами",
                "temp": "🌡️ +33°C летом, +20°C зимой",
                "flight": "⏰ Перелет: ~5 часов"
            }
        }
    },
    "Мальдивы 🇲🇻": {
        "code": "MV",
        "description": "Райские острова с белоснежными пляжами и бирюзовым океаном",
        "cities": {
            "Мале": {
                "code": "MLE",
                "description": "🏝️ Столица и главный остров архипелага",
                "temp": "🌡️ +30°C круглый год",
                "flight": "⏰ Перелет: ~11 часов"
            },
            "Маафуши": {
                "code": "MLE",
                "description": "🏖️ Остров с бюджетными отелями и дайвингом",
                "temp": "🌡️ +29°C круглый год",
                "flight": "⏰ Перелет: ~11 часов"
            }
        }
    }
}

async def fetch_hotel_prices(city_code):
    """Получает цены на отели через API Travelpayouts"""
    check_in = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    check_out = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
    
    url = "http://engine.hotellook.com/api/v2/cache.json"
    params = {
        "location": city_code,
        "checkIn": check_in,
        "checkOut": check_out,
        "currency": "rub",
        "limit": 10,
        "token": TRAVELPAYOUTS_TOKEN
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                try:
                    data = await response.json()
                    if isinstance(data, list):
                        return data
                    return []
                except:
                    return []
            return []

def get_countries_keyboard():
    """Создает клавиатуру со списком стран"""
    keyboard = []
    for country in DESTINATIONS.keys():
        keyboard.append([InlineKeyboardButton(text=country, callback_data=f"country_{country}")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_cities_keyboard(country: str):
    """Создает клавиатуру со списком городов"""
    keyboard = []
    for city in DESTINATIONS[country]["cities"].keys():
        keyboard.append([InlineKeyboardButton(text=city, callback_data=f"city_{city}")])
    keyboard.append([InlineKeyboardButton(text="↩️ Назад к странам", callback_data="back_to_countries")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    """Обработчик команды /start"""
    await state.clear()
    await message.answer(
        "👋 Добро пожаловать в турагентство!\n\n"
        "🌟 Мы поможем вам организовать незабываемый отдых!\n\n"
        "💼 Что мы предлагаем:\n"
        "• Подбор тура по вашим пожеланиям\n"
        "• Бронирование отелей по лучшим ценам\n"
        "• Поддержку 24/7\n"
        "• Гарантию лучшей цены\n\n"
        "🌍 Выберите страну, куда хотели бы отправиться:",
        reply_markup=get_countries_keyboard()
    )
    await state.set_state(TourStates.choosing_country)

@dp.callback_query(F.data.startswith("country_"))
async def process_country_selection(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора страны"""
    country = callback.data.split("_")[1]
    await state.update_data(selected_country=country)
    
    country_info = DESTINATIONS[country]
    await callback.message.edit_text(
        f"🌟 {country}\n\n"
        f"ℹ️ {country_info['description']}\n\n"
        f"🏢 Выберите город для отдыха:",
        reply_markup=get_cities_keyboard(country)
    )
    await state.set_state(TourStates.choosing_city)

@dp.callback_query(F.data.startswith("city_"))
async def process_city_selection(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора города"""
    city = callback.data.split("_")[1]
    data = await state.get_data()
    country = data['selected_country']
    city_info = DESTINATIONS[country]["cities"][city]
    city_code = city_info["code"]
    
    # Получаем реальные предложения отелей
    hotels = await fetch_hotel_prices(city_code)
    
    if not hotels:
        await callback.message.edit_text(
            f"😔 К сожалению, сейчас нет доступных предложений для города {city}.\n\n"
            f"💡 Рекомендуем:\n"
            f"• Выбрать другие даты\n"
            f"• Рассмотреть другой город\n"
            f"• Связаться с менеджером для индивидуального подбора\n\n"
            f"🔄 Выберите другой город:",
            reply_markup=get_cities_keyboard(country)
        )
        return

    # Создаем клавиатуру с отелями
    keyboard = []
    for hotel in hotels[:5]:
        price = int(hotel.get('priceFrom', 0))
        hotel_name = hotel.get('hotelName', 'Отель')
        stars = "⭐" * int(hotel.get('stars', 0))
        keyboard.append([
            InlineKeyboardButton(
                text=f"{hotel_name} {stars} - от {price:,}₽",
                callback_data=f"hotel_{country}_{city}_{hotel['hotelId']}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton(text="↩️ Назад к городам", callback_data=f"back_to_cities_{country}")])
    keyboard.append([InlineKeyboardButton(text="🏠 В главное меню", callback_data="back_to_countries")])
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    await callback.message.edit_text(
        f"🌟 {city}\n\n"
        f"📍 {city_info['description']}\n"
        f"{city_info['temp']}\n"
        f"{city_info['flight']}\n\n"
        f"🏨 Доступные отели:\n"
        f"💡 Цены указаны за 7 ночей на двоих\n"
        f"📅 Вылет: {(datetime.now() + timedelta(days=7)).strftime('%d.%m.%Y')}\n",
        reply_markup=reply_markup
    )
    await state.set_state(TourStates.choosing_hotel)

@dp.callback_query(F.data.startswith("hotel_"))
async def process_hotel_selection(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора отеля"""
    _, country, city, hotel_id = callback.data.split("_", 3)
    
    # Формируем ссылку для бронирования
    booking_url = f"https://www.hotellook.ru/hotels/{hotel_id}?marker={TRAVELPAYOUTS_MARKER}"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎫 Забронировать онлайн", url=booking_url)],
        [InlineKeyboardButton(text="💬 Получить консультацию", callback_data="contact_manager")],
        [InlineKeyboardButton(text="↩️ Другие отели", callback_data=f"city_{city}")],
        [InlineKeyboardButton(text="🏠 В главное меню", callback_data="back_to_countries")]
    ])
    
    await callback.message.edit_text(
        f"🏨 Бронирование отеля\n\n"
        f"📍 {city}, {country}\n\n"
        f"💎 Что включено:\n"
        f"• Проживание 7 ночей\n"
        f"• Медицинская страховка\n"
        f"• Трансфер аэропорт-отель-аэропорт\n"
        f"• Поддержка 24/7\n\n"
        f"💡 Выберите действие:",
        reply_markup=keyboard
    )

@dp.callback_query(F.data == "contact_manager")
async def process_contact_manager(callback: CallbackQuery):
    """Обработчик кнопки связи с менеджером"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📱 WhatsApp", url="https://wa.me/+7XXXXXXXXXX")],
        [InlineKeyboardButton(text="📲 Telegram", url="https://t.me/manager")],
        [InlineKeyboardButton(text="🏠 В главное меню", callback_data="back_to_countries")]
    ])
    
    await callback.message.edit_text(
        "👋 Наши менеджеры готовы помочь!\n\n"
        "📞 Телефон: +7 (XXX) XXX-XX-XX\n"
        "📧 Email: manager@tourcompany.com\n\n"
        "⏰ Режим работы:\n"
        "Пн-Пт: 9:00 - 20:00\n"
        "Сб-Вс: 10:00 - 18:00\n\n"
        "💡 Выберите удобный способ связи:",
        reply_markup=keyboard
    )

@dp.callback_query(F.data == "back_to_countries")
async def process_back_to_countries(callback: CallbackQuery, state: FSMContext):
    """Обработчик возврата к выбору страны"""
    await state.clear()
    await callback.message.edit_text(
        "🌍 Выберите страну, куда хотели бы отправиться:",
        reply_markup=get_countries_keyboard()
    )
    await state.set_state(TourStates.choosing_country)

@dp.callback_query(F.data.startswith("back_to_cities_"))
async def process_back_to_cities(callback: CallbackQuery, state: FSMContext):
    """Обработчик возврата к выбору города"""
    country = callback.data.split("_")[3]
    await state.update_data(selected_country=country)
    await callback.message.edit_text(
        f"🏢 Выберите город в стране {country}:",
        reply_markup=get_cities_keyboard(country)
    )
    await state.set_state(TourStates.choosing_city)

async def main():
    """Запуск бота"""
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
