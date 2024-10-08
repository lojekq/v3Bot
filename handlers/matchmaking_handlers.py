import logging
import os
from aiogram import F
from aiogram.types import FSInputFile
from aiogram import Router, types, Bot
from aiogram.fsm.context import FSMContext
from database import (
    get_user_by_id, 
    add_to_waiting_list, 
    find_match,
    get_user_interests,
    remove_from_waiting_list,
)
from aiogram.filters import Command
from database import db, check_db_connection  # Импорт функции проверки соединения

matchmaking_router = Router()

# Функция для запуска поиска партнера
async def start_matchmaking(user_id, username, gender, orientation, interests, location):
    await add_to_waiting_list(user_id, username, gender, orientation, interests, location)

    match = await find_match(user_id, gender, orientation, interests, location)
    
    if match:
        return match['user_id'], match['username']
    else:
        return None, None

# Обработка нажатия кнопки "Поиск"
@matchmaking_router.message(F.text == '🔍 Поиск')
async def handle_find_match_button(message: types.Message, bot: Bot):
    user = await get_user_by_id(message.from_user.id)
    if user:
        gender = user['gender']
        orientation = user['orientation']
        interests = ', '.join(await get_user_interests(user['user_id']))
        location = user['location']
        username = user['username']

        match_user_id, match_username = await start_matchmaking(user['user_id'], username, gender, orientation, interests, location)

        if match_user_id and match_username:
            await message.answer(f"Найдено совпадение с пользователем: {match_username}")
            await bot.send_message(match_user_id, f"У вас есть совпадение с пользователем: {user['username']}")
        else:
            await message.answer("Извините, не удалось найти совпадение.")
    else:
        await message.answer("Пользователь не найден. Попробуйте зарегистрироваться заново.")

# Обработка нажатия кнопки "Покинуть поиск"
@matchmaking_router.message(F.text == '🚪 Покинуть поиск')
async def handle_leave_match_button(message: types.Message):
    user = await get_user_by_id(message.from_user.id)
    if user:
        await remove_from_waiting_list(user['user_id'])
        await message.answer("Вы вышли из поиска.")
    else:
        await message.answer("Пользователь не найден. Попробуйте зарегистрироваться заново.")


# Функция для организации чата между двумя пользователями с указанием ников
async def start_private_chat(bot: Bot, user_id1, user_id2, user1_nickname, user2_nickname):
    # Отправляем сообщения о начале чата с указанием ников
    await bot.send_message(user_id1, f"Чат начат с пользователем: {user2_nickname}")
    await bot.send_message(user_id2, f"Чат начат с пользователем: {user1_nickname}")




