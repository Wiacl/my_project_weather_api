"""
Основной модуль для обработки команд и вывода погоды.
Добавлен цветной вывод с помощью colorama.
"""

from colorama import Fore, Style, init
from .parser import create_parser
from .api import get_weather
from .cache import read_cache, write_cache

# Инициализация colorama (для Windows и других систем)
init(autoreset=True)


def handle_command(args) -> None:
    """
    Обрабатывает команду пользователя: получает или кэширует погоду.
    """
    city = args.city
    lat = args.lat
    lon = args.lon
    refresh = args.refresh

    # ✅ Проверяем ввод
    if not city and (lat is None or lon is None):
        print(f"{Fore.RED}⚠ Ошибка: нужно указать либо название города, либо координаты (--lat и --lon){Style.RESET_ALL}")
        return

    # Создаём ключ для кэша (по городу или координатам)
    cache_key = city or f"{lat},{lon}"

    # Проверяем кэш, если не нужно обновление
    if not refresh:
        cached = read_cache(cache_key)
        if cached:
            print(f"{Fore.GREEN}✅ Погода для {cache_key} (из кэша):{Style.RESET_ALL}")
            print_weather(cached)
            return

    # Если кэша нет — запрашиваем из API
    try:
        # ИСПРАВЛЕНИЕ: передаем правильные имена параметров
        data = get_weather(city=city, lat=lat, lon=lon)
        write_cache(cache_key, data)
        print(f"{Fore.CYAN}🌤 Погода для {data.get('city', cache_key)}:{Style.RESET_ALL}")
        print_weather(data)
    except Exception as e:
        print(f"{Fore.RED}⚠ Ошибка: {e}{Style.RESET_ALL}")


def print_weather(weather_data) -> None:
    """
    Форматированный и цветной вывод текущей погоды.
    """
    current = weather_data.get("current_weather", {})
    print(f"{Fore.YELLOW}────────────────────────────{Style.RESET_ALL}")
    print(f"{Fore.GREEN}Город/координаты:{Style.RESET_ALL} {weather_data.get('city', '—')}")
    print(f"{Fore.GREEN}Координаты:{Style.RESET_ALL} {weather_data.get('latitude')}°, {weather_data.get('longitude')}°")
    print(f"{Fore.YELLOW}────────────────────────────{Style.RESET_ALL}")
    print(f"{Fore.BLUE}Температура:{Style.RESET_ALL} {current.get('temperature')} °C")
    print(f"{Fore.BLUE}Скорость ветра:{Style.RESET_ALL} {current.get('windspeed')} км/ч")
    print(f"{Fore.BLUE}Направление ветра:{Style.RESET_ALL} {current.get('winddirection')}°")
    print(f"{Fore.MAGENTA}Время измерения:{Style.RESET_ALL} {current.get('time')}")
    print(f"{Fore.YELLOW}────────────────────────────{Style.RESET_ALL}")