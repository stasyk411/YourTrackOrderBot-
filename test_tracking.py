import requests

def get_cdek_status(track_number: str):
    """Тестовая версия функции трекинга СДЭК"""
    try:
        url = f"https://api.cdek.ru/v2/orders?imNumber={track_number}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        }
        
        print(f"🔍 Тестируем трек: {track_number}")
        print(f"📡 Запрос к: {url}")
        
        response = requests.get(url, headers=headers, timeout=5)
        print(f"📊 Ответ API: код {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API ответил успешно")
            # Показываем первые 200 символов ответа для проверки
            print(f"📄 Ответ (первые 200 символов):")
            print(response.text[:200])
            return "✅ Тест пройден - API работает"
        else:
            print(f"⚠️ API вернул код: {response.status_code}")
            print(f"📄 Текст ответа: {response.text[:100]}")
            return f"⚠️ API вернул код: {response.status_code}"
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return f"❌ Ошибка: {e}"

# Тестируем на тестовом трек-номере
print("=" * 50)
print("🧪 ТЕСТИРОВАНИЕ API СДЭК")
print("=" * 50)

# Тест 1: Тестовый номер
test_track = "TEST123456789"
print(f"\n📦 Тест 1: Тестовый трек '{test_track}'")
result1 = get_cdek_status(test_track)
print(f"🎯 Результат 1: {result1}")

# Тест 2: Пустой запрос (проверка ошибок)
print(f"\n📦 Тест 2: Пустой трек-номер")
result2 = get_cdek_status("")
print(f"🎯 Результат 2: {result2}")

print("\n" + "=" * 50)
print("✅ Тестирование завершено")
print("=" * 50)