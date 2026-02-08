"""
core/services/template_service.py
Сервис для работы с шаблонами ответов (адаптирован под строковый формат)

Данные в формате: "📏 *Размер S (42-44):*\\n'Текст шаблона...'"
"""

import logging
import re
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class TemplateService:
    """
    Сервис для работы с шаблонами ответов в строковом формате
    """
    
    def __init__(self, templates_database: Dict[str, List[str]]):
        """
        Инициализация сервиса
        
        Args:
            templates_database: Словарь {категория: [список строк-шаблонов]}
        """
        self.templates_db = templates_database
        self.parsed_templates = self._parse_all_templates()
        logger.info(f"TemplateService инициализирован. Шаблонов: {len(self.parsed_templates)}")
    
    def _parse_template_string(self, template_str: str, category: str, index: int) -> Dict:
        """
        Парсит строку шаблона в структурированный словарь
        
        Args:
            template_str: Строка шаблона
            category: Категория шаблона
            index: Индекс в списке
            
        Returns:
            Dict: Структурированный шаблон
        """
        # Пытаемся извлечь заголовок (между * и *)
        title_match = re.search(r'\*(.*?)\*', template_str)
        
        if title_match:
            title = title_match.group(1).strip()
            # Текст после заголовка
            text_start = title_match.end()
            text = template_str[text_start:].strip()
        else:
            # Если нет звёздочек, используем первые 30 символов как заголовок
            title = template_str[:30].strip() + "..."
            text = template_str
        
        # Извлекаем эмодзи (если есть)
        emoji_match = re.match(r'^([^\w\s]+\s*)', template_str)
        emoji = emoji_match.group(1).strip() if emoji_match else "📋"
        
        # Генерируем теги на основе категории и заголовка
        tags = self._generate_tags(category, title)
        
        # Создаём ID
        template_id = f"{category}_{index}"
        
        return {
            'id': template_id,
            'category': category,
            'title': title,
            'text': text.strip(),
            'emoji': emoji,
            'tags': tags,
            'raw_string': template_str  # Оригинальная строка
        }
    
    def _generate_tags(self, category: str, title: str) -> List[str]:
        """
        Генерирует теги на основе категории и заголовка
        
        Args:
            category: Категория шаблона
            title: Заголовок шаблона
            
        Returns:
            List[str]: Список тегов
        """
        tags = []
        
        # Теги из категории
        category_tags = {
            'cat_size': ['размер', 's', 'm', 'l', 'xl'],
            'cat_delivery': ['доставка', 'курьер', 'сдэк'],
            'cat_pvz': ['пвз', 'пункт выдачи', 'адрес'],
            'cat_return': ['возврат', 'брак', 'обмен'],
            'cat_price': ['цена', 'акция', 'скидка'],
            'cat_emotion': ['эмоции', 'благодарность', 'отзыв']
        }
        
        tags.extend(category_tags.get(category, []))
        
        # Теги из заголовка (ключевые слова)
        title_lower = title.lower()
        keywords = ['размер', 'доставка', 'пвз', 'возврат', 'цена', 'акция', 'скидка', 
                   'брак', 'качество', 'спасибо', 'отзыв', 'курьер']
        
        for keyword in keywords:
            if keyword in title_lower:
                tags.append(keyword)
        
        # Убираем дубликаты
        return list(set(tags))
    
    def _parse_all_templates(self) -> List[Dict]:
        """
        Парсит все шаблоны из базы данных
        
        Returns:
            List[Dict]: Список структурированных шаблонов
        """
        parsed = []
        
        for category, templates in self.templates_db.items():
            for index, template_str in enumerate(templates):
                try:
                    parsed_template = self._parse_template_string(
                        template_str, category, index
                    )
                    parsed.append(parsed_template)
                except Exception as e:
                    logger.error(f"Ошибка парсинга шаблона {category}[{index}]: {e}")
        
        return parsed
    
    def get_all_categories(self) -> List[str]:
        """
        Возвращает список всех категорий
        
        Returns:
            List[str]: Список категорий
        """
        categories = list(self.templates_db.keys())
        return categories
    
    def get_templates_by_category(self, category: str) -> List[Dict]:
        """
        Возвращает шаблоны по категории
        
        Args:
            category: Название категории
            
        Returns:
            List[Dict]: Список шаблонов категории
        """
        return [t for t in self.parsed_templates if t['category'] == category]
    
    def search_templates(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Поиск шаблонов по тексту
        
        Args:
            query: Строка для поиска
            limit: Максимальное количество результатов
            
        Returns:
            List[Dict]: Найденные шаблоны
        """
        if not query or not query.strip():
            return []
        
        query_lower = query.lower().strip()
        results = []
        
        for template in self.parsed_templates:
            # Поиск в заголовке
            title = template.get('title', '').lower()
            # Поиск в тексте
            text = template.get('text', '').lower()
            # Поиск в тегах
            tags = ' '.join(tag.lower() for tag in template.get('tags', []))
            
            # Проверяем совпадение
            if (query_lower in title or 
                query_lower in text or 
                query_lower in tags):
                
                results.append(template)
        
        # Ограничиваем количество
        return results[:limit]
    
    def get_template_by_id(self, template_id: str) -> Optional[Dict]:
        """
        Находит шаблон по ID
        
        Args:
            template_id: ID шаблона в формате "категория_индекс"
            
        Returns:
            Optional[Dict]: Шаблон или None если не найден
        """
        for template in self.parsed_templates:
            if template.get('id') == template_id:
                return template
        
        return None
    
    def get_popular_templates(self, limit: int = 5) -> List[Dict]:
        """
        Возвращает популярные шаблоны (первые из каждой категории)
        
        Args:
            limit: Максимальное количество
            
        Returns:
            List[Dict]: Популярные шаблоны
        """
        # Берем по одному шаблону из каждой категории
        popular = []
        categories_used = set()
        
        for template in self.parsed_templates:
            category = template['category']
            if category not in categories_used:
                categories_used.add(category)
                popular.append(template)
                
                if len(popular) >= limit:
                    break
        
        return popular
    
    def format_template_for_display(self, template: Dict) -> Dict:
        """
        Форматирует шаблон для отображения пользователю
        
        Args:
            template: Исходный шаблон
            
        Returns:
            Dict: Форматированный шаблон
        """
        formatted = template.copy()
        
        # Эмодзи для категорий (русские названия)
        category_names = {
            'cat_size': 'Размер',
            'cat_delivery': 'Доставка',
            'cat_pvz': 'ПВЗ',
            'cat_return': 'Возврат',
            'cat_price': 'Цена',
            'cat_emotion': 'Эмоции'
        }
        
        category = template.get('category', '')
        category_display = category_names.get(category, category)
        
        # Форматируем заголовок
        title = template.get('title', 'Без названия')
        emoji = template.get('emoji', '📋')
        formatted['display_title'] = f"{emoji} {title}"
        formatted['category_display'] = category_display
        
        # Обрезаем текст для предпросмотра
        text = template.get('text', '')
        if len(text) > 100:
            formatted['preview_text'] = text[:100] + '...'
        else:
            formatted['preview_text'] = text
        
        # Форматируем теги
        tags = template.get('tags', [])
        if tags:
            formatted['display_tags'] = ' '.join(f'#{tag}' for tag in tags[:3])
        else:
            formatted['display_tags'] = ''
        
        return formatted
    
    def get_template_categories_with_counts(self) -> Dict[str, int]:
        """
        Возвращает категории с количеством шаблонов
        
        Returns:
            Dict[str, int]: Категория → количество шаблонов
        """
        return {cat: len(templates) for cat, templates in self.templates_db.items()}
    
    def get_random_template(self) -> Optional[Dict]:
        """
        Возвращает случайный шаблон
        
        Returns:
            Optional[Dict]: Случайный шаблон
        """
        import random
        
        if not self.parsed_templates:
            return None
        
        return random.choice(self.parsed_templates)
    
    def get_template_count(self) -> int:
        """
        Возвращает общее количество шаблонов
        
        Returns:
            int: Количество шаблонов
        """
        total = 0
        for templates in self.templates_db.values():
            total += len(templates)
        return total