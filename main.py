from weather import commands

def main() -> None:
    """
    Точка входа в приложение.
    Обрабатывает аргументы и вызывает выполнение команды.
    """
    parser = commands.create_parser()
    args = parser.parse_args()
    commands.handle_command(args)

if __name__ == "__main__":
    main()
