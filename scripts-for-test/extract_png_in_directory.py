#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для организации файлов и папок.

Этот скрипт выполняет следующие задачи:
1. Переименовывает папки в указанной директории по порядковому номеру.
2. Удаляет папку 'TXT' и все файлы внутри каждой переименованной папки.
3. Перемещает все .png файлы из всех папок с именем TARGET_FOLDER_NAME в новые папки с номерами.
4. Удаляет подкаталоги на определенном уровне вложенности в каждой папке.
5. (Опционально) Группирует .png файлы по частям тела в папке Group_PNGs.
6. Отслеживает уже обработанные папки по названиям их немедленных подкаталогов в SOURCE_FOLDER, чтобы избежать повторной обработки.

Использование:
    python script.py SOURCE_FOLDER TARGET_FOLDER_NAME [--group]

Аргументы:
    SOURCE_FOLDER       Папка, в которой будет работать скрипт (исходная папка).
    TARGET_FOLDER_NAME  Название целевой папки, из которой будут браться .png файлы.

Опции:
    --group             Создает папку Group_PNGs для группировки .png файлов по частям тела.

Пример:
    python script.py SOURCE_FOLDER "Vector Parts" --group

Зависимости:
    - termcolor: Для цветного вывода сообщений в консоль.
      Установить можно с помощью pip:
          pip install termcolor
"""

import shutil
import argparse
import logging
from typing import Dict, Optional, List
from termcolor import colored
from pathlib import Path
import re
import json
import sys


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

    # Создаем файловый обработчик
    fh = logging.FileHandler("file_organizer.log", encoding="utf-8")
    fh.setLevel(logging.DEBUG)

    # Создаем и устанавливаем цветной форматтер
    formatter = ColoredFormatter("%(levelname)s: %(message)s")
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    # Добавляем обработчики к логгеру
    if not logger.handlers:
        logger.addHandler(ch)
        logger.addHandler(fh)

    return logger


# Инициализация логгера
logger = setup_logger()


def sanitize_name(name: str) -> str:
    """
    Санитизирует строку для использования в качестве имени папки или файла.
    Заменяет пробелы на подчеркивания, приводит к нижнему регистру и удаляет нежелательные символы.

    Args:
        name (str): Исходная строка.

    Returns:
        str: Санитизированная строка.
    """
    name = name.replace(" ", "_").lower()
    name = "".join(c for c in name if c.isalnum() or c == "_")
    return name


def extract_part_name(file_name: Path) -> str:
    """
    Извлекает название части тела из имени файла .png.

    Args:
        file_name (Path): Имя файла (например, "Left Arm.png").

    Returns:
        str: Название части тела (например, "Left Arm").
    """
    base_name = file_name.stem  # Удаление расширения
    return base_name


def initialize_group_info(group_destination_base: Path) -> Dict[str, int]:
    """
    Инициализирует словарь group_info, определяя текущие максимальные индексы для каждой части тела.

    Args:
        group_destination_base (Path): Базовая папка для группировки файлов по частям.

    Returns:
        Dict[str, int]: Словарь с максимальными индексами для каждой части тела.
    """
    group_info = {}
    if not group_destination_base.exists():
        return group_info

    for group_folder in group_destination_base.iterdir():
        if group_folder.is_dir():
            sanitized_part_name = sanitize_name(group_folder.name)
            # Используем регулярное выражение для извлечения индекса
            max_index = 0
            for file in group_folder.glob("*.png"):
                match = re.match(
                    rf"^{re.escape(sanitized_part_name)}_(\d+)\.png$", file.name
                )
                if match:
                    index = int(match.group(1))
                    if index > max_index:
                        max_index = index
            group_info[sanitized_part_name] = max_index
            logger.debug(
                f"Инициализирован индекс для '{sanitized_part_name}': {max_index}"
            )
    return group_info


def load_processed_folders(record_file: Path) -> set:
    """
    Загружает множество обработанных папок из файла учёта.

    Args:
        record_file (Path): Путь к файлу учёта обработанных папок.

    Returns:
        set: Множество названий немедленных подкаталогов, которые уже были обработаны.
    """
    if not record_file.exists():
        return set()
    try:
        with record_file.open("r", encoding="utf-8") as f:
            data = json.load(f)
            return set(data)
    except Exception as e:
        logger.error(
            f"Не удалось загрузить файл учёта обработанных папок '{record_file}': {e}"
        )
        return set()


def save_processed_folders(record_file: Path, processed_folders: set) -> None:
    """
    Сохраняет множество обработанных папок в файл учёта.

    Args:
        record_file (Path): Путь к файлу учёта обработанных папок.
        processed_folders (set): Множество названий немедленных подкаталогов, которые уже были обработаны.
    """
    try:
        with record_file.open("w", encoding="utf-8") as f:
            json.dump(list(processed_folders), f, ensure_ascii=False, indent=4)
        logger.debug(f"Сохранены обработанные папки в '{record_file}'")
    except Exception as e:
        logger.error(
            f"Не удалось сохранить файл учёта обработанных папок '{record_file}': {e}"
        )


def move_png_files(
    target_folder_path: Path,
    destination_folder: Path,
    group_info: Optional[Dict[str, int]] = None,
    group_destination_base: Optional[Path] = None,
) -> None:
    """
    Перемещает все .png файлы из указанной целевой папки в папку назначения.
    Если group_info и group_destination_base предоставлены, также группирует файлы по частям тела.

    Args:
        target_folder_path (Path): Полный путь к целевой папке для перемещения файлов.
        destination_folder (Path): Путь к папке, куда будут перемещены файлы.
        group_info (Dict[str, int], optional): Словарь для отслеживания количества файлов по частям.
        group_destination_base (Path, optional): Базовая папка для группировки файлов по частям.
    """
    for file in target_folder_path.glob("*.png"):
        if file.is_file():
            target_file_path = destination_folder / file.name
            if not target_file_path.exists():
                try:
                    shutil.move(str(file), str(target_file_path))
                    logger.info(
                        f"Файл '{file.name}' перемещен из '{target_folder_path}' в '{destination_folder}'"
                    )
                    # Если требуется группировка
                    if group_info is not None and group_destination_base is not None:
                        part_name = extract_part_name(file)
                        sanitized_part_name = sanitize_name(part_name)
                        if not sanitized_part_name:
                            logger.warning(
                                f"Не удалось санитизировать название части для файла '{file.name}'. Файл пропущен для группировки."
                            )
                            continue
                        group_folder = (
                            group_destination_base / sanitized_part_name.capitalize()
                        )
                        if not group_folder.exists():
                            group_folder.mkdir(parents=True, exist_ok=True)
                            logger.info(
                                f"Создана папка для части тела: '{group_folder}'"
                            )
                        # Обновляем счетчик
                        count = group_info.get(sanitized_part_name, 0) + 1
                        group_info[sanitized_part_name] = count
                        # Новое имя файла
                        new_file_name = f"{sanitized_part_name}_{count}.png"
                        group_file_path = group_folder / new_file_name
                        try:
                            shutil.copy(str(target_file_path), str(group_file_path))
                            logger.info(
                                f"Файл '{file.name}' скопирован в '{group_file_path}'"
                            )
                        except Exception as e:
                            logger.error(
                                f"Не удалось скопировать файл '{file.name}' в '{group_file_path}': {e}"
                            )
                except Exception as e:
                    logger.error(
                        f"Не удалось переместить файл '{file.name}' из '{target_folder_path}' в '{destination_folder}': {e}"
                    )
            else:
                logger.warning(
                    f"Файл '{file.name}' уже существует в '{destination_folder}', перемещение отменено"
                )


def delete_directories_at_specific_level(start_path: Path) -> None:
    """
    Удаляет все подкаталоги на определенном уровне вложенности в заданной папке.

    Args:
        start_path (Path): Путь к начальной папке для удаления подкаталогов.
    """
    for dir_path in start_path.rglob("*"):
        if dir_path.is_dir():
            for sub_dir in dir_path.iterdir():
                if sub_dir.is_dir():
                    try:
                        shutil.rmtree(sub_dir)
                        logger.info(f"Папка '{sub_dir}' удалена")
                    except Exception as e:
                        logger.error(f"Не удалось удалить папку '{sub_dir}': {e}")


def delete_files_in_folder(folder_path: Path) -> None:
    """
    Удаляет все файлы в указанной папке.

    Args:
        folder_path (Path): Путь к папке, из которой нужно удалить файлы.
    """
    for file in folder_path.iterdir():
        if file.is_file():
            try:
                file.unlink()
                logger.info(f"Файл '{file.name}' удален")
            except Exception as e:
                logger.error(f"Не удалось удалить файл '{file.name}': {e}")


def rename_folders_and_clean_files(
    start_path: Path,
    target_folder_name: str,
    group: bool = False,
    record_file: Optional[Path] = None,
) -> None:
    """
    Переименовывает папки в заданной директории по порядковому номеру,
    удаляет папку 'TXT' и все файлы внутри каждой переименованной папки,
    перемещает .png файлы и удаляет подкаталоги на определенном уровне.
    При наличии флага group, группирует .png файлы по частям тела.
    Также отслеживает уже обработанные папки по названиям их немедленных подкаталогов в SOURCE_FOLDER, чтобы избежать повторной обработки.

    Args:
        start_path (Path): Начальная директория для обработки.
        target_folder_name (str): Имя целевой папки для перемещения файлов.
        group (bool, optional): Флаг для группировки файлов по частям тела. По умолчанию False.
        record_file (Path, optional): Путь к файлу учёта обработанных папок. Если не указан, используется 'processed_folders.json' в start_path.
    """
    if record_file is None:
        record_file = start_path / "processed_folders.json"

    # Загрузка уже обработанных папок
    processed_folders = load_processed_folders(record_file)

    # Поиск всех целевых папок внутри start_path
    target_folders = list(start_path.rglob(target_folder_name))
    logger.debug(f"Найдено {len(target_folders)} папок с именем '{target_folder_name}'")

    if not target_folders:
        logger.warning(
            f"Не найдено ни одной папки с именем '{target_folder_name}' внутри '{start_path}'."
        )
        return

    # Группировка целевых папок по названиям немедленных подкаталогов в SOURCE_FOLDER
    groups: Dict[str, List[Path]] = {}
    for target_folder_path in target_folders:
        try:
            relative_path = target_folder_path.relative_to(start_path)
            # Извлечение названия немедленного подкаталога (первый уровень)
            immediate_subfolder_name = relative_path.parts[0]
            if immediate_subfolder_name not in groups:
                groups[immediate_subfolder_name] = []
            groups[immediate_subfolder_name].append(target_folder_path)
        except ValueError:
            logger.error(
                f"Папка '{target_folder_path}' не находится внутри '{start_path}'. Пропуск."
            )
            continue

    # Создание папки 'Organized_PNGs' для перемещенных файлов
    organized_pngs = start_path / "Organized_PNGs"
    if not organized_pngs.exists():
        try:
            organized_pngs.mkdir(parents=True, exist_ok=True)
            logger.info(f"Создана папка для перемещения PNG файлов: '{organized_pngs}'")
        except Exception as e:
            logger.error(f"Не удалось создать папку '{organized_pngs}': {e}")
            return

    # Если group is True, создаём папку 'Group_PNGs'
    if group:
        group_pngs = start_path / "Group_PNGs"
        if not group_pngs.exists():
            try:
                group_pngs.mkdir(parents=True, exist_ok=True)
                logger.info(f"Создана папка для группировки PNG файлов: '{group_pngs}'")
            except Exception as e:
                logger.error(f"Не удалось создать папку '{group_pngs}': {e}")
                group = False  # Отключаем группировку, если не удалось создать папку
        # Инициализация счетчиков для частей тела
        group_info: Dict[str, int] = initialize_group_info(group_pngs)
    else:
        group_pngs = None
        group_info = None

    # Перемещение файлов и переименование папок по группам
    for immediate_subfolder_name, folders in groups.items():
        # Проверка, была ли уже обработана группа папок с этим именем
        if immediate_subfolder_name in processed_folders:
            logger.info(
                f"Группа папок с названием '{immediate_subfolder_name}' уже была обработана. Пропуск."
            )
            continue

        logger.debug(
            f"Обработка группы папок '{immediate_subfolder_name}' с {len(folders)} целевыми папками."
        )

        # Создание новой папки с порядковым номером для каждой целевой папки
        for index, target_folder_path in enumerate(folders, start=1):
            new_folder_name = f"{immediate_subfolder_name}_{index}"
            new_folder_path = organized_pngs / new_folder_name

            # Создание новой папки с уникальным именем
            try:
                new_folder_path.mkdir(parents=True, exist_ok=True)
                logger.info(
                    f"Создана папка '{new_folder_path}' для перемещения файлов."
                )
            except Exception as e:
                logger.error(f"Не удалось создать папку '{new_folder_path}': {e}")
                continue

            # Перемещение .png файлов
            move_png_files(target_folder_path, new_folder_path, group_info, group_pngs)

            # Удаление папки 'TXT', если она существует внутри целевой папки
            txt_folder_path = target_folder_path / "TXT"
            if txt_folder_path.exists() and txt_folder_path.is_dir():
                try:
                    shutil.rmtree(txt_folder_path)
                    logger.info(f"Папка 'TXT' удалена из '{target_folder_path}'")
                except Exception as e:
                    logger.error(
                        f"Не удалось удалить папку 'TXT' из '{target_folder_path}': {e}"
                    )

            # Удаление всех файлов в целевой папке
            delete_files_in_folder(target_folder_path)

            # Удаление подкаталогов на определенном уровне вложенности
            delete_directories_at_specific_level(target_folder_path)

        # После успешной обработки всех целевых папок в группе, добавляем название немедленного подкаталога в учёт
        processed_folders.add(immediate_subfolder_name)
        logger.debug(
            f"Группа папок '{immediate_subfolder_name}' добавлена в учёт обработанных папок."
        )

    # Сохранение обновлённого списка обработанных папок
    save_processed_folders(record_file, processed_folders)

    # Завершение группировки
    if group:
        logger.info("Группировка PNG файлов завершена.")


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
        "source_folder",
        type=str,
        help="Папка, в которой будет работать скрипт (исходная папка).",
    )
    parser.add_argument(
        "target_folder_name",
        type=str,
        help="Название целевой папки, из которой будут браться .png файлы.",
    )
    parser.add_argument(
        "--group",
        action="store_true",
        help="Создает папку Group_PNGs для группировки .png файлов по частям тела.",
    )
    return parser.parse_args()


def main() -> None:
    """
    Главная функция скрипта. Обрабатывает аргументы и выполняет основную логику.
    """
    try:
        args = parse_arguments()

        source_folder = Path(args.source_folder).resolve()
        target_folder_name = args.target_folder_name.strip('"').strip(
            "'"
        )  # Удаление лишних кавычек

        logger.debug(
            f"Parsed arguments: source_folder='{source_folder}', target_folder_name='{target_folder_name}', group={args.group}"
        )

        # Проверка существования исходной папки
        if not source_folder.is_dir():
            logger.error(
                f"Исходная папка '{source_folder}' не существует или не является директорией."
            )
            return

        logger.info(
            f"Начало обработки. Исходная папка: '{source_folder}', Целевая папка: '{target_folder_name}'"
        )
        rename_folders_and_clean_files(
            source_folder, target_folder_name, group=args.group
        )
        logger.info("Обработка завершена.")
    except Exception as e:
        logger.critical(f"Необработанная ошибка: {e}", exc_info=True)


if __name__ == "__main__":
    main()
