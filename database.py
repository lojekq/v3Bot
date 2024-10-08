import logging
import os
import aiomysql
from dotenv import load_dotenv

db = None  # Глобальная переменная для пула соединений

# Загрузка переменных окружения
load_dotenv()

# Инициализация базы данных
async def init_db():
    global db
    if db is None:
        db = await aiomysql.create_pool(
            host=os.getenv('DB_HOST'),
            port=3306,
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            db=os.getenv('DB_NAME'),
            autocommit=True
        )
        logging.info("Database connection successfully initialized")
    else:
        logging.warning("Database connection is already initialized")

# Закрытие базы данных
async def close_db():
    global db
    if db is not None:
        logging.info("Closing database connection...")
        db.close()  # Закрываем пул соединений
        await db.wait_closed()
        db = None  # Обнуляем переменную после закрытия
        logging.info("Database connection closed")

# Проверка перед использованием базы данных
async def check_db_connection():
    global db
    if db is None:
        logging.error("Database connection is not initialized (check_db_connection)")
        raise ValueError("Database connection is not initialized")
    else:
        logging.info(f"Database connection is active (check_db_connection), current db: {db}")



# Пример вызова перед использованием базы данных
async def check_db_connection():
    global db
    if db is None or db._closed:
        logging.error("Database connection is not initialized or already closed")
        raise ValueError("Database connection is not initialized or already closed")
    else:
        logging.info("Database connection is active")

# Добавьте создание таблицы пользователей в отдельную функцию
async def create_user_table():
    global db
    async with db.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    username VARCHAR(255) NOT NULL,
                    gender VARCHAR(50),
                    orientation VARCHAR(50),
                    interests TEXT,
                    location VARCHAR(255),
                    lang VARCHAR(10) DEFAULT 'en',
                    profile_photo VARCHAR(255),
                    age INT,
                    birth_year INT,
                    ban_until INT,
                    custom_gender VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await conn.commit()


# Функция создания пользователя
async def create_user(user_id, username):
    async with db.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "INSERT INTO users (user_id, username) VALUES (%s, %s)", 
                (user_id, username)
            )
            await conn.commit()

# Получение пользователя по его ID
async def get_user_by_id(user_id):
    async with db.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
            return await cursor.fetchone()

# Обновление языка пользователя
async def update_user_language(user_id, lang_code):
    async with db.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("UPDATE users SET lang = %s WHERE user_id = %s", (lang_code, user_id))
            await conn.commit()

# Обновление пола пользователя
async def update_user_gender(user_id, gender):
    async with db.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("UPDATE users SET gender = %s WHERE user_id = %s", (gender, user_id))
            await conn.commit()

# Обновление ориентации пользователя
async def update_user_orientation(user_id, orientation):
    async with db.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("UPDATE users SET orientation = %s WHERE user_id = %s", (orientation, user_id))
            await conn.commit()

# Функция для получения интересов пользователя из новой таблицы
async def get_user_interests(user_id):
    async with db.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("SELECT interest FROM user_interests WHERE user_id = %s", (user_id,))
            interests = await cursor.fetchall()
            return [row['interest'] for row in interests]  # Возвращаем список интересов


# Обновление интересов пользователя (добавление новых интересов)
async def update_user_interests(user_id, interests):
    async with db.acquire() as conn:
        async with conn.cursor() as cursor:
            # Сначала удаляем старые интересы пользователя
            await cursor.execute("DELETE FROM user_interests WHERE user_id = %s", (user_id,))
            await conn.commit()

            # Затем добавляем новые интересы
            for interest in interests:
                await cursor.execute(
                    "INSERT INTO user_interests (user_id, interest) VALUES (%s, %s)", 
                    (user_id, interest)
                )
            await conn.commit()

# Обновление возраста пользователя
async def update_user_age(user_id, age):
    async with db.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("UPDATE users SET age = %s WHERE user_id = %s", (age, user_id))
            await conn.commit()

# Обновление года рождения пользователя
async def update_user_birth_year(user_id, birth_year):
    async with db.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("UPDATE users SET birth_year = %s WHERE user_id = %s", (birth_year, user_id))
            await conn.commit()

# Обновление срока блокировки пользователя
async def update_user_ban_until(user_id, ban_until):
    async with db.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("UPDATE users SET ban_until = %s WHERE user_id = %s", (ban_until, user_id))
            await conn.commit()

# Обновление фотографии профиля пользователя
async def update_user_photo(user_id, photo_path):
    async with db.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("UPDATE users SET profile_photo = %s WHERE user_id = %s", (photo_path, user_id))
            await conn.commit()

# Обновление местоположения пользователя
async def update_user_location(user_id, location):
    async with db.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("UPDATE users SET location = %s WHERE user_id = %s", (location, user_id))
            await conn.commit()

# Обновление никнейма пользователя
async def update_user_nickname(user_id, nickname):
    async with db.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("UPDATE users SET username = %s WHERE user_id = %s", (nickname, user_id))
            await conn.commit()

# Обновление кастомного пола пользователя
async def update_user_custom_gender(user_id, custom_gender):
    async with db.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("UPDATE users SET gender = 'Other', custom_gender = %s WHERE user_id = %s", (custom_gender, user_id))
            await conn.commit()

# Добавление в список ожидания
async def add_to_waiting_list(user_id, username, gender, orientation, interests, location):
    async with db.acquire() as conn:
        async with conn.cursor() as cursor:
            query = """
                INSERT INTO waiting_list (user_id, username, gender, orientation, interests, location, request_time)
                VALUES (%s, %s, %s, %s, %s, %s, NOW()) AS new_data
                ON DUPLICATE KEY UPDATE
                    username = new_data.username,
                    gender = new_data.gender,
                    orientation = new_data.orientation,
                    interests = new_data.interests,
                    location = new_data.location,
                    request_time = NOW()
            """
            await cursor.execute(query, (user_id, username, gender, orientation, interests, location))
            await conn.commit()



# Поиск совпадений с учетом пола, ориентации и интересов
async def find_match(user_id, gender, orientation, interests, location):
    async with db.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            search_gender = None
            if orientation == 'Heterosexual':
                search_gender = 'Female' if gender == 'Male' else 'Male'
            elif orientation == 'Homosexual' or orientation == 'Lesbian':
                search_gender = gender  # Ищем тот же пол для гомосексуалов и лесбиянок
            elif orientation == 'Bisexual':
                search_gender = None  # Бисексуалы могут искать любой пол

            # Преобразуем интересы в строку для использования в запросе
            interests_list = interests.split(',')
            interests_conditions = " OR ".join([f"interests LIKE %s" for _ in interests_list])
            interests_values = [f"%{interest.strip()}%" for interest in interests_list]

            # Выполняем запрос
            query_exact = f"""
                SELECT user_id, username FROM waiting_list 
                WHERE 
                    gender = %s 
                    AND orientation = %s 
                    AND ({interests_conditions})
                    AND location = %s
                    AND user_id != %s
                LIMIT 1
            """
            params = [search_gender, orientation] + interests_values + [location, user_id]
            await cursor.execute(query_exact, params)
            match = await cursor.fetchone()

            if match:
                return match

            # Если нет полного совпадения, выполняем частичный поиск
            query_partial = f"""
                SELECT user_id, username FROM waiting_list 
                WHERE 
                    gender = %s 
                    AND orientation = %s 
                    AND ({interests_conditions})
                    AND user_id != %s
                LIMIT 1
            """
            params = [search_gender, orientation] + interests_values + [user_id]
            await cursor.execute(query_partial, params)
            match = await cursor.fetchone()

            if match:
                return match

            return None

# Удаление пользователя из списка ожидания
async def remove_from_waiting_list(user_id):
    async with db.acquire() as conn:
        async with conn.cursor() as cursor:
            query = "DELETE FROM waiting_list WHERE user_id = %s"
            await cursor.execute(query, (user_id,))
            await conn.commit()

async def save_chat_message_to_db(sender_id, receiver_id, message_id, content):
    async with db.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "INSERT INTO chat_messages (sender_id, receiver_id, message_id, content) VALUES (%s, %s, %s, %s)",
                (sender_id, receiver_id, message_id, content)
            )
            await conn.commit()


# Получение языка пользователя
async def get_user_language(user_id):
    async with db.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("SELECT lang FROM users WHERE user_id = %s", (user_id,))
            result = await cursor.fetchone()
            if result:
                return result['lang']
            return 'en'  # Язык по умолчанию, если язык не установлен

