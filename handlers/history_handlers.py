import logging
import os
from aiogram import F, Bot, Router, types
from database import block_user, get_active_chat, add_active_chat, get_user_by_id, remove_active_chat, get_chat_history, get_finished_chats  # Обновление для работы с активными чатами в БД
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile

from keyboards import initial_keyboard, match_keyboard

history_router = Router()
logging.basicConfig(level=logging.INFO)

# Путь для сохранения медиафайлов
MEDIA_PATH = 'media_files/'
if not os.path.exists(MEDIA_PATH):
    os.makedirs(MEDIA_PATH)

# Функция для сохранения медиафайлов
async def save_media_file(file_id: str, file_type: str, message_id: int, user_id: int, bot: Bot):
    file_info = await bot.get_file(file_id)
    extension = file_type if file_type != "voice" else "ogg"
    file_name = f"{message_id}_{user_id}.{extension}"
    file_path = os.path.join(MEDIA_PATH, file_name)
    await bot.download_file(file_info.file_path, file_path)
    return file_path

# Обработка кнопки "История"
@history_router.message(F.text == '📜 История')
async def handle_history_button(message: types.Message):
    user_id = message.from_user.id
    finished_chats = await get_finished_chats(user_id)
    
    if finished_chats:
        for chat in finished_chats:
            partner_username = chat['username']
            partner_id = chat['partner_id']
            
            # Кнопка открытия чата
            open_chat_button = InlineKeyboardButton(text=f"Открыть чат с {partner_username}", callback_data=f"open_chat_{partner_id}")
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[open_chat_button]])
            
            await message.answer(f"Завершённый чат с {partner_username}", reply_markup=keyboard)
    else:
        await message.answer("У вас нет завершённых чатов.")

# Клавиатура с предложением продолжить чат
def accept_or_decline_keyboard():
    accept_button = InlineKeyboardButton(text="Принять", callback_data="accept_chat")
    decline_button = InlineKeyboardButton(text="Отклонить", callback_data="decline_chat")
    
    # Добавляем кнопки в inline_keyboard
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[accept_button, decline_button]])
    return keyboard

@history_router.callback_query(F.data.startswith('open_chat_'))
async def handle_open_chat(callback_query: types.CallbackQuery, bot: Bot):
    partner_id = int(callback_query.data.split('_')[2])
    user_id = callback_query.from_user.id

    user_data = await get_user_by_id(user_id)
    partner_data = await get_user_by_id(partner_id)

    user_name = user_data['username'] if user_data else "Вы"
    partner_name = partner_data['username'] if partner_data else "Собеседник"

    chat_history = await get_chat_history(user_id, partner_id)

    if chat_history:
        for message in chat_history:
            sender_name = user_name if message['sender_id'] == user_id else partner_name
            try:
                if message['type'] == 'text':
                    await callback_query.message.answer(f"{sender_name}: {message['content']}")
                elif message['type'] == 'photo':
                    if message['content']:
                        await callback_query.message.answer_photo(FSInputFile(message['content']), caption=f"{sender_name}: Фото")
                    else:
                        await callback_query.message.answer(f"{sender_name}: Фото (файл отсутствует)")
                elif message['type'] == 'video':
                    if os.path.exists(message['content']):
                        await callback_query.message.answer_video(FSInputFile(message['content']), caption=f"{sender_name}: Видео")
                    else:
                        await callback_query.message.answer(f"{sender_name}: Видео (файл отсутствует)")
                elif message['type'] == 'audio':
                    if os.path.exists(message['content']):
                        await callback_query.message.answer_audio(FSInputFile(message['content']), caption=f"{sender_name}: Аудио")
                    else:
                        await callback_query.message.answer(f"{sender_name}: Аудио (файл отсутствует)")
                elif message['type'] == 'voice':
                    if os.path.exists(message['content']):
                        await callback_query.message.answer_voice(FSInputFile(message['content']), caption=f"{sender_name}: Голосовое сообщение")
                    else:
                        await callback_query.message.answer(f"{sender_name}: Голосовое сообщение (файл отсутствует)")
                elif message['type'] == 'animation':
                    if os.path.exists(message['content']):
                        await callback_query.message.answer_animation(FSInputFile(message['content']), caption=f"{sender_name}: Анимация")
                    else:
                        await callback_query.message.answer(f"{sender_name}: Анимация (файл отсутствует)")
                elif message['type'] == 'video_note':
                    if os.path.exists(message['content']):
                        await callback_query.message.answer_video_note(FSInputFile(message['content']), caption=f"{sender_name}: Видео-заметка")
                    else:
                        await callback_query.message.answer(f"{sender_name}: Видео-заметка (файл отсутствует)")
            except Exception as e:
                logging.error(f"Ошибка при отправке медиафайла: {e}")
                await callback_query.message.answer(f"{sender_name}: Медиафайл недоступен")

        # Кнопки: продолжить чат, заблокировать и вернуться
        buttons = [
            [InlineKeyboardButton(text="Продолжить чат", callback_data=f"continue_chat_{partner_id}")],
            [InlineKeyboardButton(text="Заблокировать", callback_data=f"block_user_{partner_id}")],
            [InlineKeyboardButton(text="Вернуться в меню", callback_data="back_to_menu")]
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        await callback_query.message.answer("Что вы хотите сделать?", reply_markup=keyboard)
    else:
        await callback_query.message.answer("История чата пуста.")


# Обработка предложения продолжить чат
@history_router.callback_query(F.data.startswith('continue_chat_'))
async def handle_continue_chat(callback_query: types.CallbackQuery, bot: Bot):
    user_id = callback_query.from_user.id
    partner_id = int(callback_query.data.split('_')[2])

    logging.info(f"User {user_id} is attempting to continue chat with partner {partner_id}")

    # Проверяем, есть ли активный чат для пользователя
    active_chat = await get_active_chat(user_id)
    user_data = await get_user_by_id(user_id)
    user_name = user_data['username'] if user_data else "Собеседник"
    
    if active_chat:
        try:
            logging.info(f"Sending message to partner_id {partner_id}")

            # Отправляем предложение продолжить чат партнеру
            await bot.send_message(
                partner_id, 
                f"{user_name} предложил продолжить чат.", 
                reply_markup=accept_or_decline_keyboard()
            )
            
            # Сообщаем пользователю, что запрос отправлен
            await callback_query.message.answer("Запрос на продолжение чата отправлен.")
        except Exception as e:
            logging.error(f"Ошибка при отправке сообщения о продолжении чата: {e}")
            await callback_query.message.answer("Произошла ошибка при отправке запроса.")
    else:
        await callback_query.message.answer("Чат с этим пользователем не найден.")



@history_router.callback_query(F.data == "accept_chat")
async def accept_chat(callback_query: types.CallbackQuery, bot: Bot):
    user_id = callback_query.from_user.id
    active_chat = await get_active_chat(user_id)

    if active_chat:
        partner_id = active_chat['partner_id']
        
        # Логируем для отладки
        logging.info(f"User ID: {user_id}, Partner ID: {partner_id}")

        if user_id == partner_id:
            logging.error("User and partner IDs are identical, check your chat logic.")
            await callback_query.message.answer("Произошла ошибка, попробуйте позже.")
            return

        # Подтверждаем продолжение чата
        await add_active_chat(user_id, partner_id)
        await add_active_chat(partner_id, user_id)

        # Отправляем уведомления
        await callback_query.message.answer("Вы приняли продолжение чата. Теперь можете отправлять сообщения.", reply_markup=match_keyboard())
        await bot.send_message(partner_id, "Ваш собеседник принял продолжение чата. Теперь можете отправлять сообщения.", reply_markup=match_keyboard())
    else:
        logging.error("Не удалось найти активный чат.")




@history_router.callback_query(F.data == "decline_chat")
async def decline_chat(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    # Удаляем активный чат, если пользователь отклоняет
    await remove_active_chat(user_id)
    await callback_query.message.answer("Вы отклонили продолжение чата.")
    # Завершаем процесс


@history_router.callback_query(F.data.startswith('block_user_'))
async def handle_block_user(callback_query: types.CallbackQuery):
    partner_id = int(callback_query.data.split('_')[2])
    await block_user(callback_query.from_user.id, partner_id)  # Блокируем пользователя

    # Удаляем чат после блокировки
    await remove_active_chat(callback_query.from_user.id)
    await callback_query.message.answer(f"Вы заблокировали пользователя {partner_id}")


@history_router.callback_query(F.data == 'back_to_menu')
async def handle_back_to_menu(callback_query: types.CallbackQuery):
    await callback_query.message.answer("Вы вернулись в главное меню.", reply_markup=initial_keyboard())
