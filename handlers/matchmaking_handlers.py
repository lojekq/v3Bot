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
)
from aiogram.filters import Command
from database import db, check_db_connection  # Импорт функции проверки соединения

matchmaking_router = Router()

# Функция для поиска собеседника
async def start_search(message, user_gender, user_orientation, user_interests, user_location):
    from database import db
    logging.info(f"Current db state inside start_search: {db}")
    if db is None:
        raise ValueError("Database connection is not initialized")
    await check_db_connection()  # Проверка соединения перед использованием

    if db is None:
        raise ValueError("Database connection is not initialized")

    async with db.acquire() as conn:
        async with conn.cursor() as cursor:
            match_user_id = await find_match(message.from_user.id, user_gender, user_orientation, user_interests, user_location)
            if match_user_id:
                match_user_id_value = match_user_id['user_id']
                await cursor.execute("DELETE FROM waiting_list WHERE user_id IN (%s, %s)", (message.from_user.id, match_user_id_value))
                await conn.commit()
                return match_user_id_value

            return None



# Обработка команды /find_match для поиска собеседника
@matchmaking_router.message(Command(commands=['find_match']))
async def handle_find_match(message: types.Message, state: FSMContext, bot: Bot):
    from database import db  # Добавляем глобальную переменную
    logging.info(f"Current db state before calling start_search: {db}")
    user = await get_user_by_id(message.from_user.id)

    if not user:
        await message.answer("Пожалуйста, завершите регистрацию, прежде чем искать собеседника.")
        return

    user_gender = user['gender']
    user_orientation = user['orientation']
    user_interests = user['interests']
    user_location = user['location']

    try:
        # Ищем подходящего собеседника по полу и ориентации
        match_user_id = await find_match(message.from_user.id, user_gender, user_orientation, user_interests, user_location)

        if match_user_id:
            # Получаем информацию о найденном пользователе
            match_user = await get_user_by_id(match_user_id['user_id'])

            # Отправляем сообщение обеим сторонам с указанием ников
            await bot.send_message(match_user['user_id'], "Мы нашли для вас собеседника!")
            await bot.send_message(message.from_user.id, "Мы нашли для вас собеседника!")

            # Передаем ники пользователей
            await start_private_chat(bot, message.from_user.id, match_user['user_id'], user['username'], match_user['username'])

        else:
            # Если собеседник не найден, добавляем пользователя в очередь
            await add_to_waiting_list(message.from_user.id, user_gender, user_orientation, user_interests, user_location)
            await message.answer("Сейчас нет подходящих собеседников. Мы уведомим вас, как только кто-то появится.")
    except ValueError as e:
        await message.answer(f"Ошибка: {str(e)}")
        logging.error(f"Ошибка при поиске собеседника: {str(e)}")


# Функция для организации чата между двумя пользователями с указанием ников
async def start_private_chat(bot: Bot, user_id1, user_id2, user1_nickname, user2_nickname):
    # Отправляем сообщения о начале чата с указанием ников
    await bot.send_message(user_id1, f"Чат начат с пользователем: {user2_nickname}")
    await bot.send_message(user_id2, f"Чат начат с пользователем: {user1_nickname}")




