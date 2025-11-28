# config.py
"""
Конфигурация базы данных PostgreSQL
"""

import os
from dataclasses import dataclass

@dataclass
class DatabaseConfig:
    host: str = os.getenv("DB_HOST", "localhost")
    port: int = int(os.getenv("DB_PORT", "5432"))
    name: str = os.getenv("DB_NAME", "weather_db")
    user: str = os.getenv("DB_USER", "weather_user")
    password: str = os.getenv("DB_PASSWORD", "weather_pass")

# Конфигурация по умолчанию
DB_CONFIG = DatabaseConfig()

def get_connection_string() -> str:
    """Возвращает строку подключения к PostgreSQL"""
    return f"postgresql://{DB_CONFIG.user}:{DB_CONFIG.password}@{DB_CONFIG.host}:{DB_CONFIG.port}/{DB_CONFIG.name}"