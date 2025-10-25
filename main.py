import argparse
from weather import commands

def main():
    parser = commands.create_parser()
    args = parser.parse_args()
    commands.handle_command(args)

if __name__ == "__main__":
    main()
    