from aiogram import Router, types, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from database import (
    get_user_by_id, get_user_interests, update_user_photo, update_user_orientation, update_user_interests, update_search_radius, get_blocked_users, unblock_user
)
from handlers.registration_handlers import INTERESTS_MAP, get_interests_keyboard, get_orientation_keyboard, save_profile_photo
from localization import translate
from aiogram.filters import StateFilter
from keyboards import initial_keyboard

settings_router = Router()

class Settings(StatesGroup):
    photo = State()
    orientation = State()
    interests = State()
    search_radius = State()
    unblock_user = State()

# Обработка команды "Настройки"
@settings_router.message(F.text == '⚙️ Настройки')
async def settings_menu(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = await get_user_by_id(user_id)
    
    if user:
        lang_code = user['lang']
        await message.answer(translate('choose_setting', lang_code), reply_markup=settings_keyboard(lang_code))

# Клавиатура настроек с кнопкой "Вернуться в главное меню"
def settings_keyboard(lang_code):
    buttons = [
        [types.KeyboardButton(text='📷 Изменить фото'), types.KeyboardButton(text='🎯 Изменить ориентацию'), types.KeyboardButton(text='📚 Изменить интересы')],
        [types.KeyboardButton(text='📍 Изменить расстояние поиска'), types.KeyboardButton(text='🚫 Снять блокировку'), types.KeyboardButton(text='⬅️ В главное меню')]
    ]
    return types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

# Обработка нажатия кнопки "Вернуться в главное меню"
@settings_router.message(F.text == '⬅️ В главное меню')
async def back_to_main_menu(message: types.Message, state: FSMContext):
    await message.answer("Вы вернулись в главное меню.", reply_markup=initial_keyboard())
    await state.clear()

# Обновление фото профиля
@settings_router.message(F.text == '📷 Изменить фото')
async def change_photo(message: types.Message, state: FSMContext):
    await message.answer("Пожалуйста, отправьте новое фото профиля.")
    await state.set_state(Settings.photo)

@settings_router.message(StateFilter(Settings.photo), F.photo)
async def save_new_photo(message: types.Message, state: FSMContext, bot: Bot):
    user_id = message.from_user.id
    file_path = await save_profile_photo(bot, message.photo[-1], user_id)
    await update_user_photo(user_id, file_path)
    await message.answer("Фото успешно обновлено!", reply_markup=initial_keyboard())
    await state.clear()

# Обновление ориентации
@settings_router.message(F.text == '🎯 Изменить ориентацию')
async def change_orientation(message: types.Message, state: FSMContext):
    user = await get_user_by_id(message.from_user.id)
    lang_code = user['lang']
    await message.answer(translate('choose_orientation', lang_code), reply_markup=get_orientation_keyboard('Other', lang_code))
    await state.set_state(Settings.orientation)

@settings_router.message(StateFilter(Settings.orientation))
async def set_new_orientation(message: types.Message, state: FSMContext):
    user = await get_user_by_id(message.from_user.id)
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
    if orientation:
        await update_user_orientation(message.from_user.id, orientation)
        await message.answer("Ориентация обновлена!", reply_markup=initial_keyboard())
        await state.clear()
    else:
        await message.answer("Неверная ориентация. Попробуйте снова.")

# Пример собственного списка интересов
CUSTOM_INTERESTS_LIST = {
    "Music": {"en": "Music", "ru": "Музыка"},
    "Cinema": {"en": "Cinema", "ru": "Кино"},
    "Sport": {"en": "Sport", "ru": "Спорт"},
    "Technology": {"en": "Technology", "ru": "Технологии"},
    "Travel": {"en": "Travel", "ru": "Путешествия"},
    "Food": {"en": "Food", "ru": "Еда"},
    "Fashion": {"en": "Fashion", "ru": "Мода"},
    "Reading": {"en": "Reading", "ru": "Чтение"},
    "Programming": {"en": "Programming", "ru": "Программирование"},
    "Games": {"en": "Games", "ru": "Игры"},
    "Photography": {"en": "Photography", "ru": "Фотография"},
    "Dancing": {"en": "Dancing", "ru": "Танцы"},
    "Yoga": {"en": "Yoga", "ru": "Йога"},
    "Meditation": {"en": "Meditation", "ru": "Медитация"},
    "Cooking": {"en": "Cooking", "ru": "Кулинария"},
    "Crossfit": {"en": "Crossfit", "ru": "Кроссфит"},
    "Art": {"en": "Art", "ru": "Искусство"},
    "Drawing": {"en": "Drawing", "ru": "Рисование"},
    "Playing Music": {"en": "Playing Music", "ru": "Игра на музыкальных инструментах"},
    "Singing": {"en": "Singing", "ru": "Пение"},
    "Psychology": {"en": "Psychology", "ru": "Психология"},
    "Science": {"en": "Science", "ru": "Наука"},
    "Cars": {"en": "Cars", "ru": "Автомобили"},
    "Motorcycles": {"en": "Motorcycles", "ru": "Мотоциклы"},
    "Extreme_Sports": {"en": "Extreme Sports", "ru": "Экстремальные виды спорта"},
    "Outdoor_Cooking": {"en": "Outdoor Cooking", "ru": "Готовка на открытом воздухе"},
    "Camping": {"en": "Camping", "ru": "Кемпинг"},
    "Movies": {"en": "Movies", "ru": "Фильмы"},
    "BDSM": {"en": "BDSM", "ru": "БДСМ"},
    "Role_Playing": {"en": "Role-Playing", "ru": "Ролевые игры"},
    "Foot_Fetish": {"en": "Foot Fetish", "ru": "Фут-фетиш"},
    "Anal_Sex": {"en": "Anal Sex", "ru": "Анальный секс"},
    "Group_Sex": {"en": "Group Sex", "ru": "Групповой секс"},
    "Orgasm_Control": {"en": "Orgasm Control", "ru": "Контроль оргазма"},
    "Bondage": {"en": "Bondage", "ru": "Бондаж"},
    "Exhibitionism": {"en": "Exhibitionism", "ru": "Эксгибиционизм"},
    "Erotic_Humiliation": {"en": "Erotic Humiliation", "ru": "Эротическое унижение"},
    "Dominance_and_Submission": {"en": "Dominance and Submission", "ru": "Доминирование и подчинение"},
    "Urophilia": {"en": "Urophilia", "ru": "Урофилия"},
    "Sadism_Masochism": {"en": "Sadism and Masochism", "ru": "Садизм и мазохизм"},
    "Wax_play": {"en": "Wax play", "ru": "Игра с воском"},
    "Quirofilia": {"en": "Quirofilia", "ru": "Кирофилия"},
    "Electrostimulation": {"en": "Electrostimulation", "ru": "Электростимуляция"}

}

# Таблица интересов
def get_interests_table(user_interests, lang_code):
    table = []
    current_row = []
    for interest_key, translations in CUSTOM_INTERESTS_LIST.items():
        interest_name = translations.get(lang_code, translations['en'])
        if interest_key in user_interests:
            button_text = f"✅ {interest_name}"
        else:
            button_text = f"❌ {interest_name}"
        current_row.append(types.KeyboardButton(text=button_text))
        
        if len(current_row) == 3:  # По два интереса в строке
            table.append(current_row)
            current_row = []
    
    if current_row:
        table.append(current_row)
    
    # Кнопка "Готово" внизу
    table.append([types.KeyboardButton(text=translate('done', lang_code))])
    
    return types.ReplyKeyboardMarkup(keyboard=table, resize_keyboard=True)

# Обновление интересов с таблицей
@settings_router.message(F.text == '📚 Изменить интересы')
async def change_interests(message: types.Message, state: FSMContext):
    user = await get_user_by_id(message.from_user.id)
    lang_code = user['lang']
    user_interests = await get_user_interests(message.from_user.id)
    
    await message.answer(translate('choose_interests', lang_code), 
                         reply_markup=get_interests_table(user_interests, lang_code))
    await state.set_state(Settings.interests)

@settings_router.message(StateFilter(Settings.interests))
async def update_interests(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_interests = data.get('user_interests', [])
    user = await get_user_by_id(message.from_user.id)
    lang_code = user['lang']
    
    if message.text == translate('done', lang_code):
        if len(user_interests) < 3:
            await message.answer(translate('interests_minimum', lang_code))
        else:
            await update_user_interests(message.from_user.id, user_interests)
            await message.answer(translate('interests_updated', lang_code), reply_markup=initial_keyboard())
            await state.clear()
    else:
        interest_text = message.text[2:].strip()  # Убираем символы ✅/❌ и пробелы
        english_interest = next((key for key, value in CUSTOM_INTERESTS_LIST.items() if value.get(lang_code, value['en']) == interest_text), None)

        if english_interest:
            if english_interest in user_interests:
                user_interests.remove(english_interest)
                await message.answer(f"{interest_text} {translate('interest_removed', lang_code)}")
            else:
                user_interests.append(english_interest)
                await message.answer(f"{interest_text} {translate('interest_added', lang_code)}")
            await state.update_data(user_interests=user_interests)

        await message.answer(translate('choose_more_interests', lang_code),
                             reply_markup=get_interests_table(user_interests, lang_code))



# Изменение радиуса поиска
@settings_router.message(F.text == '📍 Изменить расстояние поиска')
async def change_search_radius(message: types.Message, state: FSMContext):
    await message.answer("Введите новое расстояние поиска (в км):")
    await state.set_state(Settings.search_radius)

@settings_router.message(StateFilter(Settings.search_radius))
async def set_search_radius(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        new_radius = int(message.text)
        await update_search_radius(message.from_user.id, new_radius)
        await message.answer(f"Расстояние поиска изменено на {new_radius} км.", reply_markup=initial_keyboard())
        await state.clear()
    else:
        await message.answer("Пожалуйста, введите корректное число.")

# Снятие блокировки с пользователей
@settings_router.message(F.text == '🚫 Снять блокировку')
async def unblock_users_menu(message: types.Message):
    blocked_users = await get_blocked_users(message.from_user.id)
    if blocked_users:
        buttons = [types.InlineKeyboardButton(text=user[1], callback_data=f"unblock_{user[0]}") for user in blocked_users]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[btn] for btn in buttons])
        await message.answer("Выберите пользователя для разблокировки:", reply_markup=keyboard)
    else:
        await message.answer("Нет заблокированных пользователей.")


@settings_router.callback_query(F.data.startswith('unblock_'))
async def unblock_user_handler(callback_query: types.CallbackQuery):
    user_id = int(callback_query.data.split('_')[1])
    await unblock_user(callback_query.from_user.id, user_id)
    await callback_query.message.answer("Пользователь разблокирован.", reply_markup=initial_keyboard())

