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
    Читает кэшированные данные для указанного города, если они актуальны.
    
    Args:
        city (str): Ключ для поиска в кэше (название города или координаты)
        
    Returns:
        Optional[Dict[str, Any]]: Данные о погоде из кэша или None, если:
            - файл кэша не существует
            - запись для города не найдена
            - запись устарела (превышен TTL)
            - произошла ошибка чтения
    """
    #существет ли кеш
    if not os.path.exists(CACHE_FILE):
        return None

    try:
        #читаем и парсим кеш .json
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        #ищем нужную запись
        record = data.get(city)
        if not record:
            return None
        
        # Преобразуем строку времени обратно в объект datetime
        timestamp = datetime.fromisoformat(record["timestamp"])
        if datetime.now() - timestamp > CACHE_TTL:
            return None
        
        # Возвращаем актуальные данные о погоде
        return record["weather"]
    
    except Exception:
        return None


def write_cache(city: str, data: Dict[str, Any]) -> None:
    """
    Сохраняет данные в кэш с текущей меткой времени.
    
    Args:
        city (str): Ключ для сохранения (название города или координаты)
        data (Dict[str, Any]): Данные о погоде для кэширования
        
    Note:
        Если файл кэша не существует - создается новый.
        Если файл существует - данные обновляются/добавляются.
        Существующие записи для других городов сохраняются.
    """
    #создаем пустой словарь для кэша
    
    cache: Dict[str, Any] = {}
    
    # Если файл кэша существует, пытаемся загрузить существующие данные
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                cache = json.load(f)
        except Exception:
            cache = {}

    # Обновляем/добавляем запись для текущего города
    cache[city] = {
        "timestamp": datetime.now().isoformat(),
        "weather": data
    }

    # Сохраняем обновленный кэш обратно в файл
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
