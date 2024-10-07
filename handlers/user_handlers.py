import logging
from aiogram import Router, types, Bot
from aiogram import F
from aiogram.types import FSInputFile
from aiogram.fsm.context import FSMContext
from database import get_user_by_id, get_user_interests, get_user_language
from localization import translate
from aiogram.filters import Command
from handlers.registration_handlers import get_show_profile_keyboard, start_registration
from handlers.registration_handlers import registration_router
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
        await message.answer(welcome_message, reply_markup=get_show_profile_keyboard(lang_code))
    else:
        await start_registration(message, state, bot)

        return


# Обработка нажатия кнопки "Показать профиль"
@registration_router.message(F.text.func(lambda text: text in [translate('show_profile', 'en'), translate('show_profile', 'ru'), translate('show_profile', 'kz')]))
async def handle_show_profile(message: types.Message, bot: Bot):
    logging.info(f"Кнопка 'Показать профиль' нажата пользователем {message.from_user.id}")
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





