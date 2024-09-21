"""
Скрипт list_directory.py

Описание:
    Этот скрипт выводит содержимое указанной директории.

Использование:
    python list_directory.py <путь_к_директории>

Пример:
    python list_directory.py C:/Users/Username/Documents
"""

import os
import sys

# ANSI цветовые коды
COLOR_RESET = "\033[0m"
COLOR_DIR = "\033[34m"  # Синий
COLOR_FILE = "\033[32m"  # Зеленый
COLOR_ERROR = "\033[31m"  # Красный
COLOR_INFO = "\033[33m"  # Желтый


def list_directory_contents(directory):
    try:
        items = os.listdir(directory)
        if not items:
            print(f"{COLOR_INFO}Директория '{directory}' пуста.{COLOR_RESET}")
            return
        print(f"{COLOR_INFO}Содержимое директории '{directory}':{COLOR_RESET}")
        for item in items:
            path = os.path.join(directory, item)
            if os.path.isdir(path):
                print(f"{COLOR_DIR}[DIR]  {item}{COLOR_RESET}")
            else:
                print(f"{COLOR_FILE}       {item}{COLOR_RESET}")
    except FileNotFoundError:
        print(f"{COLOR_ERROR}Директория '{directory}' не найдена.{COLOR_RESET}")
    except PermissionError:
        print(f"{COLOR_ERROR}Нет доступа к директории '{directory}'.{COLOR_RESET}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            f"{COLOR_ERROR}Использование: python list_directory.py <путь_к_директории>{COLOR_RESET}"
        )
    else:
        directory = sys.argv[1]
        list_directory_contents(directory)
