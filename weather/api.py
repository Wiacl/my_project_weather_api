"""
Модуль для работы с Open-Meteo API с использованием официальной библиотеки openmeteo_requests.
"""

import pandas as pd
import openmeteo_requests
import requests_cache
from retry_requests import retry
import requests
from typing import Dict, Any

def get_coordinates(city: str) -> tuple[float, float]:
    """
    Получает координаты города через Open-Meteo Geocoding API.

    Args:
        city (str): Название города.

    Returns:
        tuple[float, float]: Кортеж (широта, долгота).
    """
    geocode_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=ru"
    response = requests.get(geocode_url, timeout=10)
    response.raise_for_status()
    data = response.json()

    if not data.get("results"):
        raise ValueError(f"Город '{city}' не найден.")

    return data["results"][0]["latitude"], data["results"][0]["longitude"]


def get_weather_data(latitude: float, longitude: float, hours: int = 24) -> pd.DataFrame:
    """
    Получает почасовой прогноз температуры для указанных координат.

    Args:
        latitude (float): Широта.
        longitude (float): Долгота.
        hours (int): Количество часов прогноза (по умолчанию 24).

    Returns:
        pd.DataFrame: Таблица с температурой по часам.
    """
    # Настраиваем клиент Open-Meteo с кэшем и повторными попытками
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    # Запрашиваем температуру по API
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m",
    }

    try:
        responses = openmeteo.weather_api(url, params=params)
    except Exception as e:
        raise ConnectionError(f"Ошибка при обращении к API Open-Meteo: {e}")

    response = responses[0]
    hourly = response.Hourly()
    hourly_temperature = hourly.Variables(0).ValuesAsNumpy()

    # Создаём DataFrame
    hourly_data = {
        "datetime": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left",
        ),
        "temperature_2m": hourly_temperature,
    }

    df = pd.DataFrame(hourly_data).head(hours)
    return df


def get_weather(city: str, hours: int = 24) -> Dict[str, Any]:
    """
    Получает прогноз погоды по названию города.

    Args:
        city (str): Название города.
        hours (int): Количество часов для прогноза.

    Returns:
        dict: Словарь с погодными данными.
    """
    try:
        lat, lon = get_coordinates(city)
        weather_df = get_weather_data(lat, lon, hours)
        return {
            "city": city,
            "latitude": lat,
            "longitude": lon,
            "data": weather_df.to_dict(orient="records"),
        }
    except Exception as e:
        raise RuntimeError(f"Не удалось получить данные для '{city}': {e}")
