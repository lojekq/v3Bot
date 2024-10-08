import os
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.bot import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from database import check_db_connection, init_db, close_db  # Импорт функций работы с базой данных
from handlers.user_handlers import user_router
from handlers.admin_handlers import admin_router
from handlers.operator_handlers import operator_router
from handlers.moderator_handlers import moderator_router
from handlers.registration_handlers import registration_router
from handlers.history_handlers import history_router
from handlers.matchmaking_handlers import matchmaking_router
from handlers.settings_handlers import settings_router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,  # Вывод всех сообщений уровня INFO и выше
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]  # Вывод логов в консоль
)

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
dp.include_router(settings_router)
dp.include_router(registration_router)
dp.include_router(history_router)
dp.include_router(matchmaking_router)


async def start_bot():
    # Инициализация базы данных
    await init_db()

    # Проверка соединения перед использованием базы данных
    await check_db_connection()

    # Запуск polling
    await dp.start_polling(bot)

async def main():
    try:
        # Инициализация базы данных
        await init_db()

        # Проверка соединения перед использованием базы данных
        await check_db_connection()
        from database import db
        if db is None:
            logging.error("Database connection is not initialized")
            return
        else:
            logging.info("Database connection successfully initialized")
        
        # Добавьте логирование состояния db
        logging.info(f"Current db state: {db}")

        # Запуск polling
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        # Закрытие соединения с базой данных только после завершения работы бота
        await close_db()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
