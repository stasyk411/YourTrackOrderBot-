"""
core/services/tracking_service.py
Сервис для бизнес-логики трекинга заказов

Отделяет бизнес-логику от интерфейса (хендлеров)
Можно тестировать отдельно от Telegram API
"""

import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class TrackingService:
    """
    Сервис для трекинга заказов
    
    Содержит всю бизнес-логику по работе с заказами:
    - Валидация номеров заказов
    - Запросы к внешним API (СДЭК)
    - Работа с базой данных
    - Форматирование ответов
    """
    
    def __init__(self, db_connection_func, cdek_api_key: Optional[str] = None):
        """
        Инициализация сервиса
        
        Args:
            db_connection_func: Функция для получения соединения с БД
            cdek_api_key: Ключ API СДЭК (опционально, для тестов можно None)
        """
        self.get_db_connection = db_connection_func
        self.cdek_api_key = cdek_api_key
        logger.info("TrackingService инициализирован")
    
    def validate_order_number(self, order_number: str) -> Dict[str, bool]:
        """
        Валидация номера заказа
        
        Args:
            order_number: Номер заказа для проверки
            
        Returns:
            Dict с результатом валидации и сообщением
        """
        if not order_number:
            return {
                "valid": False,
                "message": "Номер заказа не может быть пустым"
            }
        
        # Убираем пробелы и лишние символы
        cleaned_number = order_number.strip()
        
        # Проверяем длину
        if len(cleaned_number) < 6:
            return {
                "valid": False,
                "message": "Номер заказа слишком короткий (минимум 6 символов)"
            }
        
        # Проверяем что это цифры (или цифры + буквы для СДЭК)
        if not cleaned_number.replace(" ", "").isalnum():
            return {
                "valid": False,
                "message": "Номер заказа должен содержать только буквы и цифры"
            }
        
        logger.debug(f"Номер заказа валиден: {cleaned_number}")
        return {
            "valid": True,
            "message": "Номер заказа валиден",
            "cleaned_number": cleaned_number
        }
    
    async def track_order(self, order_number: str, user_id: int) -> Dict:
        """
        Основной метод трекинга заказа
        
        Args:
            order_number: Номер заказа для отслеживания
            user_id: ID пользователя Telegram
            
        Returns:
            Dict с результатом трекинга
        """
        logger.info(f"Запрос трекинга: order={order_number}, user={user_id}")
        
        try:
            # 1. Валидация номера
            validation = self.validate_order_number(order_number)
            if not validation["valid"]:
                logger.warning(f"Невалидный номер заказа: {order_number}")
                return {
                    "success": False,
                    "error": validation["message"],
                    "order_number": order_number
                }
            
            cleaned_number = validation["cleaned_number"]
            
            # 2. Сохранение в БД
            saved = self._save_to_database(user_id, cleaned_number)
            if not saved:
                logger.error(f"Не удалось сохранить в БД: {cleaned_number}")
                # Не прерываем процесс, только логируем
            
            # 3. Запрос статуса (в реальности - к API СДЭК)
            status = await self._get_order_status(cleaned_number)
            
            # 4. Форматирование ответа
            response = self._format_response(cleaned_number, status)
            
            logger.info(f"Трекинг завершен: {cleaned_number} -> {status}")
            return response
            
        except Exception as e:
            logger.error(f"Ошибка трекинга заказа {order_number}: {e}", exc_info=True)
            return {
                "success": False,
                "error": "Внутренняя ошибка сервиса",
                "order_number": order_number,
                "details": str(e)
            }
    
    def _save_to_database(self, user_id: int, order_number: str) -> bool:
        """
        Сохранение запроса в базу данных
        
        Args:
            user_id: ID пользователя
            order_number: Номер заказа
            
        Returns:
            bool: Успешно ли сохранено
        """
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Используем INSERT OR IGNORE чтобы избежать дубликатов
            cursor.execute(
                "INSERT OR IGNORE INTO track_requests (user_id, order_number) VALUES (?, ?)",
                (user_id, order_number)
            )
            
            conn.commit()
            conn.close()
            logger.debug(f"Сохранено в БД: user={user_id}, order={order_number}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка сохранения в БД: {e}")
            return False
    
    async def _get_order_status(self, order_number: str) -> str:
        """
        Получение статуса заказа (заглушка для тестов)
        
        В реальности здесь будет запрос к API СДЭК
        """
        # Заглушка для тестирования
        # В реальном приложении здесь будет aiohttp запрос к API СДЭК
        
        # Имитация разных статусов для тестирования
        statuses = [
            "В обработке",
            "Собран на складе",
            "Передан в доставку",
            "В пути",
            "Прибыл в город назначения",
            "Доставлен"
        ]
        
        # Детерминированный выбор статуса на основе номера заказа
        # Для тестирования - всегда возвращаем фиксированный статус
        import hashlib
        hash_obj = hashlib.md5(order_number.encode())
        hash_int = int(hash_obj.hexdigest(), 16)
        status_index = hash_int % len(statuses)
        
        # Добавляем задержку для имитации сетевого запроса
        import asyncio
        await asyncio.sleep(0.1)
        
        status = statuses[status_index]
        logger.debug(f"Получен статус для {order_number}: {status}")
        return status
    
    def _format_response(self, order_number: str, status: str) -> Dict:
        """
        Форматирование ответа для пользователя
        
        Args:
            order_number: Номер заказа
            status: Статус заказа
            
        Returns:
            Dict с форматированным ответом
        """
        # Эмодзи для разных статусов
        status_emojis = {
            "В обработке": "🔄",
            "Собран на складе": "📦",
            "Передан в доставку": "🚚",
            "В пути": "✈️",
            "Прибыл в город назначения": "🏙️",
            "Доставлен": "✅"
        }
        
        emoji = status_emojis.get(status, "📋")
        
        return {
            "success": True,
            "order_number": order_number,
            "status": status,
            "emoji": emoji,
            "message": f"{emoji} Заказ {order_number}\nСтатус: {status}",
            "timestamp": datetime.now().isoformat(),
            "formatted_time": datetime.now().strftime("%d.%m.%Y %H:%M")
        }
    
    def get_user_track_history(self, user_id: int, limit: int = 10) -> list:
        """
        Получение истории трекингов пользователя
        
        Args:
            user_id: ID пользователя
            limit: Лимит записей
            
        Returns:
            list: История трекингов
        """
        try:
            conn = self.get_db_connection()
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
            
            result = []
            for row in tracks:
                result.append({
                    "order_number": row["order_number"],
                    "created_at": row["created_at"]
                })
            
            logger.debug(f"Загружена история для user={user_id}: {len(result)} записей")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка загрузки истории: {e}")
            return []