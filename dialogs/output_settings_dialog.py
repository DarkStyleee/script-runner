# dialogs/output_settings_dialog.py

import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from utils import center_window


class OutputSettingsDialog:
    def __init__(self, parent, colored_output, save_callback):
        self.top = tk.Toplevel(parent)
        self.top.title("Настройки Вывода Логов")
        self.top.grab_set()  # Сделать окно модальным

        self.save_callback = save_callback
        self.colored_output = colored_output

        # Заголовок
        header = ttkb.Label(
            self.top,
            text="Настройки Вывода Логов",
            font=("TkDefaultFont", 14, "bold"),
        )
        header.pack(pady=10)

        # Чекбокс для цветного вывода
        self.colored_var = tk.BooleanVar(value=self.colored_output)
        colored_checkbox = ttkb.Checkbutton(
            self.top,
            text="Использовать цветной вывод логов",
            variable=self.colored_var,
        )
        colored_checkbox.pack(pady=5, padx=10)

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

    def save(self):
        """Сохранение настроек вывода логов."""
        new_colored_output = self.colored_var.get()
        self.save_callback(new_colored_output)
        self.top.destroy()
