"""
core.services package - сервисный слой приложения

Содержит бизнес-логику, отделённую от интерфейса (хендлеров)

Модули:
- tracking_service.py - логика трекинга заказов
- template_service.py - логика работы с шаблонами
"""

from core.services.tracking_service import TrackingService
from core.services.template_service import TemplateService

__all__ = ['TrackingService', 'TemplateService']
