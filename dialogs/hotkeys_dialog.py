# dialogs/hotkeys_dialog.py

import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from utils import center_window


class HotkeysDialog:
    def __init__(self, parent, current_hotkeys, save_callback):
        self.top = tk.Toplevel(parent)
        self.top.title("Настройка Горячих Клавиш")
        self.top.grab_set()  # Сделать окно модальным

        self.save_callback = save_callback
        self.hotkeys = current_hotkeys.copy()

        # Заголовок
        header = ttkb.Label(
            self.top,
            text="Настройка Горячих Клавиш",
            font=("TkDefaultFont", 14, "bold"),
        )
        header.pack(pady=10)

        # Фрейм для настроек
        settings_frame = ttkb.Frame(self.top, padding="10")
        settings_frame.pack(fill=tk.BOTH, expand=True)

        # Список действий и их текущих горячих клавиш
        self.entries = {}
        for action, key in self.hotkeys.items():
            row = ttkb.Frame(settings_frame)
            row.pack(fill=tk.X, pady=5)

            label = ttkb.Label(
                row,
                text=f"{self.get_action_display_name(action)}:",
                width=20,
                anchor=tk.W,
            )
            label.pack(side=tk.LEFT)

            entry = ttkb.Entry(row)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
            entry.insert(0, key)
            self.entries[action] = entry

        # Кнопки "Сохранить" и "Отмена"
        buttons_frame = ttkb.Frame(self.top, padding="10")
        buttons_frame.pack(fill=tk.X)

        save_button = ttkb.Button(buttons_frame, text="Сохранить", command=self.save)
        save_button.pack(side=tk.RIGHT, padx=5)

        cancel_button = ttkb.Button(
            buttons_frame, text="Отмена", command=self.top.destroy
        )
        cancel_button.pack(side=tk.RIGHT, padx=5)

        # Центрирование окна
        center_window(self.top, parent)

    def get_action_display_name(self, action):
        """Преобразование внутреннего названия действия в более читаемое."""
        names = {
            "quit": "Выход",
            "add_script": "Добавить Скрипт",
            "run_script": "Запустить Скрипт",
            "delete_script": "Удалить Скрипт",
        }
        return names.get(action, action)

    def save(self):
        """Сохранение настроек горячих клавиш."""
        new_hotkeys = {}
        for action, entry in self.entries.items():
            key = entry.get().strip()
            if not key:
                messagebox.showerror(
                    "Ошибка",
                    f"Горячая клавиша для действия '{self.get_action_display_name(action)}' не может быть пустой.",
                )
                return
            new_hotkeys[action] = key

        # Проверка на уникальность горячих клавиш
        keys = list(new_hotkeys.values())
        if len(keys) != len(set(keys)):
            messagebox.showerror("Ошибка", "Горячие клавиши должны быть уникальными.")
            return

        self.save_callback(new_hotkeys)
        self.top.destroy()
