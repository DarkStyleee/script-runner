import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox, simpledialog
import subprocess
import threading
import os
import ast
import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
import json
import shlex  # Добавлено для разбора аргументов


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


class ScriptRunnerGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Python Script Runner")

        # Путь к конфигурационному файлу
        self.config_file = "config.json"

        # Загрузка конфигурации и установка темы
        self.load_config()

        # Установка размера окна
        self.set_window_size()

        self.master.resizable(True, True)  # Разрешение изменения размера окна

        # Настройка пользовательских стилей
        self.setup_styles()

        # Заголовок приложения
        header = ttkb.Label(master, text="Python Script Runner", style="Header.TLabel")
        header.pack(pady=10)

        # Меню приложения
        self.create_menu()

        # Основной фрейм
        main_frame = ttkb.Frame(master, padding="10")
        main_frame.pack(fill=ttkb.BOTH, expand=True)

        # Фрейм для кнопок
        button_frame = ttkb.Frame(main_frame)
        button_frame.pack(fill=ttkb.X, pady=5)

        # Кнопка "Добавить скрипт"
        self.add_button = ttkb.Button(
            button_frame,
            text="Добавить скрипт",
            command=self.add_script,
            bootstyle=PRIMARY,
            style="Custom.TButton",
        )
        self.add_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Кнопка "Запустить скрипт"
        self.run_button = ttkb.Button(
            button_frame,
            text="Запустить скрипт",
            command=self.run_script,
            bootstyle=SUCCESS,
            style="Custom.TButton",
        )
        self.run_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Кнопка "Удалить скрипт"
        self.delete_button = ttkb.Button(
            button_frame,
            text="Удалить скрипт",
            command=self.remove_script,
            bootstyle=DANGER,
            style="Custom.TButton",
        )
        self.delete_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Разделитель
        separator = ttkb.Separator(main_frame, orient="horizontal")
        separator.pack(fill=ttkb.X, pady=10)

        # Фрейм для списка скриптов, вывода и документации
        content_frame = ttkb.Frame(main_frame)
        content_frame.pack(fill=ttkb.BOTH, expand=True)

        # Левая сторона: список скриптов и область Drag & Drop
        left_content_frame = ttkb.Frame(content_frame)
        left_content_frame.pack(
            side=tk.LEFT, fill=ttkb.BOTH, expand=False, padx=(0, 10)
        )

        scripts_label = ttkb.Label(
            left_content_frame, text="Добавленные скрипты:", style="Custom.TLabel"
        )
        scripts_label.pack(anchor=tk.W, pady=(0, 5))

        self.scripts = self.config.get("scripts", [])

        # Список скриптов
        self.listbox = tk.Listbox(
            left_content_frame,
            width=40,
            height=20,
            selectmode=tk.SINGLE,
            exportselection=False,  # Предотвращает потерю выбора при переключении фокуса
        )
        self.listbox.pack(side=tk.LEFT, fill=ttkb.BOTH, expand=True)
        self.listbox.bind("<<ListboxSelect>>", self.display_documentation)

        # Добавление вертикального стилизованного скроллбара
        listbox_scrollbar = ttkb.Scrollbar(
            left_content_frame,
            orient=tk.VERTICAL,
            command=self.listbox.yview,
            bootstyle="primary-round",  # Пример стиля, измените по желанию
        )
        listbox_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=listbox_scrollbar.set)

        # Настройка Drag & Drop для listbox
        self.listbox.drop_target_register(DND_FILES)
        self.listbox.dnd_bind("<<Drop>>", self.drop_scripts)

        # Правая сторона: вывод и документация
        right_content_frame = ttkb.Frame(content_frame)
        right_content_frame.pack(side=tk.RIGHT, fill=ttkb.BOTH, expand=True)

        # Текстовое поле для вывода скрипта
        output_frame = ttkb.Labelframe(
            right_content_frame, text="Вывод скрипта", padding="10"
        )
        output_frame.pack(fill=ttkb.BOTH, expand=True, pady=(0, 10))

        # Создаем Frame для Text и Scrollbar
        self.output_text_frame = ttkb.Frame(output_frame)
        self.output_text_frame.pack(fill=ttkb.BOTH, expand=True)

        self.output_text = tk.Text(
            self.output_text_frame,
            state="disabled",
            wrap=tk.WORD,  # Автоматический перенос строк
            bg=self.style.lookup(
                "TFrame", "background"
            ),  # Использование lookup для цвета фона
            fg=self.style.lookup(
                "TLabel", "foreground"
            ),  # Использование lookup для цвета текста
            bd=0,
            highlightthickness=0,
        )
        self.output_text.pack(side=tk.LEFT, fill=ttkb.BOTH, expand=True)

        # Добавляем стилизованный Scrollbar для output_text
        output_scrollbar = ttkb.Scrollbar(
            self.output_text_frame,
            orient=tk.VERTICAL,
            command=self.output_text.yview,
            bootstyle="primary-round",  # Пример стиля, измените по желанию
        )
        output_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text.config(yscrollcommand=output_scrollbar.set)

        # Текстовое поле для документации
        documentation_frame = ttkb.Labelframe(
            right_content_frame, text="Документация", padding="10"
        )
        documentation_frame.pack(fill=ttkb.BOTH, expand=True)

        # Создаем Frame для Text и Scrollbar
        self.documentation_text_frame = ttkb.Frame(documentation_frame)
        self.documentation_text_frame.pack(fill=ttkb.BOTH, expand=True)

        self.documentation_text = tk.Text(
            self.documentation_text_frame,
            state="disabled",
            wrap=tk.WORD,  # Автоматический перенос строк
            bg=self.style.lookup(
                "TFrame", "background"
            ),  # Использование lookup для цвета фона
            fg=self.style.lookup(
                "TLabel", "foreground"
            ),  # Использование lookup для цвета текста
            bd=0,
            highlightthickness=0,
        )
        self.documentation_text.pack(side=tk.LEFT, fill=ttkb.BOTH, expand=True)

        # Добавляем стилизованный Scrollbar для documentation_text
        documentation_scrollbar = ttkb.Scrollbar(
            self.documentation_text_frame,
            orient=tk.VERTICAL,
            command=self.documentation_text.yview,
            bootstyle="primary-round",  # Пример стиля, измените по желанию
        )
        documentation_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.documentation_text.config(yscrollcommand=documentation_scrollbar.set)

        # Строка состояния (Status Bar) — Создаём перед вызовом populate_listbox
        self.status = ttkb.Label(
            master,
            text="Готово",
            anchor=tk.W,
            bootstyle="inverse-dark",
            style="Status.TLabel",
        )
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

        # Заполнение listbox из конфигурации
        self.populate_listbox()

        # Привязка прокрутки через колесо мыши
        self.bind_mousewheel(self.listbox)
        self.bind_mousewheel(self.output_text)
        self.bind_mousewheel(self.documentation_text)

        # Привязка фиксированных горячих клавиш
        self.bind_fixed_hotkeys()

        # Привязка события закрытия окна для сохранения размера и конфигурации
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_styles(self):
        """Настройка пользовательских стилей."""
        # Стиль для заголовка
        self.style.configure("Header.TLabel", font=("TkDefaultFont", 24, "bold"))

        # Стиль для кнопок
        self.style.configure("Custom.TButton", font=("TkDefaultFont", 10))

        # Стиль для обычных меток
        self.style.configure("Custom.TLabel", font=("TkDefaultFont", 12))

        # Стиль для LabelFrame (например, Drag & Drop)
        self.style.configure(
            "Custom.TLabelframe.Label", font=("TkDefaultFont", 10, "bold")
        )

        # Стиль для строки состояния
        self.style.configure("Status.TLabel", font=("TkDefaultFont", 10))

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
        available_themes = self.style.theme_names()
        for theme in available_themes:
            themes_menu.add_command(
                label=theme.capitalize(),
                command=lambda t=theme: self.change_theme(t),
            )

        # Меню "Настройки"
        settings_menu = ttkb.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Настройки", menu=settings_menu)
        settings_menu.add_command(
            label="Настроить Горячие Клавиши", command=self.open_hotkeys_dialog
        )

        # Меню "Помощь"
        help_menu = ttkb.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Помощь", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.show_about)

    def populate_listbox(self):
        """Заполнение списка скриптов из конфигурации."""
        self.listbox.delete(0, tk.END)
        valid_scripts = []
        for script_path in self.scripts[
            :
        ]:  # Используем копию списка для безопасного удаления
            if os.path.isfile(script_path) and script_path.endswith(".py"):
                script_name = os.path.basename(script_path)
                # Ограничение длины имени скрипта до 100 символов для предотвращения переполнения
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
        self.save_config()  # Обновление конфигурации, если были удалены невалидные скрипты

        if valid_scripts:
            self.status.config(text=f"Загружено {len(valid_scripts)} скриптов.")
        else:
            self.status.config(text="Нет добавленных скриптов.")

    def bind_fixed_hotkeys(self):
        """Привязка фиксированных горячих клавиш на основе конфигурации."""
        hotkeys = self.config.get("hotkeys", {})
        # Отключение предыдущих привязок, если они есть
        self.master.unbind_all(f"<{hotkeys.get('quit', 'Control-q')}>")
        self.master.unbind_all(f"<{hotkeys.get('add_script', 'Control-w')}>")
        self.master.unbind_all(f"<{hotkeys.get('run_script', 'Control-e')}>")
        self.master.unbind_all(f"<{hotkeys.get('delete_script', 'Control-d')}>")

        # Привязка горячих клавиш из конфигурации
        quit_key = hotkeys.get("quit", "Control-q")
        add_key = hotkeys.get("add_script", "Control-w")
        run_key = hotkeys.get("run_script", "Control-e")
        delete_key = hotkeys.get("delete_script", "Control-d")

        self.master.bind_all(f"<{quit_key}>", lambda event: self.master.quit())
        self.master.bind_all(f"<{add_key}>", lambda event: self.add_script())
        self.master.bind_all(f"<{run_key}>", lambda event: self.run_script())
        self.master.bind_all(f"<{delete_key}>", lambda event: self.remove_script())

    def change_theme(self, theme):
        """Изменение темы приложения и сохранение выбора в конфигурационном файле."""
        self.style.theme_use(theme)
        self.status.config(text=f"Тема изменена на: {theme.capitalize()}")
        self.save_config()

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
        # event.data может содержать несколько путей, разделенных пробелами
        file_paths = self.master.tk.splitlist(event.data)
        self._add_scripts(file_paths)

    def _add_scripts(self, file_paths):
        """Внутренняя функция для добавления скриптов."""
        added = False
        for path in file_paths:
            path = path.strip("{}")  # Удаление фигурных скобок, если они есть
            if path not in self.scripts and path.endswith(".py"):
                if os.path.isfile(path):
                    self.scripts.append(path)
                    script_name = os.path.basename(path)
                    # Ограничение длины имени скрипта до 100 символов для предотвращения переполнения
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
                        f"Файл '{os.path.basename(path)}' не найден или недоступен.",
                    )
            elif not path.endswith(".py"):
                messagebox.showwarning(
                    "Неподдерживаемый формат",
                    f"Файл '{os.path.basename(path)}' не является Python-скриптом.",
                )
            else:
                messagebox.showinfo(
                    "Информация", f"Скрипт '{os.path.basename(path)}' уже добавлен."
                )
        if not added and file_paths:
            self.status.config(
                text="Все выбранные скрипты уже добавлены или имеют неподдерживаемый формат."
            )
        self.save_config()

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
            self.save_config()

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
            # Пользователь отменил ввод
            self.status.config(text="Запуск скрипта отменен.")
            return

        # Используем shlex.split для корректного разбора аргументов с учетом кавычек
        try:
            # Определение режима разбиения в зависимости от ОС
            posix = not os.name == "nt"
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

        # Запуск скрипта в отдельном потоке, чтобы не блокировать GUI
        thread = threading.Thread(target=self.execute_script, args=(command,))
        thread.start()

    def execute_script(self, command):
        """Выполнение скрипта и захват вывода."""
        try:
            # Запуск скрипта и захват вывода
            process = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            stdout, stderr = process.communicate()

            # Обновление текстового поля в главном потоке
            self.master.after(0, self.update_output, stdout, stderr)
        except Exception as e:
            self.master.after(
                0, self.update_output, "", f"Ошибка при запуске скрипта: {e}"
            )

    def update_output(self, stdout, stderr):
        """Обновление вывода скрипта."""
        self.output_text.config(state="normal")
        if stdout:
            self.output_text.insert(tk.END, "Вывод:\n" + stdout + "\n")
        if stderr:
            self.output_text.insert(tk.END, "Ошибки:\n" + stderr + "\n")
        self.output_text.config(state="disabled")

        self.status.config(text="Готово")

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
                docstring = ast.get_docstring(node)
                return docstring
        except Exception as e:
            print(f"Ошибка при чтении документации из {script_path}: {e}")
            return None

    def clear_documentation(self):
        """Очистка области документации."""
        self.documentation_text.config(state="normal")
        self.documentation_text.delete(1.0, tk.END)
        self.documentation_text.config(state="disabled")

    def save_config(self):
        """Сохранение конфигурации в файл."""
        # Получение текущего размера окна
        window_size = self.master.geometry()

        config = {
            "theme": self.style.theme_use(),
            "scripts": self.scripts,
            "window_size": window_size,
            "hotkeys": self.config.get("hotkeys", {}),
        }
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror(
                "Ошибка сохранения конфигурации",
                f"Не удалось сохранить конфигурацию: {e}",
            )

    def load_config(self):
        """Загрузка конфигурации из файла."""
        default_theme = "darkly"
        default_window_size = "1200x900"
        default_hotkeys = {
            "quit": "Control-q",
            "add_script": "Control-w",
            "run_script": "Control-e",
            "delete_script": "Control-d",
        }
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
                theme = self.config.get("theme", default_theme)
                self.scripts = self.config.get("scripts", [])
                self.window_size = self.config.get("window_size", default_window_size)
                self.hotkeys = self.config.get("hotkeys", default_hotkeys)
            except Exception as e:
                messagebox.showerror(
                    "Ошибка загрузки конфигурации",
                    f"Не удалось загрузить конфигурацию: {e}",
                )
                self.config = {}
                theme = default_theme
                self.scripts = []
                self.window_size = default_window_size
                self.hotkeys = default_hotkeys
        else:
            # Если config.json отсутствует, создать его с настройками по умолчанию
            self.config = {
                "theme": default_theme,
                "scripts": [],
                "window_size": default_window_size,
                "hotkeys": default_hotkeys,
            }
            self.hotkeys = default_hotkeys
            self.scripts = []
            self.window_size = default_window_size
            # Установка темы перед сохранением конфигурации
            self.style = ttkb.Style(default_theme)
            self.save_config()  # Сохранить первоначальную конфигурацию
            return  # Завершить метод, чтобы избежать повторного создания self.style

        # Установка темы
        self.style = ttkb.Style(theme)

    def set_window_size(self):
        """Установка размера окна из конфигурации."""
        self.master.geometry(self.window_size)

    def on_closing(self):
        """Обработка события закрытия окна."""
        # Сохранение текущего размера окна
        self.window_size = self.master.geometry()
        self.save_config()
        self.master.destroy()

    def bind_mousewheel(self, widget):
        """Функция для привязки прокрутки колесом мыши к виджету."""
        # Windows и MacOS
        widget.bind(
            "<MouseWheel>",
            lambda event: widget.yview_scroll(int(-1 * (event.delta / 120)), "units"),
        )
        # Linux
        widget.bind("<Button-4>", lambda event: widget.yview_scroll(-1, "units"))
        widget.bind("<Button-5>", lambda event: widget.yview_scroll(1, "units"))

    def open_hotkeys_dialog(self):
        """Открытие диалога настройки горячих клавиш."""
        HotkeysDialog(self.master, self.hotkeys, self.update_hotkeys)

    def update_hotkeys(self, new_hotkeys):
        """Обновление горячих клавиш и сохранение конфигурации."""
        self.hotkeys = new_hotkeys
        self.config["hotkeys"] = self.hotkeys
        self.bind_fixed_hotkeys()
        self.save_config()
        self.status.config(text="Горячие клавиши обновлены.")


if __name__ == "__main__":
    # Используем TkinterDnD.Tk для поддержки Drag & Drop
    root = TkinterDnD.Tk()
    # Настройка темы до создания приложения
    app = ScriptRunnerGUI(root)
    root.mainloop()
