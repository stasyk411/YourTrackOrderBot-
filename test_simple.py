
import re

def test_parser():
    patterns = [
        r'\b\d{5,}\b',
        r'\b(?:SD|CD)[A-Z0-9]{8,}\b',
    ]
    
    # Тестовые сообщения из Telegram
    tests = [
        ('Где мой заказ 123456789?', ['123456789']),
        ('Трек SD12345678 не работает', ['SD12345678']),
        ('/track SD12345678', []),  # Команда - не парсим
        ('Просто текст без номера', []),
    ]
    
    print("🧪 ТЕСТ ПАРСЕРА")
    print("=" * 50)
    
    all_passed = True
    for text, expected in tests:
        found = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            found.extend(matches)
        
        found = list(set(found))
        passed = found == expected
        
        print(f"📝 Текст: {text[:30]}...")
        print(f"   🔍 Найдено: {found}")
        print(f"   ✅ Ожидалось: {expected}")
        print(f"   {'🎉 ПРОШЛО' if passed else '❌ НЕ ПРОШЛО'}")
        print()
        
        if not passed:
            all_passed = False
    
    print(f"📊 ИТОГ: {'ВСЕ ТЕСТЫ ПРОЙДЕНЫ' if all_passed else 'ЕСТЬ ОШИБКИ'}")
    return all_passed

if __name__ == "__main__":
    test_parser()
