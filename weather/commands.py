"""
Основной модуль для обработки команд и вывода погоды.
"""

from .parser import create_parser
from .api import get_weather
from .cache import read_cache, write_cache

def handle_command(args) -> None:
    """
    Обрабатывает команду пользователя: получает или кэширует погоду.
    """
    city = args.city
    lat = args.lat
    lon = args.lon
    refresh = args.refresh

    cache_key = city or f"{lat},{lon}"

    if not refresh:
        cached = read_cache(cache_key)
        if cached:
            print(f"✅ Погода для {cache_key} (из кэша):")
            print_weather(cached)
            return

    try:
        data = get_weather(city=city, latitude=lat, longitude=lon)
        write_cache(cache_key, data)
        print(f"🌤 Погода для {cache_key}:")
        print_weather(data)
    except Exception as e:
        print(f"⚠ Ошибка: {e}")


def print_weather(weather_data) -> None:
    """
    Форматированный вывод текущей погоды.
    """
    current = weather_data.get("current_weather", {})
    print(f"Город: {weather_data.get('city', '—')}")
    print(f"Координаты: {weather_data.get('latitude')}°, {weather_data.get('longitude')}°")
    print("────────────────────────────")
    print(f"Температура: {current.get('temperature')} °C")
    print(f"Скорость ветра: {current.get('windspeed')} км/ч")
    print(f"Направление ветра: {current.get('winddirection')}°")
    print(f"Время измерения: {current.get('time')}")
