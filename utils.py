# utils.py

import tkinter as tk


def center_window(window: tk.Toplevel, parent: tk.Tk = None):
    """
    Центрирует указанное окно относительно родительского окна.
    Если родительское окно не указано, центрирует относительно экрана.
    """
    window.update_idletasks()  # Обновить информацию о размерах окна

    if parent is None:
        parent = window.master

    # Получение геометрии родительского окна
    parent_x = parent.winfo_rootx()
    parent_y = parent.winfo_rooty()
    parent_width = parent.winfo_width()
    parent_height = parent.winfo_height()

    # Получение размеров диалогового окна
    window_width = window.winfo_width()
    window_height = window.winfo_height()

    # Если размеры еще не определены, установить временные значения
    if window_width == 1 and window_height == 1:
        window.update()
        window_width = window.winfo_width()
        window_height = window.winfo_height()

    # Вычисление координат для центрирования
    x = parent_x + (parent_width // 2) - (window_width // 2)
    y = parent_y + (parent_height // 2) - (window_height // 2)

    window.geometry(f"+{x}+{y}")
