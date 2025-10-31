"""
Модуль для простого кэширования ответов API в JSON-файл.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

CACHE_FILE = "weather_cache.json"
CACHE_TTL = timedelta(minutes=30)  # срок жизни кэша

def read_cache(city: str) -> Optional[Dict[str, Any]]:
    """
    Читает кэшированные данные, если они актуальны.
    """
    if not os.path.exists(CACHE_FILE):
        return None

    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        record = data.get(city)
        if not record:
            return None
        timestamp = datetime.fromisoformat(record["timestamp"])
        if datetime.now() - timestamp > CACHE_TTL:
            return None
        return record["weather"]
    except Exception:
        return None


def write_cache(city: str, data: Dict[str, Any]) -> None:
    """
    Сохраняет данные в кэш как JSON.
    """
    cache: Dict[str, Any] = {}
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                cache = json.load(f)
        except Exception:
            cache = {}

    cache[city] = {
        "timestamp": datetime.now().isoformat(),
        "weather": data
    }

    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
