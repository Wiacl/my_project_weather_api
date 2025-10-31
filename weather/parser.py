import argparse

def create_parser() -> argparse.ArgumentParser:
    """
    Создаёт и возвращает объект парсера аргументов командной строки.

    Returns:
        argparse.ArgumentParser: настроенный парсер для обработки аргументов погодного приложения.
    """
    
    parser = argparse.ArgumentParser(description="Консольное приложение для получения прогноза погоды")
    
    parser.add_argument("city", type=str, nargs='?',default=None, help="Название города, например: Moscow")
    
    parser.add_argument("--lat", type=float, help="Широта (если используем координаты)")
    
    parser.add_argument("--lon", type=float, help="Долгота (если используем координаты)")
    
    parser.add_argument("--refresh", action="store_true", help="Игнорировать кэш и запросить новые данные")
    
    return parser
