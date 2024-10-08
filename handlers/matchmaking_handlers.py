import logging
import os
from math import radians, sin, cos, sqrt, atan2
from aiogram import F
from aiogram.types import FSInputFile
from aiogram import Router, types, Bot
from aiogram.fsm.context import FSMContext
from database import (
    add_finished_chat,
    block_user,
    get_user_by_id, 
    add_to_waiting_list, 
    find_match,
    get_user_interests,
    remove_from_waiting_list,
    save_chat_message_to_db,  # Добавляем функцию для сохранения сообщений в БД
    add_active_chat,           # Добавляем функцию для добавления активного чата в БД
    remove_active_chat,        # Добавляем функцию для удаления активного чата из БД
    get_active_chat   # Добавляем функцию для сохранения сообщений в БД
)
from keyboards import initial_keyboard, search_keyboard, match_keyboard
from localization import translate  # Импорт функции для перевода интересов
from aiogram.filters import Command
from utils import calculate_distance


# Путь для сохранения медиафайлов
MEDIA_PATH = 'media_files/'
if not os.path.exists(MEDIA_PATH):
    os.makedirs(MEDIA_PATH)

matchmaking_router = Router()

# Функция для получения общих интересов
def get_common_interests(user_interests, match_interests):
    return list(set(user_interests) & set(match_interests))

# Функция для перевода интересов на нужный язык
def translate_interests(interests, lang_code):
    return [translate(interest.lower(), lang_code) for interest in interests]

# Модификация функции для запуска поиска партнера с проверкой на активные чаты
async def start_matchmaking(user_id, username, gender, orientation, interests, location):
    await add_to_waiting_list(user_id, username, gender, orientation, interests, location)

    # Пытаемся найти совпадение, исключая пользователей, которые уже находятся в активных чатах
    match = await find_match(user_id, gender, orientation, interests, location)
    
    # Проверка, чтобы найденный пользователь не был занят в активном чате
    if match:
        active_chat = await get_active_chat(match['user_id'])
        if not active_chat:
            return match['user_id'], match['username']
    return None, None

@matchmaking_router.message(F.text == '🔍 Поиск')
async def handle_find_match_button(message: types.Message, bot: Bot):
    user = await get_user_by_id(message.from_user.id)
    if user:
        gender = user['gender']
        orientation = user['orientation']
        user_interests = await get_user_interests(user['user_id'])
        location = user['location']
        username = user['username']
        lang_code = user['lang']  # Получаем язык пользователя

        # Отправляем сообщение, что поиск начат, и меняем клавиатуру
        await message.answer("Поиск начат, пожалуйста, подождите...", reply_markup=search_keyboard())

        match_user_id, match_username = await start_matchmaking(user['user_id'], username, gender, orientation, ', '.join(user_interests), location)

        if match_user_id and match_username:
            # Получаем данные для найденного пользователя
            match_user = await get_user_by_id(match_user_id)
            match_interests = await get_user_interests(match_user_id)
            match_location = match_user['location']
            match_lang_code = match_user['lang']  # Язык найденного пользователя

            # Определяем общие интересы
            common_interests = get_common_interests(user_interests, match_interests)

            # Переводим общие интересы на язык пользователя
            translated_common_interests = translate_interests(common_interests, lang_code)

            # Разделяем координаты на широту и долготу
            user_lat, user_lon = map(float, location.split(','))
            match_lat, match_lon = map(float, match_location.split(','))

            # Вычисляем расстояние между пользователями
            distance = calculate_distance(user_lat, user_lon, match_lat, match_lon)

            # Сохраняем информацию о чате между пользователями
            await add_active_chat(message.from_user.id, match_user_id)

            # Формируем ответное сообщение с общей информацией
            match_info = (
                f"Найдено совпадение с пользователем: {match_username}.\n"
                f"Общие интересы: {', '.join(translated_common_interests) if common_interests else 'Нет общих интересов'}.\n"
                f"Расстояние между вами: {distance:.2f} км.\n"
                f"Вы можете начать общение."
            )
            await message.answer(match_info, reply_markup=match_keyboard())  # Переход на клавиатуру для чата
            await bot.send_message(match_user_id, f"У вас есть совпадение с пользователем: {user['username']}.\n"
                                                 f"Общие интересы: {', '.join(translate_interests(common_interests, match_lang_code)) if common_interests else 'Нет общих интересов'}.\n"
                                                 f"Расстояние между вами: {distance:.2f} км.\n"
                                                 f"Вы можете начать общение.", reply_markup=match_keyboard())
        else:
            await message.answer("Извините, не удалось найти совпадение.", reply_markup=initial_keyboard())
    else:
        await message.answer("Пользователь не найден. Попробуйте зарегистрироваться заново.")


# Обработка нажатия кнопки "Покинуть поиск"
@matchmaking_router.message(F.text == '🚪 Покинуть поиск')
async def handle_leave_match_button(message: types.Message):
    user = await get_user_by_id(message.from_user.id)
    if user:
        await remove_from_waiting_list(user['user_id'])
        await message.answer("Вы вышли из поиска.", reply_markup=initial_keyboard())
    else:
        await message.answer("Пользователь не найден. Попробуйте зарегистрироваться заново.")


@matchmaking_router.message(F.text == '❌ Выйти из чата')
async def handle_exit_chat_button(message: types.Message, bot: Bot):
    user_id = message.from_user.id
    active_chat = await get_active_chat(user_id)
    if active_chat:
        partner_id = active_chat['partner_id']

        # Добавляем завершенные чаты в таблицу
        await add_finished_chat(user_id, partner_id)
        await add_finished_chat(partner_id, user_id)

        # Удаляем пользователей из активных чатов
        await remove_active_chat(user_id)

        # Оповещаем обе стороны о завершении чата
        await message.answer("Вы завершили чат.", reply_markup=search_keyboard())
        await bot.send_message(partner_id, "Ваш собеседник завершил чат.", reply_markup=search_keyboard())
    else:
        await message.answer("Вы не находитесь в чате.")

# Функция для блокировки пользователя
@matchmaking_router.message(F.text == '🚫 Заблокировать')
async def handle_block_user_button(message: types.Message, bot: Bot):
    user_id = message.from_user.id
    active_chat = await get_active_chat(user_id)
    if active_chat:
        partner_id = active_chat['partner_id']

        # Блокируем пользователя
        await block_user(user_id, partner_id)

        # Удаляем пользователей из активных чатов из БД
        await remove_active_chat(user_id)

        # Оповещаем обе стороны о блокировке
        await message.answer("Вы заблокировали пользователя и завершили чат.", reply_markup=search_keyboard())
        await bot.send_message(partner_id, "Ваш собеседник заблокировал вас и завершил чат.", reply_markup=search_keyboard())
    else:
        await message.answer("Вы не находитесь в активном чате.")

        
# Функция для сохранения медиафайлов
async def save_media_file(file_id: str, file_type: str, message_id: int, user_id: int, bot: Bot):
    file_info = await bot.get_file(file_id)
    extension = file_type if file_type != "voice" else "ogg"  # Голосовые сохраняем как .ogg
    file_name = f"{message_id}_{user_id}.{extension}"
    file_path = os.path.join(MEDIA_PATH, file_name)

    # Сохраняем файл на диск
    await bot.download_file(file_info.file_path, file_path)
    return file_path

# Обработка сообщений и медиафайлов между пользователями в чате
@matchmaking_router.message(F.text | F.photo | F.video | F.audio | F.voice | F.animation | F.video_note)
async def relay_message(message: types.Message, bot: Bot):
    user_id = message.from_user.id
    active_chat = await get_active_chat(user_id)

    # Проверяем, есть ли активный чат для пользователя
    if active_chat:
        partner_id = active_chat['partner_id']
        # Сохраняем сообщение в базе данных
        if message.text:
            # Сохраняем текстовое сообщение
            await save_chat_message_to_db(user_id, partner_id, message.message_id, message.text, 'text')
            await bot.send_message(partner_id, message.text)
        
        # Сохраняем и пересылаем фото
        elif message.photo:
            file_id = message.photo[-1].file_id
            file_path = await save_media_file(file_id, "jpg", message.message_id, user_id, bot)
            await save_chat_message_to_db(user_id, partner_id, message.message_id, file_path, 'photo')
            await bot.send_photo(partner_id, file_id, caption=message.caption)

        # Сохраняем и пересылаем видео
        elif message.video:
            file_id = message.video.file_id
            file_path = await save_media_file(file_id, "mp4", message.message_id, user_id, bot)
            await save_chat_message_to_db(user_id, partner_id, message.message_id, file_path, 'video')
            await bot.send_video(partner_id, file_id, caption=message.caption)

        # Сохраняем и пересылаем аудио
        elif message.audio:
            file_id = message.audio.file_id
            file_path = await save_media_file(file_id, "mp3", message.message_id, user_id, bot)
            await save_chat_message_to_db(user_id, partner_id, message.message_id, file_path, 'audio')
            await bot.send_audio(partner_id, file_id, caption=message.caption)

        # Сохраняем и пересылаем голосовые сообщения
        elif message.voice:
            file_id = message.voice.file_id
            file_path = await save_media_file(file_id, "ogg", message.message_id, user_id, bot)
            await save_chat_message_to_db(user_id, partner_id, message.message_id, file_path, 'voice')
            await bot.send_voice(partner_id, file_id)

        # Сохраняем и пересылаем анимацию (GIF)
        elif message.animation:
            file_id = message.animation.file_id
            file_path = await save_media_file(file_id, "gif", message.message_id, user_id, bot)
            await save_chat_message_to_db(user_id, partner_id, message.message_id, file_path, 'animation')
            await bot.send_animation(partner_id, file_id, caption=message.caption)

        # Сохраняем и пересылаем видео-заметки (кружки)
        elif message.video_note:
            file_id = message.video_note.file_id
            file_path = await save_media_file(file_id, "mp4", message.message_id, user_id, bot)
            await save_chat_message_to_db(user_id, partner_id, message.message_id, file_path, 'video_note')
            await bot.send_video_note(partner_id, file_id)
    
    else:
        await message.answer("Вы не в чате. Найдите партнера для общения, чтобы начать чат.")