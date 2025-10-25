from parser import create_parser
from api import get_weather
from cache import read_cache, write_cache

def handle_command(args):
    city = args.city
    refresh = args.refresh

    if not refresh:
        cached = read_cache(city)
        if cached:
            print(f"✅ Погода для {city} (из кэша):")
            print_weather(cached)
            return

    try:
        weather_data = get_weather(city)
        write_cache(city, weather_data)
        print(f"🌤 Погода для {city}:")
        print_weather(weather_data)
    except Exception as e:
        print(f"⚠ Ошибка: {e}")

def print_weather(weather):
    temp = weather.get("temperature")
    wind = weather.get("windspeed")
    print(f"Температура: {temp}°C, Ветер: {wind} км/ч")
