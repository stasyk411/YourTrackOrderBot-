# КОМАНДА: Закрываем файл и готовим новую версию
# Сначала закройте VS Code с routes.py

# Теперь создаём новую версию routes.py с добавленным /help
# Копируйте ВЕСЬ этот код и замените текущий файл:

"""
app/routes.py - Регистрация всех хендлеров бота
Здесь подключаются все обработчики из папки handlers/
"""

def register_handlers(bot, config):
    """
    Регистрирует все хендлеры для бота
    
    Args:
        bot: экземпляр TeleBot
        config: конфигурация приложения
    """
    print("📋 Регистрация маршрутов...")
    
    # Импортируем хендлеры здесь, чтобы избежать циклических импортов
    # Каждый хендлер добавляется по мере рефакторинга
    
    # 1. Хендлер /night (перенесён)
    try:
        from handlers.night import register as register_night
        register_night(bot, config)
        print("✅ /night зарегистрирован")
    except ImportError as e:
        print(f"⚠️ Ошибка импорта handlers.night: {e}")
    except Exception as e:
        print(f"⚠️ Ошибка регистрации /night: {e}")
    
    # 2. Хендлер /start (перенесён)
    try:
        from handlers.start import register as register_start
        register_start(bot, config)
        print("✅ /start зарегистрирован")
    except ImportError as e:
        print(f"⚠️ Ошибка импорта handlers.start: {e}")
    except Exception as e:
        print(f"⚠️ Ошибка регистрации /start: {e}")
    
    # 3. Хендлер /pay (перенесён)
    try:
        from handlers.pay import register as register_pay
        register_pay(bot, config)
        print("✅ /pay зарегистрирован")
    except ImportError as e:
        print(f"⚠️ Ошибка импорта handlers.pay: {e}")
    except Exception as e:
        print(f"⚠️ Ошибка регистрации /pay: {e}")
    
    # 4. Хендлер /get_pdf (перенесён)
    try:
        from handlers.get_pdf import register as register_get_pdf
        register_get_pdf(bot, config)
        print("✅ /get_pdf зарегистрирован")
    except ImportError as e:
        print(f"⚠️ Ошибка импорта handlers.get_pdf: {e}")
    except Exception as e:
        print(f"⚠️ Ошибка регистрации /get_pdf: {e}")
    
    # 5. Хендлер /help (новый)
    try:
        from handlers.help import register as register_help
        register_help(bot, config)
        print("✅ /help зарегистрирован")
    except ImportError as e:
        print(f"⚠️ Ошибка импорта handlers.help: {e}")
    except Exception as e:
        print(f"⚠️ Ошибка регистрации /help: {e}")
    
    # TODO: Добавить остальные хендлеры по мере переноса:
    # from handlers.track import register as register_track  
    # register_track(bot, config)
    
    # from handlers.templates import register as register_templates
    # register_templates(bot, config)
    
    # from handlers.mytracks import register as register_mytracks
    # register_mytracks(bot, config)
    
    print("✅ Все маршруты зарегистрированы")