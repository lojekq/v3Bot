import logging
import os
import aiomysql
from dotenv import load_dotenv

from utils import calculate_distance

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
async def update_user_orientation(user_id: int, orientation: str):
    async with db.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "UPDATE users SET orientation = %s WHERE user_id = %s",
                (orientation, user_id)
            )
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

# Функция для блокировки пользователя
async def block_user(blocker_id, blocked_id):
    async with db.acquire() as conn:
        async with conn.cursor() as cursor:
            # Проверяем, если пользователь уже заблокирован
            query = "SELECT 1 FROM blocked_users WHERE blocker_id = %s AND blocked_id = %s"
            await cursor.execute(query, (blocker_id, blocked_id))
            result = await cursor.fetchone()

            if not result:
                # Если пользователь не заблокирован, добавляем в таблицу
                query = "INSERT INTO blocked_users (blocker_id, blocked_id) VALUES (%s, %s)"
                await cursor.execute(query, (blocker_id, blocked_id))
                await conn.commit()
            else:
                logging.info(f"Пользователь {blocked_id} уже заблокирован пользователем {blocker_id}.")

# Функция добавления завершенного чата
async def add_finished_chat(user_id, partner_id):
    async with db.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            # Проверяем, существует ли уже завершённый чат
            await cursor.execute(
                "SELECT * FROM finished_chats WHERE user_id = %s AND partner_id = %s",
                (user_id, partner_id)
            )
            result = await cursor.fetchone()
            if result:
                logging.info("Запись уже существует, не нужно добавлять снова.")
                return

            # Если записи нет, добавляем её
            query = "INSERT INTO finished_chats (user_id, partner_id) VALUES (%s, %s)"
            await cursor.execute(query, (user_id, partner_id))


# Функция поиска совпадений с учетом завершенных чатов
async def find_match(user_id, gender, orientation, interests, location):
    async with db.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            # Получаем данные пользователя, включая расстояние поиска
            await cursor.execute("SELECT distance FROM users WHERE user_id = %s", (user_id,))
            user_data = await cursor.fetchone()
            max_distance = user_data.get('distance', 10)  # Используем расстояние пользователя или значение по умолчанию 10 км

            user_lat, user_lon = map(float, location.split(','))

            # Определение гендера для поиска
            if orientation == 'Heterosexual':
                search_gender = 'Female' if gender == 'Male' else 'Male'
            elif orientation in ['Homosexual', 'Lesbian']:
                search_gender = gender  # Ищем тот же пол
            else:  # Bisexual or any other
                search_gender = None  # Открытый поиск без учета пола

            # Преобразуем интересы в список
            interests_list = interests.split(',')

            # Запрос для проверки заблокированных пользователей
            blocked_users_query = """
                SELECT blocked_id FROM blocked_users WHERE blocker_id = %s
                UNION
                SELECT blocker_id FROM blocked_users WHERE blocked_id = %s
            """
            await cursor.execute(blocked_users_query, (user_id, user_id))
            blocked_users = [row['blocked_id'] for row in await cursor.fetchall()]

            # Проверка завершенных чатов
            finished_chats_query = """
                SELECT partner_id FROM finished_chats WHERE user_id = %s
            """
            await cursor.execute(finished_chats_query, (user_id,))
            finished_chats = [row['partner_id'] for row in await cursor.fetchall()]

            # Основной цикл для поиска совпадений
            for interests_count in range(len(interests_list), -1, -1):
                if interests_count > 0:
                    # Динамическое создание условий для поиска по интересам
                    interests_conditions = " OR ".join([f"wl.interests LIKE %s" for _ in range(interests_count)])
                    interests_values = [f"%{interest.strip()}%" for interest in interests_list[:interests_count]]
                else:
                    interests_conditions = "1 = 1"
                    interests_values = []

                blocked_users_filter = ""
                if blocked_users:
                    blocked_users_filter = f"AND wl.user_id NOT IN ({','.join(['%s'] * len(blocked_users))})"

                finished_chats_filter = ""
                if finished_chats:
                    finished_chats_filter = f"AND wl.user_id NOT IN ({','.join(['%s'] * len(finished_chats))})"

                # Запрос на поиск пользователя с учетом блокировок и завершенных чатов
                query = f"""
                    SELECT wl.user_id, wl.username, wl.location, wl.gender, wl.orientation, wl.interests
                    FROM waiting_list wl
                    WHERE wl.user_id != %s
                    {blocked_users_filter}  -- исключаем заблокированных
                    {finished_chats_filter}  -- исключаем пользователей с завершенными чатами
                    {"AND wl.gender = %s" if search_gender else ""}
                    AND ({interests_conditions})
                """

                # Составляем параметры для запроса
                params = [user_id] + blocked_users + finished_chats + interests_values
                if search_gender:
                    params.append(search_gender)

                await cursor.execute(query, params)
                matches = await cursor.fetchall()

                # Проверяем каждого найденного пользователя по расстоянию
                for match in matches:
                    match_lat, match_lon = map(float, match['location'].split(','))
                    distance = calculate_distance(user_lat, user_lon, match_lat, match_lon)

                    if distance <= max_distance:
                        return match

            return None

# Удаление пользователя из списка ожидания
async def remove_from_waiting_list(user_id):
    async with db.acquire() as conn:
        async with conn.cursor() as cursor:
            query = "DELETE FROM waiting_list WHERE user_id = %s"
            await cursor.execute(query, (user_id,))
            await conn.commit()

# Функция для сохранения сообщений чата в базу данных
async def save_chat_message_to_db(sender_id, receiver_id, message_id, content, msg_type='text'):
    async with db.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "INSERT INTO chat_messages (sender_id, receiver_id, message_id, content, type) VALUES (%s, %s, %s, %s, %s)",
                (sender_id, receiver_id, message_id, content, msg_type)
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

# Получение завершённых чатов пользователя
async def get_finished_chats(user_id):
    async with db.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            query = """
                SELECT fc.user_id, fc.partner_id, u.username
                FROM finished_chats fc
                JOIN users u ON fc.partner_id = u.user_id
                WHERE fc.user_id = %s
            """
            await cursor.execute(query, (user_id,))
            return await cursor.fetchall()


# Получение истории чатов между двумя пользователями
async def get_chat_history(user_id, partner_id):
    async with db.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("""
                SELECT * FROM chat_messages 
                WHERE (sender_id = %s AND receiver_id = %s) 
                OR (sender_id = %s AND receiver_id = %s)
                ORDER BY message_id ASC
            """, (user_id, partner_id, partner_id, user_id))
            return await cursor.fetchall()
        
async def add_active_chat(user_id: int, partner_id: int):
    existing_chat = await get_active_chat(user_id)
    async with db.acquire() as conn:
        async with conn.cursor() as cursor:
            if not existing_chat:
                # Если нет активного чата, добавляем его
                await cursor.execute(
                    "INSERT INTO active_chats (user_id, partner_id) VALUES (%s, %s)",
                    (user_id, partner_id)
                )
            await conn.commit()

async def remove_active_chat(user_id: int):
    async with db.acquire() as conn:
        async with conn.cursor() as cursor:
            # Обновляем статус чата вместо удаления
            await cursor.execute(
                "UPDATE active_chats SET status = 'finished' WHERE user_id = %s OR partner_id = %s",
                (user_id, user_id)
            )
            await conn.commit()

async def get_active_chat(user_id: int):
    async with db.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(
                "SELECT * FROM active_chats WHERE user_id = %s OR partner_id = %s",
                (user_id, user_id)
            )
            result = await cursor.fetchone()
            
            # Проверяем, чтобы partner_id был другим пользователем
            if result:
                if result['user_id'] == user_id:
                    return {'partner_id': result['partner_id']}
                else:
                    return {'partner_id': result['user_id']}

async def is_nickname_taken(nickname: str) -> bool:
    async with db.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", (nickname,))
            result = await cursor.fetchone()
            return result[0] > 0
        
async def update_search_radius(user_id: int, distance: float):
    async with db.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "UPDATE users SET distance = %s WHERE user_id = %s",
                (distance, user_id)
            )
            await conn.commit()

async def get_blocked_users(user_id: int):
    async with db.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                """
                SELECT blocked_users.blocked_id, users.username 
                FROM blocked_users 
                JOIN users ON blocked_users.blocked_id = users.user_id 
                WHERE blocked_users.blocker_id = %s
                """, 
                (user_id,)
            )
            result = await cursor.fetchall()
            return result  # Вернем результат как список кортежей
 # Используем индекс 0 для доступа к первому элементу кортежа

async def unblock_user(blocker_id: int, blocked_id: int):
    async with db.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "DELETE FROM blocked_users WHERE blocker_id = %s AND blocked_id = %s", 
                (blocker_id, blocked_id)
            )
            await conn.commit()

