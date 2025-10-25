import requests

def get_weather(city: str):
    """Возвращает данные о погоде по названию города."""
    try:
        # Используем API для получения координат
        geocode_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=ru"
        geo_resp = requests.get(geocode_url, timeout=10)
        geo_resp.raise_for_status()
        geo_data = geo_resp.json()

        if "results" not in geo_data or not geo_data["results"]:
            raise ValueError(f"Город '{city}' не найден.")

        lat = geo_data["results"][0]["latitude"]
        lon = geo_data["results"][0]["longitude"]

        # Получаем погоду
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        )
        weather_resp = requests.get(weather_url, timeout=10)
        weather_resp.raise_for_status()
        return weather_resp.json()["current_weather"]

    except requests.RequestException as e:
        raise ConnectionError(f"Ошибка соединения: {e}")
    except Exception as e:
        raise RuntimeError(f"Ошибка при получении погоды: {e}")
