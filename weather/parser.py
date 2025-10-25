import argparse

def create_parser():
    parser = argparse.ArgumentParser(description="Погодное приложение (через Open-Meteo API)")
    parser.add_argument("city", type=str, help="Название города (например: Moscow)")
    parser.add_argument("--refresh", action="store_true", help="Игнорировать кэш и запросить новые данные")
    return parser
