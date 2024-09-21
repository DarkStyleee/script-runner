import os
import sys


def create_new_directory(path):
    try:
        os.makedirs(path, exist_ok=True)
        print(f"Директория '{path}' успешно создана (или уже существует).")
    except Exception as e:
        print(f"Ошибка при создании директории: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python create_directory.py <путь_для_новой_директории>")
    else:
        path = sys.argv[1]
        create_new_directory(path)
