#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для организации файлов и папок.

Этот скрипт выполняет следующие задачи:
1. Переименовывает папки в указанной директории по порядковому номеру.
2. Удаляет папку 'TXT' и все файлы внутри каждой переименованной папки.
3. Перемещает все .png файлы из определенной папки в целевую папку.
4. Удаляет подкаталоги на определенном уровне вложенности в каждой папке.

Использование:
    python script.py [-f TARGET_FOLDER_NAME]

Аргументы:
    -f, --folder    Название целевой папки для обработки. По умолчанию "Vector Parts".

Пример:
    python script.py --folder "Images"

Зависимости:
    - termcolor: Для цветного вывода сообщений в консоль.
      Установить можно с помощью pip:
          pip install termcolor
"""

import os
import shutil
import argparse
import logging
from typing import List
from termcolor import colored


# Настройка логирования с поддержкой цветов
class ColoredFormatter(logging.Formatter):
    """
    Форматтер для логирования с поддержкой цветов.
    """

    # Определение цветов для разных уровней логирования
    COLORS = {
        logging.DEBUG: "cyan",
        logging.INFO: "green",
        logging.WARNING: "yellow",
        logging.ERROR: "red",
        logging.CRITICAL: "magenta",
    }

    def format(self, record: logging.LogRecord) -> str:
        log_color = self.COLORS.get(record.levelno, "white")
        message = super().format(record)
        return colored(message, log_color)


def setup_logger() -> logging.Logger:
    """
    Настраивает и возвращает логгер с цветным выводом.

    Returns:
        logging.Logger: Настроенный логгер.
    """
    logger = logging.getLogger("FileOrganizer")
    logger.setLevel(logging.DEBUG)  # Устанавливаем минимальный уровень логирования

    # Создаем консольный обработчик
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # Создаем и устанавливаем цветной форматтер
    formatter = ColoredFormatter("%(levelname)s: %(message)s")
    ch.setFormatter(formatter)

    # Добавляем обработчик к логгеру
    if not logger.handlers:
        logger.addHandler(ch)

    return logger


# Инициализация логгера
logger = setup_logger()


def move_png_files(source_folder: str, target_folder_name: str) -> None:
    """
    Перемещает все .png файлы из папки с именем target_folder_name
    в родительскую папку, если файлы с такими именами отсутствуют в целевой папке.

    Args:
        source_folder (str): Путь к исходной папке для поиска файлов.
        target_folder_name (str): Имя целевой папки для перемещения файлов.
    """
    for root, _, files in os.walk(source_folder, topdown=False):
        if os.path.basename(root) == target_folder_name:
            # Определяем целевую папку как родительскую папку target_folder_name
            target_folder = os.path.dirname(os.path.dirname(root))
            for file in files:
                if file.lower().endswith(".png"):
                    source_file_path = os.path.join(root, file)
                    target_file_path = os.path.join(target_folder, file)
                    if not os.path.exists(target_file_path):
                        try:
                            shutil.move(source_file_path, target_file_path)
                            logger.info(
                                f"Файл '{file}' перемещен из '{root}' в '{target_folder}'"
                            )
                        except Exception as e:
                            logger.error(
                                f"Не удалось переместить файл '{file}' из '{root}' в '{target_folder}': {e}"
                            )
                    else:
                        logger.warning(
                            f"Файл '{file}' уже существует в '{target_folder}', перемещение отменено"
                        )


def delete_directories_at_specific_level(start_path: str) -> None:
    """
    Удаляет все подкаталоги на определенном уровне вложенности в заданной папке.

    Args:
        start_path (str): Путь к начальной папке для удаления подкаталогов.
    """
    for root, dirs, _ in os.walk(start_path, topdown=True):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            if os.path.isdir(dir_path):
                for sub_dir in os.listdir(dir_path):
                    sub_dir_path = os.path.join(dir_path, sub_dir)
                    if os.path.isdir(sub_dir_path):
                        try:
                            shutil.rmtree(sub_dir_path)
                            logger.info(f"Папка '{sub_dir_path}' удалена")
                        except Exception as e:
                            logger.error(
                                f"Не удалось удалить папку '{sub_dir_path}': {e}"
                            )


def delete_files_in_folder(folder_path: str) -> None:
    """
    Удаляет все файлы в указанной папке.

    Args:
        folder_path (str): Путь к папке, из которой нужно удалить файлы.
    """
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isfile(item_path):
            try:
                os.remove(item_path)
                logger.info(f"Файл '{item}' удален")
            except Exception as e:
                logger.error(f"Не удалось удалить файл '{item}': {e}")


def rename_folders_and_clean_files(start_path: str, target_folder_name: str) -> None:
    """
    Переименовывает папки в заданной директории по порядковому номеру,
    удаляет папку 'TXT' и все файлы внутри каждой переименованной папки,
    перемещает .png файлы и удаляет подкаталоги на определенном уровне.

    Args:
        start_path (str): Начальная директория для обработки.
        target_folder_name (str): Имя целевой папки для перемещения файлов.
    """
    # Получаем список всех папок в start_path и сортируем их
    folders: List[str] = [
        folder
        for folder in os.listdir(start_path)
        if os.path.isdir(os.path.join(start_path, folder))
    ]
    folders.sort()

    for index, folder in enumerate(folders, start=1):
        new_name = str(index)
        original_path = os.path.join(start_path, folder)
        new_path = os.path.join(start_path, new_name)

        try:
            # Переименовываем папку
            os.rename(original_path, new_path)
            logger.info(f"Папка '{folder}' переименована в '{new_name}'")
        except Exception as e:
            logger.error(
                f"Не удалось переименовать папку '{folder}' в '{new_name}': {e}"
            )
            continue  # Переход к следующей папке при ошибке

        # Удаляем папку 'TXT', если она существует
        txt_folder_path = os.path.join(new_path, "TXT")
        if os.path.exists(txt_folder_path):
            try:
                shutil.rmtree(txt_folder_path)
                logger.info(f"Папка 'TXT' удалена из '{new_path}'")
            except Exception as e:
                logger.error(f"Не удалось удалить папку 'TXT' из '{new_path}': {e}")

        # Удаляем все файлы в переименованной папке
        delete_files_in_folder(new_path)

        # Перемещаем .png файлы в целевую папку
        move_png_files(new_path, target_folder_name)

        # Удаляем подкаталоги на определенном уровне
        delete_directories_at_specific_level(new_path)


def parse_arguments() -> argparse.Namespace:
    """
    Парсит аргументы командной строки.

    Returns:
        argparse.Namespace: Объект с атрибутами, содержащими значения аргументов.
    """
    parser = argparse.ArgumentParser(
        description="Скрипт для организации файлов и папок."
    )
    parser.add_argument(
        "-f",
        "--folder",
        type=str,
        default="Vector Parts",
        help="Название целевой папки для обработки.",
    )
    return parser.parse_args()


def main() -> None:
    """
    Главная функция скрипта. Обрабатывает аргументы и выполняет основную логику.
    """
    args = parse_arguments()
    logger.info(f"Начало обработки. Целевая папка: '{args.folder}'")
    rename_folders_and_clean_files(".", args.folder)
    logger.info("Обработка завершена.")


if __name__ == "__main__":
    main()
