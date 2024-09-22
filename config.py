# config.py

import json
import os


class ConfigManager:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        """Загрузка конфигурации из JSON файла."""
        if os.path.exists(self.config_file):
            with open(self.config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            return {}

    def save_config(self):
        """Сохранение текущей конфигурации в JSON файл."""
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)

    def update(self, key, value):
        """Обновление ключа конфигурации новым значением и сохранение."""
        self.config[key] = value
        self.save_config()
