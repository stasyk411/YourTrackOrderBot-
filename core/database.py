# core/database.py
import sqlite3
import os
from datetime import datetime

# Путь к файлу БД ОТНОСИТЕЛЬНО этого файла
# Если database.py лежит в /core, а БД мы хотим в /data, то путь: ../data/tracking.db
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'tracking.db')

def get_db_connection():
    """Создаёт и возвращает соединение с базой данных."""
    # Убедимся, что папка data существует
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Чтобы результаты были как словари
    return conn

def init_db():
    """Создаёт таблицы, если они не существуют. Вызывается один раз при старте бота."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Таблица для запросов на отслеживание
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS track_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            order_number TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, order_number)  -- Не сохранять дубликаты
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"[DATABASE] База данных инициализирована: {DB_PATH}")

def save_track_request(user_id: int, order_number: str) -> bool:
    """Сохраняет запрос на отслеживание. Возвращает True если успешно."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO track_requests (user_id, order_number) VALUES (?, ?)",
            (user_id, order_number)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[DATABASE ERROR] Не удалось сохранить запрос: {e}")
        return False

def get_user_tracks(user_id: int, limit: int = 20):
    """Возвращает последние треки пользователя."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT order_number, created_at 
            FROM track_requests 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (user_id, limit))
        
        tracks = cursor.fetchall()
        conn.close()
        
        # Преобразуем в список словарей для удобства
        result = []
        for row in tracks:
            result.append({
                "order_number": row["order_number"],
                "created_at": row["created_at"]
            })
        return result
    except Exception as e:
        print(f"[DATABASE ERROR] Не удалось загрузить треки: {e}")
        return []