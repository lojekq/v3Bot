from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from localization import set_language, translate

# Первоначальная клавиатура (когда поиск еще не начат)
def initial_keyboard():
    keyboard = [
        [KeyboardButton(text='🔍 Поиск'), KeyboardButton(text='👤 Показать профиль')]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

# Клавиатура во время поиска
def search_keyboard():
    keyboard = [
        [KeyboardButton(text='🚪 Покинуть поиск')]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

# Клавиатура при нахождении совпадения
def match_keyboard():
    keyboard = [
        [KeyboardButton(text='❌ Выйти из чата'), KeyboardButton(text='🚫 Заблокировать')]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
