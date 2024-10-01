import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.bot import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Router
from dotenv import load_dotenv
from database import init_db
from database import get_user_by_id, create_user, update_user_language
from handlers.user_handlers import user_router
from handlers.admin_handlers import admin_router
from handlers.operator_handlers import operator_router
from handlers.moderator_handlers import moderator_router

# Загрузка переменных окружения из файла .env
load_dotenv()

API_TOKEN = os.getenv('BOT_TOKEN')

# Создание бота и диспетчера
bot = Bot(token=API_TOKEN, session=AiohttpSession(), default=DefaultBotProperties(parse_mode='HTML'))
dp = Dispatcher(storage=MemoryStorage())

# Подключение маршрутизаторов (routers)
dp.include_router(user_router)
dp.include_router(admin_router)
dp.include_router(operator_router)
dp.include_router(moderator_router)

async def main():
    # Инициализация базы данных
    await init_db()
    # Запуск polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
