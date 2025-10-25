import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

CACHE_FILE = "weather_cache.json"
CACHE_TTL = timedelta(minutes=30)

def read_cache(city: str) -> Optional[Dict[str, Any]]:
    """
    Читает кэшированные данные для указанного города.

    Args:
        city (str): Название города.

    Returns:
        Optional[Dict[str, Any]]: Данные из кэша, если они актуальны.
    """
    if not os.path.exists(CACHE_FILE):
        return None

    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            cache = json.load(f)
        record = cache.get(city)
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
    Сохраняет данные в кэш.

    Args:
        city (str): Название города.
        data (Dict[str, Any]): Данные для сохранения.
    """
    cache: Dict[str, Any] = {}
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                cache = json.load(f)
        except Exception:
            cache = {}

    cache[city] = {"timestamp": datetime.now().isoformat(), "weather": data}

    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
