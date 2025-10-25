import json
import os
from datetime import datetime, timedelta

CACHE_FILE = "weather_cache.json"
CACHE_TTL = timedelta(minutes=30)  # срок жизни кэша

def read_cache(city: str):
    """Читает кэш, если он актуален."""
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

def write_cache(city: str, weather_data: dict):
    """Сохраняет данные о погоде в кэш."""
    data = {}
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}

    data[city] = {
        "timestamp": datetime.now().isoformat(),
        "weather": weather_data
    }

    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
