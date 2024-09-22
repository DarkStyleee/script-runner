# main.py

import os
import re
import shlex
import threading
import subprocess
import ast
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from tkinterdnd2 import DND_FILES, TkinterDnD

from config import ConfigManager
from dialogs import HotkeysDialog, OutputSettingsDialog
from constants import ANSI_COLOR_MAP, DEFAULT_HOTKEYS


class ScriptRunnerGUI:
    ANSI_ESCAPE_PATTERN = re.compile(r"\x1b\[(?:\d+;?)*m")

    def __init__(self, master):
        self.master = master
        self.master.title("Python Script Runner")

        # Инициализация менеджера конфигурации
        self.config_manager = ConfigManager()
        self.config = self.config_manager.config

        # Установка темы и стилей
        theme = self.config.get("theme", "darkly")
        self.style = ttkb.Style(theme)
        self.setup_styles()

        # Установка размера окна
        self.set_window_size()
        self.master.resizable(True, True)

        # Создание интерфейса
        self.create_widgets()

        # Привязка событий и горячих клавиш
        self.bind_mousewheel(self.listbox)
        self.bind_mousewheel(self.output_text)
        self.bind_mousewheel(self.documentation_text)
        self.bind_fixed_hotkeys()

        # Создание тегов для ANSI цветов, если цветной вывод включен
        if self.config.get("colored_output", True):
            self.create_ansi_tags()

        # Обработка события закрытия окна
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_styles(self):
        """Настройка пользовательских стилей."""
        # Стиль для заголовка
        self.style.configure("Header.TLabel", font=("TkDefaultFont", 24, "bold"))
        # Стиль для кнопок
        self.style.configure("Custom.TButton", font=("TkDefaultFont", 10))
        # Стиль для меток
        self.style.configure("Custom.TLabel", font=("TkDefaultFont", 12))
        # Стиль для строки состояния
        self.style.configure("Status.TLabel", font=("TkDefaultFont", 10))

    def create_widgets(self):
        """Создание виджетов интерфейса."""
        # Заголовок приложения
        header = ttkb.Label(
            self.master, text="Python Script Runner", style="Header.TLabel"
        )
        header.pack(pady=10)

        # Меню приложения
        self.create_menu()

        # Основной фрейм
        main_frame = ttkb.Frame(self.master, padding="10")
        main_frame.pack(fill=BOTH, expand=True)

        # Фрейм для кнопок
        button_frame = ttkb.Frame(main_frame)
        button_frame.pack(fill=X, pady=5)

        # Кнопки управления скриптами
        self.add_button = ttkb.Button(
            button_frame,
            text="Добавить скрипт",
            command=self.add_script,
            bootstyle=PRIMARY,
            style="Custom.TButton",
        )
        self.add_button.pack(side=LEFT, padx=5, pady=5)

        self.run_button = ttkb.Button(
            button_frame,
            text="Запустить скрипт",
            command=self.run_script,
            bootstyle=SUCCESS,
            style="Custom.TButton",
        )
        self.run_button.pack(side=LEFT, padx=5, pady=5)

        self.delete_button = ttkb.Button(
            button_frame,
            text="Удалить скрипт",
            command=self.remove_script,
            bootstyle=DANGER,
            style="Custom.TButton",
        )
        self.delete_button.pack(side=LEFT, padx=5, pady=5)

        # Разделитель
        separator = ttkb.Separator(main_frame, orient="horizontal")
        separator.pack(fill=X, pady=10)

        # Фрейм для списка скриптов и вывода
        content_frame = ttkb.Frame(main_frame)
        content_frame.pack(fill=BOTH, expand=True)

        # Левая часть: список скриптов
        left_content_frame = ttkb.Frame(content_frame)
        left_content_frame.pack(side=LEFT, fill=Y, padx=(0, 10))

        scripts_label = ttkb.Label(
            left_content_frame, text="Добавленные скрипты:", style="Custom.TLabel"
        )
        scripts_label.pack(anchor=W, pady=(0, 5))

        self.scripts = self.config.get("scripts", [])

        # Список скриптов
        self.listbox = tk.Listbox(
            left_content_frame,
            width=40,
            height=20,
            selectmode=SINGLE,
            exportselection=False,
        )
        self.listbox.pack(side=LEFT, fill=Y, expand=True)
        self.listbox.bind("<<ListboxSelect>>", self.display_documentation)

        # Скроллбар для списка скриптов
        listbox_scrollbar = ttkb.Scrollbar(
            left_content_frame,
            orient=VERTICAL,
            command=self.listbox.yview,
            bootstyle="primary-round",
        )
        listbox_scrollbar.pack(side=RIGHT, fill=Y)
        self.listbox.config(yscrollcommand=listbox_scrollbar.set)

        # Настройка Drag & Drop для listbox
        self.listbox.drop_target_register(DND_FILES)
        self.listbox.dnd_bind("<<Drop>>", self.drop_scripts)

        # Правая часть: вывод и документация
        right_content_frame = ttkb.Frame(content_frame)
        right_content_frame.pack(side=RIGHT, fill=BOTH, expand=True)

        # Фрейм вывода скрипта
        output_frame = ttkb.Labelframe(
            right_content_frame, text="Вывод скрипта", padding="10"
        )
        output_frame.pack(fill=BOTH, expand=True, pady=(0, 10))

        self.output_text = tk.Text(
            output_frame,
            state="disabled",
            wrap=WORD,
            bg=self.style.lookup("TFrame", "background"),
            fg=self.style.lookup("TLabel", "foreground"),
            bd=0,
            highlightthickness=0,
        )
        self.output_text.pack(side=LEFT, fill=BOTH, expand=True)

        # Скроллбар для вывода
        output_scrollbar = ttkb.Scrollbar(
            output_frame,
            orient=VERTICAL,
            command=self.output_text.yview,
            bootstyle="primary-round",
        )
        output_scrollbar.pack(side=RIGHT, fill=Y)
        self.output_text.config(yscrollcommand=output_scrollbar.set)

        # Фрейм документации
        documentation_frame = ttkb.Labelframe(
            right_content_frame, text="Документация", padding="10"
        )
        documentation_frame.pack(fill=BOTH, expand=True)

        self.documentation_text = tk.Text(
            documentation_frame,
            state="disabled",
            wrap=WORD,
            bg=self.style.lookup("TFrame", "background"),
            fg=self.style.lookup("TLabel", "foreground"),
            bd=0,
            highlightthickness=0,
        )
        self.documentation_text.pack(side=LEFT, fill=BOTH, expand=True)

        # Скроллбар для документации
        documentation_scrollbar = ttkb.Scrollbar(
            documentation_frame,
            orient=VERTICAL,
            command=self.documentation_text.yview,
            bootstyle="primary-round",
        )
        documentation_scrollbar.pack(side=RIGHT, fill=Y)
        self.documentation_text.config(yscrollcommand=documentation_scrollbar.set)

        # Строка состояния
        self.status = ttkb.Label(
            self.master,
            text="Готово",
            anchor=W,
            bootstyle="inverse-dark",
            style="Status.TLabel",
        )
        self.status.pack(side=BOTTOM, fill=X)

        # Заполнение списка скриптов
        self.populate_listbox()

    def create_menu(self):
        """Создание меню приложения."""
        self.menubar = ttkb.Menu(self.master)
        self.master.config(menu=self.menubar)

        # Меню "Файл"
        file_menu = ttkb.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(
            label="Выход", command=self.master.quit, accelerator="Ctrl+Q"
        )

        # Меню "Темы"
        themes_menu = ttkb.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Темы", menu=themes_menu)
        for theme in self.style.theme_names():
            themes_menu.add_command(
                label=theme.capitalize(), command=lambda t=theme: self.change_theme(t)
            )

        # Меню "Настройки"
        settings_menu = ttkb.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Настройки", menu=settings_menu)
        settings_menu.add_command(
            label="Настроить Горячие Клавиши", command=self.open_hotkeys_dialog
        )
        settings_menu.add_command(
            label="Настройки Вывода Логов", command=self.open_output_settings_dialog
        )

        # Меню "Помощь"
        help_menu = ttkb.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Помощь", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.show_about)

    def populate_listbox(self):
        """Заполнение списка скриптов из конфигурации."""
        self.listbox.delete(0, tk.END)
        valid_scripts = []
        for script_path in self.scripts[:]:
            if os.path.isfile(script_path) and script_path.endswith(".py"):
                script_name = os.path.basename(script_path)
                display_name = (
                    (script_name[:97] + "...")
                    if len(script_name) > 100
                    else script_name
                )
                self.listbox.insert(tk.END, display_name)
                valid_scripts.append(script_path)
            else:
                messagebox.showwarning(
                    "Предупреждение",
                    f"Скрипт '{script_path}' не найден или имеет неподдерживаемый формат.",
                )
                self.scripts.remove(script_path)
        self.config_manager.update("scripts", self.scripts)

        if valid_scripts:
            self.status.config(text=f"Загружено {len(valid_scripts)} скриптов.")
        else:
            self.status.config(text="Нет добавленных скриптов.")

    def bind_fixed_hotkeys(self):
        """Привязка фиксированных горячих клавиш на основе конфигурации."""
        hotkeys = self.config.get("hotkeys", DEFAULT_HOTKEYS)
        # Отключение предыдущих привязок
        for action in DEFAULT_HOTKEYS.keys():
            self.master.unbind_all(f"<{hotkeys.get(action, DEFAULT_HOTKEYS[action])}>")

        # Привязка новых горячих клавиш
        self.master.bind_all(
            f"<{hotkeys.get('quit', 'Control-q')}>", lambda e: self.master.quit()
        )
        self.master.bind_all(
            f"<{hotkeys.get('add_script', 'Control-a')}>", lambda e: self.add_script()
        )
        self.master.bind_all(
            f"<{hotkeys.get('run_script', 'Control-r')}>", lambda e: self.run_script()
        )
        self.master.bind_all(
            f"<{hotkeys.get('delete_script', 'Delete')}>",
            lambda e: self.remove_script(),
        )

    def change_theme(self, theme):
        """Изменение темы приложения и сохранение выбора в конфигурационном файле."""
        self.style.theme_use(theme)
        self.status.config(text=f"Тема изменена на: {theme.capitalize()}")
        self.config_manager.update("theme", theme)

    def show_about(self):
        """Показать информацию о программе."""
        messagebox.showinfo(
            "О программе",
            "Python Script Runner\nСоздано с использованием ttkbootstrap.\n© 2024",
        )

    def add_script(self):
        """Добавление скриптов через диалоговое окно."""
        file_paths = filedialog.askopenfilenames(
            title="Выберите скрипты",
            filetypes=[("Python files", "*.py")],
            initialdir=os.getcwd(),
        )
        self._add_scripts(file_paths)

    def drop_scripts(self, event):
        """Добавление скриптов через Drag & Drop."""
        file_paths = self.master.tk.splitlist(event.data)
        self._add_scripts(file_paths)

    def _add_scripts(self, file_paths):
        """Внутренняя функция для добавления скриптов."""
        added = False
        for path in file_paths:
            path = path.strip("{}")
            if (
                path not in self.scripts
                and path.endswith(".py")
                and os.path.isfile(path)
            ):
                self.scripts.append(path)
                script_name = os.path.basename(path)
                display_name = (
                    (script_name[:97] + "...")
                    if len(script_name) > 100
                    else script_name
                )
                self.listbox.insert(tk.END, display_name)
                self.status.config(text=f"Добавлен скрипт: {display_name}")
                added = True
            else:
                messagebox.showwarning(
                    "Неподдерживаемый формат",
                    f"Файл '{os.path.basename(path)}' не является Python-скриптом или уже добавлен.",
                )
        if not added and file_paths:
            self.status.config(
                text="Все выбранные скрипты уже добавлены или имеют неподдерживаемый формат."
            )
        self.config_manager.update("scripts", self.scripts)

    def remove_script(self):
        """Удаление выбранного скрипта."""
        selected_indices = self.listbox.curselection()
        if not selected_indices:
            messagebox.showwarning(
                "Предупреждение", "Пожалуйста, выберите скрипт для удаления."
            )
            return
        index = selected_indices[0]
        script_name = os.path.basename(self.scripts[index])
        confirm = messagebox.askyesno(
            "Подтверждение", f"Вы действительно хотите удалить скрипт '{script_name}'?"
        )
        if confirm:
            self.listbox.delete(index)
            del self.scripts[index]
            self.status.config(text=f"Удален скрипт: {script_name}")
            self.clear_documentation()
            self.config_manager.update("scripts", self.scripts)

    def run_script(self):
        """Запуск выбранного скрипта."""
        selected_indices = self.listbox.curselection()
        if not selected_indices:
            messagebox.showwarning(
                "Предупреждение", "Пожалуйста, выберите скрипт для запуска."
            )
            return
        index = selected_indices[0]
        script_path = self.scripts[index]
        script_name = os.path.basename(script_path)

        # Запрос аргументов для скрипта
        args = simpledialog.askstring(
            "Аргументы",
            "Введите аргументы для скрипта (используйте кавычки для аргументов с пробелами):",
            parent=self.master,
        )
        if args is None:
            self.status.config(text="Запуск скрипта отменен.")
            return

        # Разбор аргументов
        try:
            posix = os.name != "nt"
            parsed_args = shlex.split(args, posix=posix)
        except ValueError as ve:
            messagebox.showerror(
                "Ошибка разбора аргументов",
                f"Не удалось разобрать аргументы: {ve}",
            )
            self.status.config(text="Ошибка разбора аргументов.")
            return

        command = ["python", script_path] + parsed_args

        self.output_text.config(state="normal")
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, f"Запуск скрипта: {' '.join(command)}\n\n")
        self.output_text.config(state="disabled")

        self.status.config(text=f"Запуск скрипта: {script_name}")

        # Запуск скрипта в отдельном потоке
        thread = threading.Thread(target=self.execute_script, args=(command,))
        thread.start()

    def execute_script(self, command):
        """Выполнение скрипта и захват вывода."""
        try:
            process = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            stdout, stderr = process.communicate()
            combined_output = stdout + stderr
            self.master.after(0, self.update_output, combined_output)
        except Exception as e:
            self.master.after(0, self.update_output, f"Ошибка при запуске скрипта: {e}")

    def update_output(self, output):
        """Обновление вывода скрипта."""
        self.output_text.config(state="normal")
        if self.config.get("colored_output", True):
            self.insert_colored_text(output)
        else:
            clean_output = self.ANSI_ESCAPE_PATTERN.sub("", output)
            self.output_text.insert(tk.END, clean_output)
        self.output_text.config(state="disabled")
        self.status.config(text="Готово")

    def insert_colored_text(self, text):
        """Вставка текста с цветами на основе ANSI escape последовательностей."""
        current_color = None
        last_end = 0

        for match in self.ANSI_ESCAPE_PATTERN.finditer(text):
            start, end = match.span()
            if start > last_end:
                segment = text[last_end:start]
                if current_color:
                    self.output_text.insert(tk.END, segment, current_color)
                else:
                    self.output_text.insert(tk.END, segment)
            ansi_codes = match.group()[2:-1].split(";")
            for code in ansi_codes:
                if code == "0":
                    current_color = None
                elif code in ANSI_COLOR_MAP:
                    color = ANSI_COLOR_MAP[code]
                    if color not in self.output_text.tag_names():
                        try:
                            self.output_text.tag_configure(color, foreground=color)
                        except tk.TclError:
                            continue
                    current_color = color
            last_end = end

        # Вставка оставшегося текста
        if last_end < len(text):
            segment = text[last_end:]
            if current_color:
                self.output_text.insert(tk.END, segment, current_color)
            else:
                self.output_text.insert(tk.END, segment)

    def display_documentation(self, event):
        """Отображение документации выбранного скрипта."""
        selected_indices = self.listbox.curselection()
        if not selected_indices:
            self.clear_documentation()
            return
        index = selected_indices[0]
        script_path = self.scripts[index]
        doc = self.get_script_docstring(script_path)
        self.documentation_text.config(state="normal")
        self.documentation_text.delete(1.0, tk.END)
        if doc:
            self.documentation_text.insert(tk.END, doc)
        else:
            self.documentation_text.insert(tk.END, "Документация не найдена.")
        self.documentation_text.config(state="disabled")
        script_name = os.path.basename(script_path)
        self.status.config(text=f"Отображение документации для: {script_name}")

    def get_script_docstring(self, script_path):
        """Извлечение docstring из скрипта."""
        try:
            with open(script_path, "r", encoding="utf-8") as f:
                node = ast.parse(f.read())
                return ast.get_docstring(node)
        except Exception as e:
            print(f"Ошибка при чтении документации из {script_path}: {e}")
            return None

    def clear_documentation(self):
        """Очистка области документации."""
        self.documentation_text.config(state="normal")
        self.documentation_text.delete(1.0, tk.END)
        self.documentation_text.config(state="disabled")

    def set_window_size(self):
        """Установка размера окна из конфигурации."""
        window_size = self.config.get("window_size", "1200x900")
        self.master.geometry(window_size)

    def on_closing(self):
        """Обработка события закрытия окна."""
        window_size = self.master.geometry()
        self.config_manager.update("window_size", window_size)
        self.master.destroy()

    def bind_mousewheel(self, widget):
        """Привязка прокрутки колесом мыши к виджету."""
        widget.bind(
            "<MouseWheel>",
            lambda event: widget.yview_scroll(int(-1 * (event.delta / 120)), "units"),
        )
        widget.bind("<Button-4>", lambda event: widget.yview_scroll(-1, "units"))
        widget.bind("<Button-5>", lambda event: widget.yview_scroll(1, "units"))

    def open_hotkeys_dialog(self):
        """Открытие диалога настройки горячих клавиш."""
        HotkeysDialog(
            self.master,
            self.config.get("hotkeys", DEFAULT_HOTKEYS),
            self.update_hotkeys,
        )

    def open_output_settings_dialog(self):
        """Открытие диалога настройки вывода логов."""
        OutputSettingsDialog(
            self.master,
            self.config.get("colored_output", True),
            self.update_output_settings,
        )

    def update_hotkeys(self, new_hotkeys):
        """Обновление горячих клавиш и сохранение конфигурации."""
        self.config_manager.update("hotkeys", new_hotkeys)
        self.bind_fixed_hotkeys()
        self.status.config(text="Горячие клавиши обновлены.")

    def update_output_settings(self, new_colored_output):
        """Обновление настроек вывода логов и сохранение конфигурации."""
        self.config_manager.update("colored_output", new_colored_output)
        if new_colored_output:
            self.create_ansi_tags()
        else:
            for tag in ANSI_COLOR_MAP.values():
                if tag in self.output_text.tag_names():
                    self.output_text.tag_delete(tag)
        self.status.config(text="Настройки вывода логов обновлены.")

    def create_ansi_tags(self):
        """Создание тегов для ANSI цветов в текстовом поле вывода."""
        for code, color in ANSI_COLOR_MAP.items():
            if color not in self.output_text.tag_names():
                try:
                    self.output_text.tag_configure(color, foreground=color)
                except tk.TclError:
                    continue


def main():
    root = TkinterDnD.Tk()
    app = ScriptRunnerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
