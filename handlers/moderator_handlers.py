from aiogram import Router, types
from aiogram.filters import Command

moderator_router = Router()

# Команда для модераторов (пример)
@moderator_router.message(Command(commands=['moderator']))
async def moderator_panel(message: types.Message):
    await message.answer("This is the moderator panel.")
