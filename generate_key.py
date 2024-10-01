from cryptography.fernet import Fernet

# Генерация ключа шифрования
key = Fernet.generate_key()

# Преобразование ключа в строку и вывод
print(f"Your encryption key: {key.decode()}")
