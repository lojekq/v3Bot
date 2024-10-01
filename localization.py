from babel.support import Translations
import os
from aiogram import types

LOCALES_DIR = os.path.join(os.path.dirname(__file__), 'locale')

# Получение перевода для выбранного языка
def get_translations(lang_code):
    try:
        translations = Translations.load(LOCALES_DIR, [lang_code])
    except FileNotFoundError:
        translations = Translations.load(LOCALES_DIR, ['en'])
    return translations

# Установка выбора языка (кнопки)
def set_language():
    # Создание клавиатуры с кнопками для выбора языка
    markup = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="English")],
            [types.KeyboardButton(text="Русский")],
            [types.KeyboardButton(text="Қазақша")]
        ],
        resize_keyboard=True
    )
    return markup

# Функция перевода сообщения
def translate(message_key, lang_code):
    translations = get_translations(lang_code)
    return translations.gettext(message_key)

