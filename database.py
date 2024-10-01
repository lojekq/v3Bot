import os
import mysql.connector
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Подключение к MySQL
db = mysql.connector.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME')
)

# Инициализация базы данных
async def init_db():
    cursor = db.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id BIGINT NOT NULL,
            username VARCHAR(255) NOT NULL,
            gender VARCHAR(50),
            orientation VARCHAR(50),
            interests TEXT,
            location VARCHAR(255),
            lang VARCHAR(10) DEFAULT 'en',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.commit()

# Функция создания пользователя
async def create_user(user_id, username):
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO users (user_id, username) VALUES (%s, %s)", 
        (user_id, username)
    )
    db.commit()

# Получение пользователя по его ID
async def get_user_by_id(user_id):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    return cursor.fetchone()

# Обновление языка пользователя
async def update_user_language(user_id, lang_code):
    cursor = db.cursor()
    cursor.execute("UPDATE users SET lang = %s WHERE user_id = %s", (lang_code, user_id))
    db.commit()

# Обновление пола пользователя
async def update_user_gender(user_id, gender):
    cursor = db.cursor()
    cursor.execute("UPDATE users SET gender = %s WHERE user_id = %s", (gender, user_id))
    db.commit()

# Обновление ориентации пользователя
async def update_user_orientation(user_id, orientation):
    cursor = db.cursor()
    cursor.execute("UPDATE users SET orientation = %s WHERE user_id = %s", (orientation, user_id))
    db.commit()

# Получение интересов пользователя
async def get_user_interests(user_id):
    cursor = db.cursor()
    cursor.execute("SELECT interests FROM users WHERE user_id = %s", (user_id,))
    result = cursor.fetchone()
    if result and result[0]:
        return result[0].split(",")  # Преобразуем строку интересов в список
    return []

# Обновление интересов пользователя (асинхронно)
async def update_user_interests(user_id, interests):
    cursor = db.cursor()
    interests_str = ",".join(interests)  # Преобразуем список интересов в строку
    cursor.execute("UPDATE users SET interests = %s WHERE user_id = %s", (interests_str, user_id))
    db.commit()

# Обновление местоположения пользователя
async def update_user_location(user_id, location):
    cursor = db.cursor()
    cursor.execute("UPDATE users SET location = %s WHERE user_id = %s", (location, user_id))
    db.commit()

# Обновление никнейма пользователя
async def update_user_nickname(user_id, nickname):
    cursor = db.cursor()
    cursor.execute("UPDATE users SET username = %s WHERE user_id = %s", (nickname, user_id))
    db.commit()

# Обновление пола пользователя для опции "Другой" (хранение в базе как "Other")
async def update_user_custom_gender(user_id, custom_gender):
    cursor = db.cursor()
    # Сохраняем пол как "Other" и добавляем поле для кастомного пола
    cursor.execute("UPDATE users SET gender = 'Other', custom_gender = %s WHERE user_id = %s", (custom_gender, user_id))
    db.commit()



