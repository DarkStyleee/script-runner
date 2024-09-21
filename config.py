# config.py

import json
import os
from constants import (
    DEFAULT_THEME,
    DEFAULT_WINDOW_SIZE,
    DEFAULT_HOTKEYS,
    DEFAULT_COLORED_OUTPUT,
)


class ConfigManager:
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = {}
        self.load_config()

    def load_config(self):
        """Загрузка конфигурации из файла или установка значений по умолчанию."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
            except Exception as e:
                print(f"Ошибка загрузки конфигурации: {e}")
                self.set_defaults()
        else:
            self.set_defaults()
            self.save_config()

    def set_defaults(self):
        """Установка значений конфигурации по умолчанию."""
        self.config = {
            "theme": DEFAULT_THEME,
            "scripts": [],
            "window_size": DEFAULT_WINDOW_SIZE,
            "hotkeys": DEFAULT_HOTKEYS,
            "colored_output": DEFAULT_COLORED_OUTPUT,
        }

    def save_config(self):
        """Сохранение конфигурации в файл."""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Ошибка сохранения конфигурации: {e}")

    def get(self, key, default=None):
        """Получение значения из конфигурации."""
        return self.config.get(key, default)

    def update(self, key, value):
        """Обновление значения в конфигурации."""
        self.config[key] = value
        self.save_config()
