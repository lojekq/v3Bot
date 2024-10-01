from aiogram import Router, types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import Command
from database import get_user_by_id, create_user, update_user_language, update_user_gender, update_user_orientation, update_user_interests, update_user_nickname
from localization import set_language, translate
from aiogram.filters.state import StateFilter

user_router = Router()

# Определение состояний
class Registration(StatesGroup):
    nickname = State()
    gender = State()
    custom_gender = State()
    orientation = State()
    interests = State()

# Команда /start
@user_router.message(Command(commands=['start']))
async def start(message: types.Message, state: FSMContext):
    user = await get_user_by_id(message.from_user.id)
    
    if user:
        lang_code = user['lang'] or 'en'
        welcome_message = translate('welcome_back', lang_code)
        await message.answer(welcome_message)
    else:
        await create_user(message.from_user.id, message.from_user.username)
        await message.answer(translate('choose_language', 'en'), reply_markup=set_language())

# Обработка выбора языка
@user_router.message(lambda message: message.text in ['English', 'Русский', 'Қазақша'])
async def set_user_language(message: types.Message, state: FSMContext, bot: Bot):
    language_map = {
        "English": "en",
        "Русский": "ru",
        "Қазақша": "kz"
    }
    lang_code = language_map.get(message.text, 'en')
    await update_user_language(message.from_user.id, lang_code)
    
    # Переход к вводу никнейма
    await message.answer(translate('enter_nickname', lang_code), reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(Registration.nickname)

# Обработка ввода никнейма
@user_router.message(StateFilter(Registration.nickname))
async def set_nickname(message: types.Message, state: FSMContext, bot: Bot):
    user = await get_user_by_id(message.from_user.id)
    if user:
        await update_user_nickname(message.from_user.id, message.text)
        lang_code = user['lang']
        
        # Переход к выбору пола
        await message.answer(translate('nickname_saved', lang_code))
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
@user_router.message(StateFilter(Registration.gender))
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

        # Сохраняем пол в базе данных
        await update_user_gender(message.from_user.id, gender)
        
        # Переход к выбору ориентации
        await message.answer(translate('gender_saved', lang_code), reply_markup=types.ReplyKeyboardRemove())
        await message.answer(translate('choose_orientation', lang_code), reply_markup=get_orientation_keyboard(gender, lang_code))
        
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
@user_router.message(StateFilter(Registration.orientation))
async def set_orientation(message: types.Message, state: FSMContext, bot: Bot):
    user = await get_user_by_id(message.from_user.id)
    if user:
        lang_code = user['lang']
        
        # Получаем пол из базы данных
        gender = user['gender']
        
        # Возможные ориентации в зависимости от пола
        if gender == 'Male':
            valid_orientations = [
                translate('orientation_heterosexual', lang_code),
                translate('orientation_homosexual', lang_code),
                translate('orientation_bisexual', lang_code),
                translate('orientation_pansexual', lang_code),
                translate('orientation_asexual', lang_code)
            ]
        elif gender == 'Female':
            valid_orientations = [
                translate('orientation_heterosexual_female', lang_code),
                translate('orientation_lesbian', lang_code),
                translate('orientation_bisexual_female', lang_code),
                translate('orientation_pansexual_female', lang_code),
                translate('orientation_asexual_female', lang_code)
            ]
        else:  # Пол "Other", доступны все варианты
            valid_orientations = [
                translate('orientation_heterosexual', lang_code),
                translate('orientation_homosexual', lang_code),
                translate('orientation_lesbian', lang_code),
                translate('orientation_bisexual', lang_code),
                translate('orientation_pansexual', lang_code),
                translate('orientation_asexual', lang_code)
            ]
        
        # Проверка, введена ли допустимая ориентация
        if message.text not in valid_orientations:
            await message.answer(translate('invalid_orientation', lang_code))
            await message.answer(translate('choose_orientation', lang_code), reply_markup=get_orientation_keyboard(gender, lang_code))
        else:
            # Сохраняем ориентацию в базе данных
            await update_user_orientation(message.from_user.id, message.text)
            
            # Переход к выбору интересов
            await message.answer(translate('orientation_saved', lang_code), reply_markup=types.ReplyKeyboardRemove())
            await message.answer(translate('choose_interests', lang_code), reply_markup=get_interests_keyboard(lang_code))
            await state.set_state(Registration.interests)

# Клавиатура для выбора интересов с 40 пунктами
def get_interests_keyboard(lang_code):
    interests_buttons = [
        [types.KeyboardButton(text="Музыка"), types.KeyboardButton(text="Кино")],
        [types.KeyboardButton(text="Спорт"), types.KeyboardButton(text="Технологии")],
        [types.KeyboardButton(text="Путешествия"), types.KeyboardButton(text="Еда")],
        [types.KeyboardButton(text="Мода"), types.KeyboardButton(text="Чтение")],
        [types.KeyboardButton(text="Программирование"), types.KeyboardButton(text="Игры")],
        [types.KeyboardButton(text="Фотография"), types.KeyboardButton(text="Танцы")],
        [types.KeyboardButton(text="Йога"), types.KeyboardButton(text="Медитация")],
        [types.KeyboardButton(text="Кулинария"), types.KeyboardButton(text="Кроссфит")],
        [types.KeyboardButton(text="Арт"), types.KeyboardButton(text="Рисование")],
        [types.KeyboardButton(text="Музыка (игра)"), types.KeyboardButton(text="Пение")],
        [types.KeyboardButton(text="Психология"), types.KeyboardButton(text="Наука")],
        [types.KeyboardButton(text="Автомобили"), types.KeyboardButton(text="Мотоциклы")],
        [types.KeyboardButton(text="Экстремальные виды спорта"), types.KeyboardButton(text="Готовка на природе")],
        [types.KeyboardButton(text="Кемпинг"), types.KeyboardButton(text="Фильмы")],
        [types.KeyboardButton(text=translate('done', lang_code))]  # Эта кнопка появится только после выбора 3 интересов
    ]
    markup = types.ReplyKeyboardMarkup(keyboard=interests_buttons, resize_keyboard=True)
    return markup

# Обработка выбора интересов
@user_router.message(StateFilter(Registration.interests))
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
            # Сохраняем интересы и завершаем
            await update_user_interests(message.from_user.id, user_interests)
            await message.answer(translate('registration_completed', lang_code), reply_markup=types.ReplyKeyboardRemove())
            await state.clear()  # Завершение регистрации
    else:
        # Добавляем интерес в список, если он не был добавлен ранее
        if message.text not in user_interests:
            user_interests.append(message.text)
            await state.update_data(user_interests=user_interests)
            await message.answer(f"{message.text} {translate('interest_added', lang_code)}")

        # Если выбрано меньше 3 интересов, не показываем кнопку "Готово"
        if len(user_interests) >= 3:
            await message.answer(translate('done_button_available', lang_code), reply_markup=get_interests_keyboard_with_done(lang_code))
        else:
            await message.answer(translate('choose_more_interests', lang_code))

# Клавиатура с кнопкой "Готово", когда выбрано минимум 3 интереса
def get_interests_keyboard_with_done(lang_code):
    interests_buttons = get_interests_keyboard(lang_code).keyboard
    interests_buttons.insert(0, [types.KeyboardButton(text=translate('done', lang_code))])  # Добавляем кнопку "Готово" в начало
    markup = types.ReplyKeyboardMarkup(keyboard=interests_buttons, resize_keyboard=True)
    return markup

