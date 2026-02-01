"""
PDF генератор для TrackOrderPro Bot с использованием pdfkit
"""

import os
import logging
import tempfile
from pathlib import Path

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Пробуем импортировать pdfkit
try:
    import pdfkit
    PDFKIT_AVAILABLE = True
except ImportError:
    PDFKIT_AVAILABLE = False
    logger.warning("pdfkit не установлен. Установите: pip install pdfkit")

class PDFGenerator:
    """Генератор PDF с использованием pdfkit (wkhtmltopdf)"""
    
    def __init__(self, templates_dir="data", static_dir="static"):
        self.templates_dir = Path(templates_dir)
        self.static_dir = Path(static_dir)
        
        # Настройка пути к wkhtmltopdf
        self.wkhtmltopdf_path = None
        if PDFKIT_AVAILABLE:
            self.wkhtmltopdf_path = self._find_wkhtmltopdf()
        
        if not self.wkhtmltopdf_path and PDFKIT_AVAILABLE:
            logger.warning("wkhtmltopdf не найден. PDF может не генерироваться.")
    
    def _find_wkhtmltopdf(self):
        """Ищет wkhtmltopdf в системе"""
        if not PDFKIT_AVAILABLE:
            return None
            
        # Возможные пути установки на Windows
        possible_paths = [
            r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe",
            r"C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe",
            os.path.expanduser(r"~\AppData\Local\Programs\wkhtmltopdf\bin\wkhtmltopdf.exe"),
            r"C:\wkhtmltopdf\bin\wkhtmltopdf.exe",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"Найден wkhtmltopdf: {path}")
                return path
        
        logger.warning("wkhtmltopdf не найден. Проверьте установку.")
        return None
    
    def load_html_template(self, template_name="templates_guide.html"):
        """Загружает HTML шаблон"""
        template_path = self.templates_dir / template_name
        
        if not template_path.exists():
            logger.error(f"HTML шаблон не найден: {template_path}")
            return None
        
        try:
            with open(template_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
            
            # Исправляем путь к CSS для локальной файловой системы
            css_path = (self.static_dir / "styles.css").absolute()
            # Заменяем все варианты ссылок на CSS
            html_content = html_content.replace(
                'href="../static/styles.css"',
                f'href="file:///{css_path}"'
            )
            
            logger.info(f"HTML шаблон загружен: {template_path}")
            return html_content
            
        except Exception as e:
            logger.error(f"Ошибка загрузки HTML: {e}")
            return None
    
    def generate_pdf(self, html_content, output_path=None):
        """Генерирует PDF из HTML"""
        if not html_content:
            logger.error("Не передан HTML контент")
            return None
        
        if not PDFKIT_AVAILABLE:
            logger.error("pdfkit не установлен")
            return self._generate_fallback(html_content, output_path)
        
        if not self.wkhtmltopdf_path:
            logger.error("wkhtmltopdf не установлен")
            return self._generate_fallback(html_content, output_path)
        
        try:
            # Настройки для PDF
            options = {
                'page-size': 'A4',
                'margin-top': '15mm',
                'margin-right': '15mm',
                'margin-bottom': '15mm',
                'margin-left': '15mm',
                'encoding': "UTF-8",
                'no-outline': None,
                'enable-local-file-access': None,  # Разрешаем доступ к локальным файлам
            }
            
            # Конфигурация pdfkit с путем к wkhtmltopdf
            config = pdfkit.configuration(wkhtmltopdf=self.wkhtmltopdf_path)
            
            if output_path:
                # Сохраняем в файл
                pdfkit.from_string(
                    html_content,
                    output_path,
                    options=options,
                    configuration=config
                )
                logger.info(f"PDF создан: {output_path}")
                return output_path
            else:
                # Генерируем в память
                pdf_bytes = pdfkit.from_string(
                    html_content,
                    False,
                    options=options,
                    configuration=config
                )
                logger.info("PDF сгенерирован в память")
                return pdf_bytes
                
        except Exception as e:
            logger.error(f"Ошибка генерации PDF с pdfkit: {e}")
            return self._generate_fallback(html_content, output_path)
    
    def _generate_fallback(self, html_content, output_path=None):
        """Fallback: если pdfkit не работает, сохраняем как HTML"""
        try:
            if output_path:
                # Сохраняем как HTML файл
                html_path = str(output_path).replace('.pdf', '.html')
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                logger.info(f"HTML сохранён (fallback): {html_path}")
                return html_path
            else:
                # Возвращаем HTML как текст
                return html_content.encode('utf-8')
        except Exception as e:
            logger.error(f"Ошибка fallback: {e}")
            return None
    
    def generate_templates_pdf(self, output_dir="data", return_bytes=False):
        """Основной метод для генерации PDF с шаблонами"""
        logger.info("Начинаю генерацию PDF с шаблонами...")
        
        # Загружаем HTML
        html_content = self.load_html_template()
        
        if not html_content:
            # Создаём простой HTML если файл не найден
            html_content = self._create_fallback_html()
        
        if return_bytes:
            # Возвращаем PDF в виде bytes
            pdf_data = self.generate_pdf(html_content)
            return pdf_data
        else:
            # Сохраняем в файл
            output_path = Path(output_dir) / "templates_guide.pdf"
            result = self.generate_pdf(html_content, str(output_path))
            return result
    
    def _create_fallback_html(self):
        """Создаёт простой HTML если основной файл не найден"""
        return '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Шаблоны ответов для продавцов</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; line-height: 1.6; }
        h1 { color: #2c5aa0; border-bottom: 2px solid #2c5aa0; padding-bottom: 10px; }
        h2 { color: #2c5aa0; margin-top: 25px; }
        .template { background: #f8f9fa; border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .template-number { background: #2c5aa0; color: white; padding: 3px 8px; border-radius: 3px; font-size: 14px; }
    </style>
</head>
<body>
    <h1>TrackOrderPro - 32 шаблона ответов</h1>
    <p>Используйте бота @TrackOrderDevBot для доступа ко всем шаблонам:</p>
    <p><strong>Команда:</strong> <code>/templates</code> - 32 готовых ответа в Telegram</p>
    <p><strong>Основные категории:</strong> Размеры, Доставка, Оплата, Качество, Гарантии, Эмоции</p>
</body>
</html>'''
    
    def check_wkhtmltopdf_installation(self):
        """Проверяет установку wkhtmltopdf"""
        if not PDFKIT_AVAILABLE:
            return "❌ pdfkit не установлен. Установите: pip install pdfkit"
        
        if self.wkhtmltopdf_path:
            return f"✅ wkhtmltopdf найден: {self.wkhtmltopdf_path}"
        else:
            return "⚠️ wkhtmltopdf не найден. Установите с https://wkhtmltopdf.org/ или используйте fallback"


# Упрощённый интерфейс
def generate_pdf_guide(output_path=None, return_bytes=False):
    """Быстрая генерация PDF"""
    generator = PDFGenerator()
    
    if output_path:
        return generator.generate_pdf(
            generator.load_html_template(),
            output_path
        )
    else:
        return generator.generate_templates_pdf(return_bytes=return_bytes)


# Тестирование
if __name__ == "__main__":
    print("=" * 50)
    print("Тестирование PDF генератора")
    print("=" * 50)
    
    generator = PDFGenerator()
    
    # Проверяем установку
    print("\n1. Проверка установки:")
    print(generator.check_wkhtmltopdf_installation())
    
    # Проверяем HTML
    print("\n2. Проверка HTML шаблона:")
    html = generator.load_html_template()
    if html:
        print(f"✅ HTML загружен ({len(html)} символов)")
    else:
        print("❌ HTML не загружен")
    
    # Тестируем генерацию
    print("\n3. Генерируем PDF...")
    result = generator.generate_templates_pdf()
    
    if result:
        if result.endswith('.pdf'):
            print(f"✅ PDF создан: {result}")
            # Проверяем размер файла
            if os.path.exists(result):
                size = os.path.getsize(result)
                print(f"📄 Размер файла: {size} байт ({size/1024:.1f} KB)")
        elif result.endswith('.html'):
            print(f"⚠️ Создан HTML (fallback): {result}")
        else:
            print(f"✅ Данные созданы: {type(result)}")
    else:
        print("❌ Ошибка создания")
    
    print("\n" + "=" * 50)
    print("Тестирование завершено!")