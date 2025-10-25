import argparse

def create_parser() -> argparse.ArgumentParser:
    """
    Создаёт и возвращает объект парсера аргументов командной строки.

    Returns:
        argparse.ArgumentParser: настроенный парсер.
    """
    parser = argparse.ArgumentParser(description="Консольное приложение для получения прогноза погоды")
    parser.add_argument("city", type=str, help="Название города, например: Moscow")
    parser.add_argument("--refresh", action="store_true", help="Игнорировать кэш и запросить новые данные")
    parser.add_argument("--hours", type=int, default=24, help="Количество часов для прогноза (по умолчанию 24)")
    return parser
