import logging
import os
from aiogram import Router, types, Bot
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import Command
from database import (
    get_user_by_id, create_user, get_user_interests, get_user_language, update_user_photo, update_user_age,
    update_user_language, update_user_gender, update_user_orientation,
    update_user_interests, update_user_nickname, update_user_location,
    update_user_custom_gender, update_user_ban_until, update_user_birth_year
)
from localization import set_language, translate
from aiogram.filters import StateFilter
from aiogram.types import FSInputFile
from datetime import datetime

registration_router = Router()

# Добавим новый шаг для ввода данных
class Registration(StatesGroup):
    language = State()
    nickname = State()
    birth_year = State()
    gender = State()
    custom_gender = State()
    orientation = State()
    interests = State()
    add_photo_choice = State()
    profile_photo = State()
    location = State()

# Убедитесь, что папка для фото существует
PHOTO_PATH = 'photos/'
if not os.path.exists(PHOTO_PATH):
    os.makedirs(PHOTO_PATH)

# Маппинг для перевода пола и ориентации
GENDER_MAP = {
    'Male': 'gender_male',
    'Female': 'gender_female',
    'Other': 'gender_other'
}

ORIENTATION_MAP = {
    'Heterosexual': 'orientation_heterosexual',
    'Homosexual': 'orientation_homosexual',
    'Bisexual': 'orientation_bisexual',
    'Pansexual': 'orientation_pansexual',
    'Asexual': 'orientation_asexual',
    'Lesbian': 'orientation_lesbian'
}


INTERESTS_MAP = {
    "Music": {"en": "Music", "ru": "Музыка", "kz": "Музыка"},
    "Cinema": {"en": "Cinema", "ru": "Кино", "kz": "Кино"},
    "Sport": {"en": "Sport", "ru": "Спорт", "kz": "Спорт"},
    "Technology": {"en": "Technology", "ru": "Технологии", "kz": "Технологиялар"},
    "Travel": {"en": "Travel", "ru": "Путешествия", "kz": "Саяхат"},
    "Food": {"en": "Food", "ru": "Еда", "kz": "Тамақ"},
    "Fashion": {"en": "Fashion", "ru": "Мода", "kz": "Сән"},
    "Reading": {"en": "Reading", "ru": "Чтение", "kz": "Оқу"},
    "Programming": {"en": "Programming", "ru": "Программирование", "kz": "Бағдарламалау"},
    "Games": {"en": "Games", "ru": "Игры", "kz": "Ойындар"},
    "Photography": {"en": "Photography", "ru": "Фотография", "kz": "Фотосурет"},
    "Dancing": {"en": "Dancing", "ru": "Танцы", "kz": "Би"},
    "Yoga": {"en": "Yoga", "ru": "Йога", "kz": "Йога"},
    "Meditation": {"en": "Meditation", "ru": "Медитация", "kz": "Медитация"},
    "Cooking": {"en": "Cooking", "ru": "Кулинария", "kz": "Аспаздық"},
    "Crossfit": {"en": "Crossfit", "ru": "Кроссфит", "kz": "Кроссфит"},
    "Art": {"en": "Art", "ru": "Искусство", "kz": "Өнер"},
    "Drawing": {"en": "Drawing", "ru": "Рисование", "kz": "Сурет салу"},
    "Playing Music": {"en": "Playing Music", "ru": "Игра на музыкальных инструментах", "kz": "Музыкалық аспаптарда ойнау"},
    "Singing": {"en": "Singing", "ru": "Пение", "kz": "Ән айту"},
    "Psychology": {"en": "Psychology", "ru": "Психология", "kz": "Психология"},
    "Science": {"en": "Science", "ru": "Наука", "kz": "Ғылым"},
    "Cars": {"en": "Cars", "ru": "Автомобили", "kz": "Көліктер"},
    "Motorcycles": {"en": "Motorcycles", "ru": "Мотоциклы", "kz": "Мотоциклдер"},
    "Extreme Sports": {"en": "Extreme Sports", "ru": "Экстремальные виды спорта", "kz": "Экстремалды спорт түрлері"},
    "Outdoor Cooking": {"en": "Outdoor Cooking", "ru": "Готовка на открытом воздухе", "kz": "Ашық аспан астындағы аспаздық"},
    "Camping": {"en": "Camping", "ru": "Кемпинг", "kz": "Кемпинг"},
    "Movies": {"en": "Movies", "ru": "Фильмы", "kz": "Фильмдер"}
}

# Функция для сохранения фото
async def save_profile_photo(bot: Bot, photo: types.PhotoSize, user_id: int):
    # Получаем информацию о файле с помощью API Telegram
    file_info = await bot.get_file(photo.file_id)
    file_extension = file_info.file_path.split('.')[-1]
    file_name = f"{user_id}.{file_extension}"

    # Путь для сохранения фотографии
    photo_path = os.path.join(PHOTO_PATH, file_name)

    # Сохраняем файл локально
    await bot.download_file(file_info.file_path, photo_path)

    # Возвращаем путь к фото
    return photo_path


async def start_registration(message: types.Message, state: FSMContext, bot: Bot):
    # Начало процесса регистрации
    await create_user(message.from_user.id, message.from_user.username)
    # Задаем язык по умолчанию на первом шаге (например, английский)
    lang_code = 'en'
    
    # Отправляем сообщение с выбором языка
    await message.answer(translate('choose_language', lang_code), reply_markup=set_language())
    
    # Переходим к выбору языка
    await state.set_state(Registration.language)

# Обработка выбора языка
@registration_router.message(StateFilter(Registration.language))
async def set_user_language(message: types.Message, state: FSMContext, bot: Bot):
    language_map = {
        "English": "en",
        "Русский": "ru",
        "Қазақша": "kz"
    }
    lang_code = language_map.get(message.text, 'en')
    
    # Обновляем язык пользователя в базе данных
    await update_user_language(message.from_user.id, lang_code)

    # Переход к следующему шагу регистрации
    await message.answer(translate('enter_nickname', lang_code), reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(Registration.nickname)


# Обработка ввода никнейма
@registration_router.message(StateFilter(Registration.nickname))
async def set_nickname(message: types.Message, state: FSMContext, bot: Bot):
    user = await get_user_by_id(message.from_user.id)
    if user:
        await update_user_nickname(message.from_user.id, message.text)
        lang_code = user['lang']

        # Переход к вводу возраста
        await message.answer(translate('enter_birth_year', lang_code))
        await state.set_state(Registration.birth_year)

# Обработка ввода года рождения
@registration_router.message(StateFilter(Registration.birth_year))
async def set_birth_year(message: types.Message, state: FSMContext):
    user = await get_user_by_id(message.from_user.id)
    if user:
        lang_code = user['lang']

        # Проверяем, что пользователь ввел только цифры
        if not message.text.isdigit():
            await message.answer(translate('invalid_birth_year', lang_code))
            return

        # Преобразуем ввод в целое число
        birth_year = int(message.text)
        current_year = datetime.now().year

        # Проверка возраста и корректности года
        age = current_year - birth_year
        if age < 19:
            # Если пользователю меньше 19 лет, мы его блокируем до достижения 19 лет
            ban_duration = 19 - age  # Количество лет до достижения 19
            unban_year = current_year + ban_duration
            await update_user_ban_until(message.from_user.id, unban_year)
            await message.answer(translate('underage_ban', lang_code).format(unban_year=unban_year))
            return
        elif birth_year > current_year or birth_year < 1990:
            # Если год рождения указан некорректно
            await message.answer(translate('invalid_birth_year', lang_code))
            return

        # Сохраняем возраст пользователя
        await update_user_age(message.from_user.id, age)

        # Переход к выбору пола
        await message.answer(translate('age_saved', lang_code))
        await message.answer(translate('start_registration', lang_code), reply_markup=get_gender_keyboard(lang_code))
        await state.set_state(Registration.gender)

# Клавиатура для выбора пола
def get_gender_keyboard(lang_code):
    gender_buttons = [
        [types.KeyboardButton(text=translate('gender_male', lang_code))],
        [types.KeyboardButton(text=translate('gender_female', lang_code))],
        [types.KeyboardButton(text=translate('gender_other', lang_code))]
    ]
    markup = types.ReplyKeyboardMarkup(keyboard=gender_buttons, resize_keyboard=True)
    return markup

# Обработка выбора пола
@registration_router.message(StateFilter(Registration.gender))
async def set_gender(message: types.Message, state: FSMContext, bot: Bot):
    user = await get_user_by_id(message.from_user.id)
    if user:
        lang_code = user['lang']
        gender_map = {
            translate('gender_male', lang_code): 'Male',
            translate('gender_female', lang_code): 'Female',
            translate('gender_other', lang_code): 'Other'
        }
        gender = gender_map.get(message.text)

        if not gender:
            await message.answer(translate('invalid_gender', lang_code))
            return

        if gender == 'Other':
            # Переход к вводу кастомного гендера
            await message.answer(translate('enter_custom_gender', lang_code))
            await state.set_state(Registration.custom_gender)
        else:
            # Сохраняем пол и продолжаем регистрацию
            await update_user_gender(message.from_user.id, gender)
            await message.answer(translate('gender_saved', lang_code), reply_markup=types.ReplyKeyboardRemove())
            await message.answer(translate('choose_orientation', lang_code), reply_markup=get_orientation_keyboard(gender, lang_code))
            await state.set_state(Registration.orientation)

# Обработка кастомного гендера
@registration_router.message(StateFilter(Registration.custom_gender))
async def set_custom_gender(message: types.Message, state: FSMContext, bot: Bot):
    user = await get_user_by_id(message.from_user.id)
    if user:
        lang_code = user['lang']

        # Сохраняем кастомный пол и отмечаем его как "Other" для основной логики
        custom_gender = message.text
        await update_user_custom_gender(message.from_user.id, custom_gender)
        await update_user_gender(message.from_user.id, 'Other')  # Используем "Other" для основной логики

        # Переход к выбору ориентации
        await message.answer(translate('gender_saved_custom', lang_code).format(custom_gender=custom_gender), reply_markup=types.ReplyKeyboardRemove())
        await message.answer(translate('choose_orientation', lang_code), reply_markup=get_orientation_keyboard('Other', lang_code))
        await state.set_state(Registration.orientation)

# Клавиатура для выбора ориентации
def get_orientation_keyboard(gender, lang_code):
    if gender == 'Male':
        orientation_buttons = [
            [types.KeyboardButton(text=translate('orientation_heterosexual', lang_code))],
            [types.KeyboardButton(text=translate('orientation_homosexual', lang_code))],
            [types.KeyboardButton(text=translate('orientation_bisexual', lang_code))],
            [types.KeyboardButton(text=translate('orientation_pansexual', lang_code))],
            [types.KeyboardButton(text=translate('orientation_asexual', lang_code))]
        ]
    elif gender == 'Female':
        orientation_buttons = [
            [types.KeyboardButton(text=translate('orientation_heterosexual_female', lang_code))],
            [types.KeyboardButton(text=translate('orientation_lesbian', lang_code))],
            [types.KeyboardButton(text=translate('orientation_bisexual_female', lang_code))],
            [types.KeyboardButton(text=translate('orientation_pansexual_female', lang_code))],
            [types.KeyboardButton(text=translate('orientation_asexual_female', lang_code))]
        ]
    else:  # Пол "Other", доступны все варианты
        orientation_buttons = [
            [types.KeyboardButton(text=translate('orientation_heterosexual', lang_code))],
            [types.KeyboardButton(text=translate('orientation_homosexual', lang_code))],
            [types.KeyboardButton(text=translate('orientation_lesbian', lang_code))],
            [types.KeyboardButton(text=translate('orientation_bisexual', lang_code))],
            [types.KeyboardButton(text=translate('orientation_pansexual', lang_code))],
            [types.KeyboardButton(text=translate('orientation_asexual', lang_code))]
        ]
    markup = types.ReplyKeyboardMarkup(keyboard=orientation_buttons, resize_keyboard=True)
    return markup

# Обработка выбора ориентации
@registration_router.message(StateFilter(Registration.orientation))
async def set_orientation(message: types.Message, state: FSMContext, bot: Bot):
    user = await get_user_by_id(message.from_user.id)
    if user:
        lang_code = user['lang']
        
        orientation_map = {
            translate('orientation_heterosexual', lang_code): 'Heterosexual',
            translate('orientation_homosexual', lang_code): 'Homosexual',
            translate('orientation_bisexual', lang_code): 'Bisexual',
            translate('orientation_pansexual', lang_code): 'Pansexual',
            translate('orientation_asexual', lang_code): 'Asexual',
            translate('orientation_lesbian', lang_code): 'Lesbian'
        }
        orientation = orientation_map.get(message.text)

        if not orientation:
            await message.answer(translate('invalid_orientation', lang_code))
            return

        # Сохраняем ориентацию на английском в базу
        await update_user_orientation(message.from_user.id, orientation)

        # Переход к выбору интересов
        await message.answer(translate('orientation_saved', lang_code), reply_markup=types.ReplyKeyboardRemove())
        await message.answer(translate('choose_interests', lang_code), reply_markup=get_interests_keyboard(lang_code))
        await state.set_state(Registration.interests)

# Клавиатура для выбора интересов с 40 пунктами
def get_interests_keyboard(lang_code):
    interests_buttons = [
        [types.KeyboardButton(text=translate('music', lang_code)), types.KeyboardButton(text=translate('cinema', lang_code))],
        [types.KeyboardButton(text=translate('sport', lang_code)), types.KeyboardButton(text=translate('technology', lang_code))],
        [types.KeyboardButton(text=translate('travel', lang_code)), types.KeyboardButton(text=translate('food', lang_code))],
        [types.KeyboardButton(text=translate('fashion', lang_code)), types.KeyboardButton(text=translate('reading', lang_code))],
        [types.KeyboardButton(text=translate('programming', lang_code)), types.KeyboardButton(text=translate('games', lang_code))],
        [types.KeyboardButton(text=translate('photography', lang_code)), types.KeyboardButton(text=translate('dancing', lang_code))],
        [types.KeyboardButton(text=translate('yoga', lang_code)), types.KeyboardButton(text=translate('meditation', lang_code))],
        [types.KeyboardButton(text=translate('cooking', lang_code)), types.KeyboardButton(text=translate('crossfit', lang_code))],
        [types.KeyboardButton(text=translate('art', lang_code)), types.KeyboardButton(text=translate('drawing', lang_code))],
        [types.KeyboardButton(text=translate('music_playing', lang_code)), types.KeyboardButton(text=translate('singing', lang_code))],
        [types.KeyboardButton(text=translate('psychology', lang_code)), types.KeyboardButton(text=translate('science', lang_code))],
        [types.KeyboardButton(text=translate('cars', lang_code)), types.KeyboardButton(text=translate('motorcycles', lang_code))],
        [types.KeyboardButton(text=translate('extreme_sports', lang_code)), types.KeyboardButton(text=translate('outdoor_cooking', lang_code))],
        [types.KeyboardButton(text=translate('camping', lang_code)), types.KeyboardButton(text=translate('movies', lang_code))]
    ]
    markup = types.ReplyKeyboardMarkup(keyboard=interests_buttons, resize_keyboard=True)
    return markup

# Клавиатура с кнопкой "Готово", когда выбрано минимум 3 интереса
def get_interests_keyboard_with_done(lang_code):
    interests_buttons = get_interests_keyboard(lang_code).keyboard
    interests_buttons.insert(0, [types.KeyboardButton(text=translate('done', lang_code))])  # Добавляем кнопку "Готово" в начало
    markup = types.ReplyKeyboardMarkup(keyboard=interests_buttons, resize_keyboard=True)
    return markup

# Обработка выбора интересов
@registration_router.message(StateFilter(Registration.interests))
async def set_interests(message: types.Message, state: FSMContext, bot: Bot):
    # Получаем текущие интересы пользователя
    data = await state.get_data()
    user_interests = data.get('user_interests', [])

    # Получаем язык пользователя
    user = await get_user_by_id(message.from_user.id)
    lang_code = user['lang']

    # Обработка кнопки "Готово" (Done)
    if message.text == translate('done', lang_code):
        if len(user_interests) < 3:
            await message.answer(translate('interests_minimum', lang_code))
        else:
            # Преобразуем интересы в английские названия перед сохранением
            english_interests = [INTERESTS_MAP.get(interest, {}).get('en', interest) for interest in user_interests]

            # Сохраняем интересы и переходим к добавлению фото
            await update_user_interests(message.from_user.id, english_interests)
            await message.answer(translate('registration_completed', lang_code), reply_markup=types.ReplyKeyboardRemove())

            # Переход к выбору добавления фото
            await message.answer(translate('ask_add_photo', lang_code), reply_markup=get_yes_no_keyboard(lang_code))
            await state.set_state(Registration.add_photo_choice)
    else:
        # Найдем английский эквивалент выбранного интереса
        english_interest = next(
            (interest for interest, translations in INTERESTS_MAP.items() if translations.get(lang_code) == message.text),
            None
        )

        # Добавляем интерес в список, если он не был добавлен ранее
        if english_interest and english_interest not in user_interests:
            user_interests.append(english_interest)
            await state.update_data(user_interests=user_interests)
            await message.answer(f"{message.text} {translate('interest_added', lang_code)}")

        # Если выбрано меньше 3 интересов, не показываем кнопку "Готово"
        if len(user_interests) >= 3:
            await message.answer(translate('done_button_available', lang_code), reply_markup=get_interests_keyboard_with_done(lang_code))
        else:
            await message.answer(translate('choose_more_interests', lang_code))

# Клавиатура с кнопками "Да" и "Нет"
def get_yes_no_keyboard(lang_code):
    buttons = [
        [types.KeyboardButton(text=translate('yes', lang_code))],
        [types.KeyboardButton(text=translate('no', lang_code))]
    ]
    return types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

# Обработка ответа на вопрос о добавлении фото
@registration_router.message(StateFilter(Registration.add_photo_choice))
async def add_photo_choice(message: types.Message, state: FSMContext, bot: Bot):
    user = await get_user_by_id(message.from_user.id)
    if user:
        lang_code = user['lang']

        if message.text == translate('yes', lang_code):
            # Если пользователь выбрал "Да", просим загрузить фото
            await message.answer(translate('send_profile_photo', lang_code), reply_markup=types.ReplyKeyboardRemove())
            await state.set_state(Registration.profile_photo)
        elif message.text == translate('no', lang_code):
            # Если пользователь выбрал "Нет", переходим к геолокации
            await message.answer(translate('share_location_prompt', lang_code), reply_markup=request_location_keyboard(lang_code))
            await state.set_state(Registration.location)
        else:
            await message.answer(translate('invalid_choice', lang_code), reply_markup=get_yes_no_keyboard(lang_code))

# Обработка загрузки фото, видео и GIF профиля
@registration_router.message(StateFilter(Registration.profile_photo), F.photo | F.video | F.animation)
async def process_profile_media(message: types.Message, state: FSMContext, bot: Bot):
    user = await get_user_by_id(message.from_user.id)
    if user:
        lang_code = user['lang']

        # Проверяем, что отправлен фото, видео или GIF
        media = None
        media_type = None
        if message.photo:
            media = message.photo[-1]  # Получаем наибольшую версию загруженной фотографии
            media_type = 'photo'
        elif message.video:
            media = message.video  # Получаем видео
            media_type = 'video'
        elif message.animation:
            media = message.animation  # Получаем GIF
            media_type = 'animation'

        if not media:
            await message.answer(translate('invalid_media', lang_code))
            return

        # Сохраняем фото, видео или GIF
        try:
            if media_type == 'photo':
                file_path = await save_profile_photo(bot, media, message.from_user.id)
            else:
                file_path = await save_profile_video_or_gif(bot, media, message.from_user.id, media_type)
            
            await update_user_photo(message.from_user.id, file_path)
            await message.answer(translate('media_saved', lang_code), reply_markup=types.ReplyKeyboardRemove())

            # Переход к запросу геолокации
            await message.answer(translate('share_location_prompt', lang_code), reply_markup=request_location_keyboard(lang_code))
            await state.set_state(Registration.location)
        except Exception as e:
            await message.answer(translate('media_save_error', lang_code))
            print(f"Ошибка при сохранении медиа: {e}")

# Функция для сохранения видео или GIF
async def save_profile_video_or_gif(bot: Bot, media: types.Video | types.Animation, user_id: int, media_type: str):
    # Получаем информацию о файле с помощью API Telegram
    file_info = await bot.get_file(media.file_id)
    file_extension = 'mp4' if media_type == 'video' else 'gif'
    file_name = f"{user_id}.{file_extension}"

    # Путь для сохранения видео или GIF
    media_path = os.path.join(PHOTO_PATH, file_name)

    # Сохраняем файл локально
    await bot.download_file(file_info.file_path, media_path)

    # Возвращаем путь к видео или GIF
    return media_path

# Клавиатура для запроса геолокации
def request_location_keyboard(lang_code):
    buttons = [
        [types.KeyboardButton(text=translate('share_location', lang_code), request_location=True)]
    ]
    return types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

# Обработка отправки геолокации
@registration_router.message(StateFilter(Registration.location))
async def process_location(message: types.Message, state: FSMContext, bot: Bot):
    user = await get_user_by_id(message.from_user.id)
    if user:
        lang_code = user['lang']

        if message.location:
            latitude = message.location.latitude
            longitude = message.location.longitude

            # Сохраняем координаты в базе данных
            await update_user_location(message.from_user.id, f"{latitude}, {longitude}")

            # Сообщение пользователю
            await message.answer(translate('location_saved', lang_code), reply_markup=types.ReplyKeyboardRemove())

            # Показать профиль после регистрации
            await message.answer(translate('registration_completed', lang_code), reply_markup=get_show_profile_keyboard(lang_code))
            await show_profile(message, bot)
            await state.clear()  # Завершение процесса регистрации
        else:
            await message.answer(translate('location_error', lang_code))

# Клавиатура для отображения кнопки "Показать профиль"
def get_show_profile_keyboard(lang_code):
    buttons = [
        [types.KeyboardButton(text=translate('show_profile', lang_code))],
    ]
    return types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

# Обработка нажатия кнопки "Показать профиль"
@registration_router.message(F.text == translate('show_profile', 'en'))
async def handle_show_profile(message: types.Message, bot: Bot):
    await show_profile(message, bot)

# Показ профиля с учётом языка пользователя
async def show_profile(message: types.Message, bot: Bot):
    user = await get_user_by_id(message.from_user.id)

    if user:
        # Получаем язык пользователя
        user_lang = await get_user_language(message.from_user.id)

        # Переводим пол и ориентацию с использованием маппингов
        gender_key = GENDER_MAP.get(user.get('gender', 'Other'), 'gender_other')
        gender = translate(gender_key, user_lang)

        orientation_key = ORIENTATION_MAP.get(user.get('orientation', 'Heterosexual'), 'orientation_heterosexual')
        orientation = translate(orientation_key, user_lang)

        nickname = user.get('username', 'N/A')

        # Получение интересов пользователя из таблицы user_interests
        interests_list = await get_user_interests(message.from_user.id)

        # Проверяем, что interests_list — это список строк, и объединяем их с переводом
        if interests_list:
            interests_str = ', '.join([translate(interest.lower(), user_lang) for interest in interests_list])
        else:
            interests_str = translate('no_interests', user_lang)  # "Нет интересов" на нужном языке

        location = user.get('location', 'N/A')

        # Формируем сообщение профиля с переводом
        profile_info = (
            f"👤 {translate('nickname', user_lang)}: {nickname}\n"
            f"🚻 {translate('gender', user_lang)}: {gender}\n"
            f"🎯 {translate('orientation', user_lang)}: {orientation}\n"
            f"📚 {translate('interests', user_lang)}: {interests_str}\n"
        )

        # Логируем итоговую информацию профиля
        logging.info(f"Generated profile info: {profile_info}")

        # Отправляем медиа (фото, видео или GIF) профиля, если оно есть
        media_path = user.get('profile_photo')
        if media_path:
            try:
                # Определяем тип медиа по расширению файла
                input_file = FSInputFile(media_path)
                if media_path.endswith('.mp4'):
                    await bot.send_video(message.chat.id, input_file, caption=profile_info)
                elif media_path.endswith('.gif'):
                    await bot.send_animation(message.chat.id, input_file, caption=profile_info)
                else:
                    await bot.send_photo(message.chat.id, input_file, caption=profile_info)
            except Exception as e:
                await message.answer(f"Ошибка при отправке медиа: {e}")
                logging.error(f"Media send error: {e}")
        else:
            await message.answer(profile_info)
    else:
        logging.error(f"User not found with ID: {message.from_user.id}")
        await message.answer("Пользователь не найден. Попробуйте зарегистрироваться заново.")




