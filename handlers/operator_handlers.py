from aiogram import Router, types
from aiogram.filters import Command

operator_router = Router()

# Команда для операторов (пример)
@operator_router.message(Command(commands=['operator']))
async def operator_panel(message: types.Message):
    await message.answer("This is the operator panel.")
