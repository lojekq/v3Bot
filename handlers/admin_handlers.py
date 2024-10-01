from aiogram import Router, types
from aiogram.filters import Command
from database import get_user_by_id

admin_router = Router()

# Команда для администраторов (пример)
@admin_router.message(Command(commands=['admin']))
async def admin_panel(message: types.Message):
    await message.answer("This is the admin panel.")
