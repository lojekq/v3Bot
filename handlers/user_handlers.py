import logging
from aiogram import Router, types, Bot
from aiogram import F
from aiogram.types import FSInputFile, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from database import get_user_by_id, get_user_interests, get_user_language
from handlers.settings_handlers import CUSTOM_INTERESTS_LIST
from localization import translate
from aiogram.filters import Command
from handlers.registration_handlers import start_registration
from handlers.matchmaking_handlers import handle_find_match_button, handle_leave_match_button
from handlers.registration_handlers import registration_router
from keyboards import initial_keyboard, search_keyboard, match_keyboard
user_router = Router()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,  # Вывод всех сообщений уровня INFO и выше
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]  # Вывод логов в консоль
)

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


@user_router.message(Command(commands=['start']))
async def on_start_command(message: types.Message, state: FSMContext, bot: Bot):
    user = await get_user_by_id(message.from_user.id)

    if user:
        lang_code = user.get('lang', 'en')  # Проверь, корректен ли этот код языка
        welcome_message = translate('welcome_back', lang_code)
        await message.answer(welcome_message, reply_markup=initial_keyboard())
    else:
        await start_registration(message, state, bot)

        return
    


# Обработка нажатия кнопки "Показать профиль"
@user_router.message(F.text == '👤 Показать профиль')
async def handle_show_profile_button(message: types.Message, bot: Bot):
    await show_profile(message, bot)

# Показ профиля
async def show_profile(message: types.Message, bot: Bot):
    user = await get_user_by_id(message.from_user.id)
    if user:
        lang_code = await get_user_language(message.from_user.id)
        gender_key = GENDER_MAP.get(user.get('gender', 'Other'), 'gender_other')
        gender = translate(gender_key, lang_code)
        orientation_key = ORIENTATION_MAP.get(user.get('orientation', 'Heterosexual'), 'orientation_heterosexual')
        orientation = translate(orientation_key, lang_code)
        nickname = user.get('username', 'N/A')
        interests_list = await get_user_interests(message.from_user.id)

        # Перевод интересов с использованием translate()
        if interests_list:
            interests_str = ', '.join([translate(CUSTOM_INTERESTS_LIST.get(interest, {}).get(lang_code, interest), lang_code) for interest in interests_list])
        else:
            interests_str = translate('no_interests', lang_code)

        location = user.get('location', 'N/A')
        profile_info = (
            f"👤 {translate('nickname', lang_code)}: {nickname}\n"
            f"🚻 {translate('gender', lang_code)}: {gender}\n"
            f"🎯 {translate('orientation', lang_code)}: {orientation}\n"
            f"📚 {translate('interests', lang_code)}: {interests_str}\n"
        )
        
        media_path = user.get('profile_photo')
        if media_path:
            try:
                input_file = FSInputFile(media_path)
                if media_path.endswith('.mp4'):
                    await bot.send_video(message.chat.id, input_file, caption=profile_info)
                elif media_path.endswith('.gif'):
                    await bot.send_animation(message.chat.id, input_file, caption=profile_info)
                else:
                    await bot.send_photo(message.chat.id, input_file, caption=profile_info)
            except Exception as e:
                await message.answer(f"Ошибка при отправке медиа: {e}")
        else:
            await message.answer(profile_info)
    else:
        await message.answer("Пользователь не найден. Попробуйте зарегистрироваться заново.")






