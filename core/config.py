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
    night_start: time
    night_end: time


def get_bot_config() -> BotConfig:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError(f"Не задан TELEGRAM_BOT_TOKEN в .env по пути {env_path}")

    return BotConfig(
        token=token,
        night_start=time(22, 0),
        night_end=time(9, 0),
    )
NIGHT_START = time(22, 0)  # 22:00
NIGHT_END = time(9, 0)     # 09:00
