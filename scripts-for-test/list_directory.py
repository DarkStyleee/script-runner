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


def list_directory_contents(directory):
    try:
        items = os.listdir(directory)
        if not items:
            print(f"Директория '{directory}' пуста.")
            return
        print(f"Содержимое директории '{directory}':")
        for item in items:
            path = os.path.join(directory, item)
            if os.path.isdir(path):
                print(f"[DIR]  {item}")
            else:
                print(f"       {item}")
    except FileNotFoundError:
        print(f"Директория '{directory}' не найдена.")
    except PermissionError:
        print(f"Нет доступа к директории '{directory}'.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python list_directory.py <путь_к_директории>")
    else:
        directory = sys.argv[1]
        list_directory_contents(directory)
