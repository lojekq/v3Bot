from babel.support import Translations
import os
import logging
# Путь к локалям
LOCALES_DIR = os.path.join(os.path.dirname(__file__), 'locale')

# Функция для загрузки переводов по языковому коду
def get_translations(lang_code):
    try:
        translations = Translations.load(LOCALES_DIR, [lang_code])
        logging.info(f"Loaded translations for language: {lang_code}")
        return translations
    except FileNotFoundError:
        logging.error(f"Translation file for {lang_code} not found, loading English as default.")
        return Translations.load(LOCALES_DIR, ['en'])





def translate(message_key, lang_code):
    translations = get_translations(lang_code)
    logging.info(f"Translating key: {message_key}, for language: {lang_code}")
    return translations.gettext(message_key)


# Функция для создания клавиатуры выбора языка
def set_language():
    from aiogram import types
    markup = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="English")],
            [types.KeyboardButton(text="Русский")],
            [types.KeyboardButton(text="Қазақша")]
        ],
        resize_keyboard=True
    )
    return markup
