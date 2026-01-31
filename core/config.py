from pathlib import Path
from dataclasses import dataclass
from datetime import time
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# Загружаем .env из корня проекта
env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)

@dataclass
class BotConfig:
    token: str
    morning_start: time = time(6, 0)
    morning_end: time = time(10, 0)
    day_start: time = time(10, 0)
    day_end: time = time(18, 0)
    evening_start: time = time(18, 0)
    evening_end: time = time(22, 0)
    night_start: time = time(22, 0)
    night_end: time = time(6, 0)

def get_bot_config() -> BotConfig:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError(f"Не задан TELEGRAM_BOT_TOKEN в .env по пути {env_path}")

    return BotConfig(token=token)

# Глобальные константы для быстрого доступа
MORNING_START = time(6, 0)   # 🌅 Утро
MORNING_END = time(10, 0)
DAY_START = time(10, 0)      # ☀️ День
DAY_END = time(18, 0)
EVENING_START = time(18, 0)  # 🌆 Вечер
EVENING_END = time(22, 0)
NIGHT_START = time(22, 0)    # 🌙 Ночь
NIGHT_END = time(6, 0)
