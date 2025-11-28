"""
Основной модуль для обработки команд и вывода погоды.
Добавлен цветной вывод с помощью colorama.
Добавлена БД.
"""

from colorama import Fore, Style, init
from .api import get_weather
from .cache import read_cache, write_cache
from .database import db

# Инициализация colorama 
init(autoreset=True)


def handle_command(args) -> None:
    """
    Обрабатывает команду пользователя: получает или кэширует погоду.
    
    Args:
        args: Объект с аргументами командной строки, содержащий:
            - city: название города
            - lat: широта
            - lon: долгота  
            - refresh: флаг принудительного обновления кэша
            - history: показать историю запросов
            - stats: показать статистику
    """
    
    # Извлекаем аргументы из командной строки
    
    city = args.city
    lat = args.lat
    lon = args.lon
    refresh = args.refresh
    history = getattr(args, 'history', False)
    stats = getattr(args, 'stats', False)
    
     # Инициализируем базу данных при первом запуске
    try:
        db.init_db()
    except Exception as e:
        print(f"{Fore.YELLOW}⚠ Предупреждение: Не удалось инициализировать БД: {e}{Style.RESET_ALL}")

    # Обработка команды истории
    if history and city:
        show_weather_history(city)
        return
    
    # Обработка команды статистики
    if stats and city:
        show_weather_stats(city)
        return
    
    # проверяем ввод
    
    if not city and (lat is None or lon is None):
        print(f"{Fore.RED} Ошибка: нужно указать либо название города, либо координаты (--lat и --lon){Style.RESET_ALL}")
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
        data = get_weather(city=city, lat=lat, lon=lon)
        write_cache(cache_key, data)
        
        # Сохраняем в базу данных
        try:
            db.save_weather_data(data)
        except Exception as e:
            print(f"{Fore.YELLOW}⚠ Не удалось сохранить в БД: {e}{Style.RESET_ALL}")
        
        print_weather(data)
    except Exception as e:
        print(f"{Fore.RED}⚠ Ошибка: {e}{Style.RESET_ALL}")


def print_weather(weather_data) -> None:
    """
    Форматированный и цветной вывод текущей погоды.
    
    Args:
        weather_data (dict): Словарь с данными о погоде, содержащий:
            - city: название города
            - latitude, longitude: координаты
            - current_weather: словарь с текущей погодой
    """
    # Извлекаем данные о текущей погоде, если нет - используем пустой словарь
    
    current = weather_data.get("current_weather", {})
    
    print(f"{Fore.GREEN}Город/координаты:{Style.RESET_ALL} {weather_data.get('city', '—')}")
    
    print(f"{Fore.GREEN}Координаты:{Style.RESET_ALL} {weather_data.get('latitude')}°, {weather_data.get('longitude')}°")
    
    print(f"{Fore.YELLOW}────────────────────────────{Style.RESET_ALL}")
    
    print(f"{Fore.BLUE}Температура:{Style.RESET_ALL} {current.get('temperature')} °C")
    
    print(f"{Fore.BLUE}Скорость ветра:{Style.RESET_ALL} {current.get('windspeed')} км/ч")
    
    print(f"{Fore.BLUE}Направление ветра:{Style.RESET_ALL} {current.get('winddirection')}°")
    
    print(f"{Fore.MAGENTA}Время измерения:{Style.RESET_ALL} {current.get('time')}")
    
    print(f"{Fore.YELLOW}────────────────────────────{Style.RESET_ALL}")
    
def show_weather_history(city: str, limit: int = 5) -> None:
    """
    Показывает историю запросов погоды для города
    
    Args:
        city: Название города
        limit: Количество записей для показа
    """
    try:
        records = db.get_recent_weather(city, limit)
        
        if not records:
            print(f"{Fore.YELLOW}История запросов для города '{city}' не найдена.{Style.RESET_ALL}")
            return
        
        print(f"{Fore.CYAN} История погоды для {city} (последние {len(records)} записей):{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}────────────────────────────{Style.RESET_ALL}")
        
        for i, record in enumerate(records, 1):
            print(f"{Fore.GREEN}Запись #{i}:{Style.RESET_ALL}")
            print(f"  Температура: {record['temperature']} °C")
            print(f"  Ветер: {record['wind_speed']} км/ч, направление: {record['wind_direction']}°")
            print(f"  Время данных: {record['weather_time']}")
            print(f"  Записано: {record['recorded_at']}")
            print(f"{Fore.YELLOW}────────────────────────────{Style.RESET_ALL}")
            
    except Exception as e:
        print(f"{Fore.RED}Ошибка при получении истории: {e}{Style.RESET_ALL}")


def show_weather_stats(city: str, days: int = 7) -> None:
    """
    Показывает статистику погоды за указанный период
    
    Args:
        city: Название города
        days: Количество дней для анализа
    """
    try:
        stats = db.get_weather_stats(city, days)
        
        if not stats or not stats.get('records_count'):
            print(f"{Fore.YELLOW}Статистика для города '{city}' за последние {days} дней не найдена.{Style.RESET_ALL}")
            return
        
        print(f"{Fore.CYAN} Статистика погоды для {city} за последние {days} дней:{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}────────────────────────────{Style.RESET_ALL}")
        print(f"Количество записей: {stats['records_count']}")
        print(f"Средняя температура: {stats['avg_temp']:.1f} °C")
        print(f"Максимальная температура: {stats['max_temp']:.1f} °C")
        print(f"Минимальная температура: {stats['min_temp']:.1f} °C")
        print(f"Средняя скорость ветра: {stats['avg_wind']:.1f} км/ч")
        print(f"{Fore.YELLOW}────────────────────────────{Style.RESET_ALL}")
        
    except Exception as e:
        print(f"{Fore.RED}Ошибка при получении статистики: {e}{Style.RESET_ALL}")