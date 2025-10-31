from weather import commands
from weather.parser import create_parser

def main() -> None:
    """
    Точка входа в приложение.
    Обрабатывает аргументы и вызывает выполнение команды.
    """
    parser = create_parser()  # ИСПРАВЛЕНИЕ: используем правильную функцию
    args = parser.parse_args()
    commands.handle_command(args)

if __name__ == "__main__":
    main()  