"""
tests/test_services.py
Тесты для сервисного слоя приложения

Тестируем:
1. TrackingService - логику трекинга заказов
2. TemplateService - логику работы с шаблонами
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch

# Добавляем путь к проекту для импорта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestTrackingService(unittest.TestCase):
    """Тесты для TrackingService"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        from core.services import TrackingService
        
        # Мок функции для соединения с БД
        self.mock_db_func = Mock()
        self.tracking_service = TrackingService(self.mock_db_func)
    
    def test_validate_order_number_valid(self):
        """Тест валидации корректного номера заказа"""
        # Тестируем валидные номера
        test_cases = [
            "123456",
            "ABC123",
            "123 456",
            "  123456  ",  # с пробелами
        ]
        
        for order_number in test_cases:
            with self.subTest(order_number=order_number):
                result = self.tracking_service.validate_order_number(order_number)
                self.assertTrue(result["valid"], 
                              f"Номер {order_number} должен быть валидным")
                self.assertIn("cleaned_number", result)
    
    def test_validate_order_number_invalid(self):
        """Тест валидации некорректных номеров заказа"""
        test_cases = [
            ("", "пустой номер"),
            ("123", "слишком короткий"),
            ("!@#$%", "спецсимволы"),
        ]
        
        for order_number, description in test_cases:
            with self.subTest(description=description):
                result = self.tracking_service.validate_order_number(order_number)
                self.assertFalse(result["valid"],
                               f"Номер {order_number} должен быть невалидным")
                self.assertIn("message", result)
    
    def test_save_to_database_success(self):
        """Тест успешного сохранения в БД"""
        # Настраиваем мок для успешного сохранения
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        self.mock_db_func.return_value = mock_conn
        
        # Вызываем метод
        result = self.tracking_service._save_to_database(123, "TEST123")
        
        # Проверяем
        self.assertTrue(result)
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()
    
    def test_save_to_database_failure(self):
        """Тест ошибки сохранения в БД"""
        # Настраиваем мок для ошибки
        self.mock_db_func.side_effect = Exception("DB error")
        
        # Вызываем метод
        result = self.tracking_service._save_to_database(123, "TEST123")
        
        # Проверяем
        self.assertFalse(result)
    
    def test_format_response(self):
        """Тест форматирования ответа"""
        # Вызываем метод
        response = self.tracking_service._format_response("TEST123", "В пути")
        
        # Проверяем структуру ответа
        expected_keys = ["success", "order_number", "status", "emoji", 
                        "message", "timestamp", "formatted_time"]
        
        for key in expected_keys:
            self.assertIn(key, response, f"Ответ должен содержать ключ {key}")
        
        self.assertEqual(response["order_number"], "TEST123")
        self.assertEqual(response["status"], "В пути")
        self.assertIn("TEST123", response["message"])


class TestTemplateService(unittest.TestCase):
    """Тесты для TemplateService"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        from core.services import TemplateService
        
        # Тестовая база шаблонов
        self.test_templates_db = {
            'cat_test': [
                "📏 *Тестовый шаблон 1:*\n'Это первый тестовый шаблон'",
                "🚚 *Доставка тест:*\n'Тестовая доставка шаблон'"
            ],
            'cat_other': [
                "💰 *Цена тест:*\n'Тестовый шаблон о цене'"
            ]
        }
        
        self.template_service = TemplateService(self.test_templates_db)
    
    def test_init_parses_templates(self):
        """Тест что шаблоны парсятся при инициализации"""
        self.assertEqual(len(self.template_service.parsed_templates), 3)
        
        # Проверяем структуру первого шаблона
        first_template = self.template_service.parsed_templates[0]
        expected_keys = ['id', 'category', 'title', 'text', 'emoji', 
                        'tags', 'raw_string']
        
        for key in expected_keys:
            self.assertIn(key, first_template, 
                         f"Шаблон должен содержать ключ {key}")
    
    def test_get_all_categories(self):
        """Тест получения всех категорий"""
        categories = self.template_service.get_all_categories()
        
        self.assertEqual(len(categories), 2)
        self.assertIn('cat_test', categories)
        self.assertIn('cat_other', categories)
    
    def test_get_templates_by_category(self):
        """Тест получения шаблонов по категории"""
        templates = self.template_service.get_templates_by_category('cat_test')
        
        self.assertEqual(len(templates), 2)
        self.assertEqual(templates[0]['category'], 'cat_test')
        self.assertEqual(templates[1]['category'], 'cat_test')
    
    def test_search_templates(self):
        """Тест поиска шаблонов"""
        # Поиск по слову в заголовке
        results = self.template_service.search_templates('доставка')
        self.assertEqual(len(results), 1)
        self.assertIn('доставка', results[0]['title'].lower())
        
        # Поиск по слову в тексте - исправлено: 2 вместо 3
        results = self.template_service.search_templates('тестовый')
        self.assertEqual(len(results), 2)  # Исправлено: 2 шаблона содержат "тестовый"
        
        # Поиск с лимитом
        results = self.template_service.search_templates('тестовый', limit=1)
        self.assertEqual(len(results), 1)
    
    def test_search_templates_empty_query(self):
        """Тест поиска с пустым запросом"""
        results = self.template_service.search_templates('')
        self.assertEqual(len(results), 0)
        
        results = self.template_service.search_templates('   ')
        self.assertEqual(len(results), 0)
    
    def test_get_template_by_id(self):
        """Тест получения шаблона по ID"""
        # Получаем ID первого шаблона
        first_id = self.template_service.parsed_templates[0]['id']
        
        # Ищем по ID
        template = self.template_service.get_template_by_id(first_id)
        
        self.assertIsNotNone(template)
        self.assertEqual(template['id'], first_id)
    
    def test_get_template_by_id_not_found(self):
        """Тест поиска несуществующего шаблона"""
        template = self.template_service.get_template_by_id('non_existent')
        self.assertIsNone(template)
    
    def test_get_popular_templates(self):
        """Тест получения популярных шаблонов"""
        popular = self.template_service.get_popular_templates(2)
        
        self.assertEqual(len(popular), 2)
        # Должны быть из разных категорий
        categories = {t['category'] for t in popular}
        self.assertEqual(len(categories), 2)
    
    def test_format_template_for_display(self):
        """Тест форматирования шаблона для отображения"""
        # Берем первый шаблон
        original = self.template_service.parsed_templates[0]
        formatted = self.template_service.format_template_for_display(original)
        
        # Проверяем добавленные поля
        self.assertIn('display_title', formatted)
        self.assertIn('preview_text', formatted)
        self.assertIn('display_tags', formatted)
        self.assertIn('category_display', formatted)
        
        # Проверяем что оригинальные поля сохранились
        self.assertEqual(formatted['id'], original['id'])
        self.assertEqual(formatted['category'], original['category'])
    
    def test_get_template_categories_with_counts(self):
        """Тест получения категорий с количеством шаблонов"""
        categories_counts = self.template_service.get_template_categories_with_counts()
        
        self.assertEqual(categories_counts['cat_test'], 2)
        self.assertEqual(categories_counts['cat_other'], 1)
    
    def test_get_template_count(self):
        """Тест получения общего количества шаблонов"""
        count = self.template_service.get_template_count()
        self.assertEqual(count, 3)
    
    def test_get_random_template(self):
        """Тест получения случайного шаблона"""
        random_template = self.template_service.get_random_template()
        self.assertIsNotNone(random_template)
        self.assertIn('id', random_template)
        self.assertIn('title', random_template)


class TestServicesIntegration(unittest.TestCase):
    """Интеграционные тесты сервисов с реальными данными"""
    
    def test_template_service_with_real_data(self):
        """Тест TemplateService с реальной базой шаблонов"""
        from core.services import TemplateService
        from data.templates_database import TEMPLATES_DATABASE
        
        service = TemplateService(TEMPLATES_DATABASE)
        
        # Проверяем что данные загрузились
        self.assertGreater(service.get_template_count(), 0)
        
        # Проверяем категории
        categories = service.get_all_categories()
        self.assertGreater(len(categories), 0)
        
        # Проверяем поиск
        results = service.search_templates('доставка', limit=1)
        self.assertEqual(len(results), 1)
    
    def test_tracking_service_initialization(self):
        """Тест инициализации TrackingService"""
        from core.services import TrackingService
        
        # Просто проверяем что сервис создается без ошибок
        mock_db = Mock()
        service = TrackingService(mock_db)
        
        self.assertIsNotNone(service)
        self.assertEqual(service.get_db_connection, mock_db)


if __name__ == '__main__':
    # Запускаем тесты
    unittest.main(verbosity=2)