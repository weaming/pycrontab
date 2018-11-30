import argparse
import logging
from .config import parse_configs_and_run


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config", default="crontab.yml", help="config file path"
    )
    parser.add_argument(
        "-l",
        "--log-level",
        default="INFO",
        help="logging level",
        choices=["INFO", "DEBUG", "WARNING"],
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="{asctime} {levelname} {name}({processName}|{threadName})>{filename}:{funcName}()#{lineno} : {message}",
        style="{",
    )
    parse_configs_and_run(args.config)


if __name__ == "__main__":
    main()
