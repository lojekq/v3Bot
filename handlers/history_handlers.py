import logging
from aiogram import F, Bot, Router, types
from database import block_user, get_active_chat, get_chat_history, get_finished_chats, add_active_chat, remove_active_chat  # Новые функции для работы с активными чатами
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from keyboards import initial_keyboard

history_router = Router()
logging.basicConfig(level=logging.INFO)

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
    keyboard = InlineKeyboardMarkup(row_width=2)
    accept_button = InlineKeyboardButton(text="Принять", callback_data="accept_chat")
    decline_button = InlineKeyboardButton(text="Отклонить", callback_data="decline_chat")
    keyboard.add(accept_button, decline_button)
    return keyboard

@history_router.callback_query(F.data.startswith('open_chat_'))
async def handle_open_chat(callback_query: types.CallbackQuery):
    partner_id = int(callback_query.data.split('_')[2])
    user_id = callback_query.from_user.id

    # Получение всех сообщений чата
    chat_history = await get_chat_history(user_id, partner_id)

    if chat_history:
        for message in chat_history:
            if message['type'] == 'text':
                await callback_query.message.answer(message['content'])
            elif message['type'] == 'photo':
                await callback_query.message.answer_photo(message['content'])
            elif message['type'] == 'video':
                await callback_query.message.answer_video(message['content'])
            # Добавляем обработку других типов сообщений (видео, аудио и т.д.)
        
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
    partner_id = int(callback_query.data.split('_')[2])  # Получаем partner_id из callback_data

    logging.info(f"User {user_id} is attempting to continue chat with partner {partner_id}")

    # Проверка, есть ли уже активный чат
    active_chat = await get_active_chat(user_id)

    if active_chat:
        await callback_query.message.answer("Вы уже находитесь в активном чате.")
        return

    try:
        # Сохраняем новый активный чат в базу данных
        await add_active_chat(user_id, partner_id)
        await add_active_chat(partner_id, user_id)

        # Отправляем предложение продолжить чат партнеру
        await bot.send_message(
            partner_id, 
            "Ваш собеседник предложил продолжить чат.", 
            reply_markup=accept_or_decline_keyboard()
        )
        
        # Сообщаем пользователю, что запрос отправлен
        await callback_query.message.answer("Запрос на продолжение чата отправлен.")
    except Exception as e:
        logging.error(f"Ошибка при отправке сообщения о продолжении чата: {e}")
        await callback_query.message.answer("Произошла ошибка при отправке запроса.")

# Обработка принятия или отклонения продолжения чата
@history_router.callback_query(F.data == "accept_chat")
async def accept_chat(callback_query: types.CallbackQuery):
    await callback_query.message.answer("Вы приняли продолжение чата.")
    # Логика для возобновления чата

@history_router.callback_query(F.data == "decline_chat")
async def decline_chat(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    partner_id = (await get_active_chat(user_id))['partner_id']

    # Удаляем активный чат из базы данных
    await remove_active_chat(user_id)
    await remove_active_chat(partner_id)

    await callback_query.message.answer("Вы отклонили продолжение чата. Чат завершён.")

# Обработка блокировки пользователя
@history_router.callback_query(F.data.startswith('block_user_'))
async def handle_block_user(callback_query: types.CallbackQuery):
    partner_id = int(callback_query.data.split('_')[2])
    await block_user(callback_query.from_user.id, partner_id)  # Блокируем пользователя
    await remove_active_chat(callback_query.from_user.id)  # Удаляем активный чат
    await callback_query.message.answer(f"Вы заблокировали пользователя {partner_id}")

# Обработка возврата в меню
@history_router.callback_query(F.data == 'back_to_menu')
async def handle_back_to_menu(callback_query: types.CallbackQuery):
    await callback_query.message.answer("Вы вернулись в главное меню.", reply_markup=initial_keyboard())
