"""
Модуль для работы с Open-Meteo API с помощью requests.
"""

import requests
from typing import Dict, Any, Optional

def get_coordinates(city: str) -> tuple[float, float]:
    """
    Получает координаты города через Open-Meteo Geocoding API.

    Args:
        city (str): Название города.
    Returns:
        tuple[float, float]: (широта, долгота)
    """
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=ru"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    if not data.get("results"):
        raise ValueError(f"Город '{city}' не найден.")

    lat = data["results"][0]["latitude"]
    lon = data["results"][0]["longitude"]
    return lat, lon


def get_weather(city: Optional[str] = None,
                latitude: Optional[float] = None,
                longitude: Optional[float] = None) -> Dict[str, Any]:
    """
    Возвращает текущую погоду по названию города или координатам.

    Args:
        city (Optional[str]): Название города.
        latitude (Optional[float]): Широта.
        longitude (Optional[float]): Долгота.

    Returns:
        dict: JSON с погодными данными.
    """
    try:
        if latitude is not None and longitude is not None:
            lat, lon = latitude, longitude
            location_name = f"{lat}, {lon}"
        elif city:
            location_name = city
            lat, lon = get_coordinates(city)
        else:
            raise ValueError("Нужно указать либо название города, либо координаты (--lat и --lon)")

        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}&current_weather=true"
        )

        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        data["city"] = location_name
        return data

    except requests.RequestException as e:
        raise ConnectionError(f"Ошибка соединения: {e}")
    except Exception as e:
        raise RuntimeError(f"Ошибка при получении данных: {e}")
