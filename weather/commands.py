from .parser import create_parser
from .api import get_weather
from .cache import read_cache, write_cache

def handle_command(args) -> None:
    """
    Обрабатывает команду пользователя: получает погоду и выводит результат.
    """
    city = args.city
    refresh = args.refresh
    hours = args.hours

    # Пытаемся прочитать данные из кэша
    if not refresh:
        cached = read_cache(city)
        if cached:
            print(f"✅ Погода для {city} (из кэша):")
            print_weather(cached)
            return

    # Иначе — запрос к API
    try:
        weather = get_weather(city, hours)
        write_cache(city, weather)
        print(f"🌤 Погода для {city}:")
        print_weather(weather)
    except Exception as e:
        print(f"⚠ Ошибка: {e}")


def print_weather(weather_data) -> None:
    """
    Форматирует и выводит прогноз в консоль.

    Args:
        weather_data (dict): Погодные данные.
    """
    print(f"Город: {weather_data['city']}")
    print(f"Координаты: {weather_data['latitude']}°, {weather_data['longitude']}°")
    print("\nПочасовая температура (°C):")

    for record in weather_data["data"]:
        time = record["datetime"]
        temp = record["temperature_2m"]
        print(f"{time} — {temp}°C")
