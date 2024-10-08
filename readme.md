# Python Script Runner

**Python Script Runner** — это удобное графическое приложение для запуска скриптов на `tkinter` и `ttkbootstrap`.

## Содержание

- [Особенности](#особенности)
- [Установка](#установка)
- [Использование](#использование)
  - [Добавление Скриптов](#добавление-скриптов)
  - [Запуск Скриптов](#запуск-скриптов)
  - [Удаление Скриптов](#удаление-скриптов)
  - [Просмотр Документации](#просмотр-документации)
- [Конфигурация](#конфигурация)
  - [Файл Конфигурации (`config.json`)](#файл-конфигурации-configjson)
  - [Горячие Клавиши](#горячие-клавиши)
- [Настройка](#настройка)
  - [Темы](#темы)
- [Зависимости](#зависимости)
- [Устранение Проблем](#устранение-проблем)

## Особенности

- **Управление Скриптами:** Лёгкое добавление, запуск и удаление Python-скриптов через понятный интерфейс.
- **Настраиваемые Горячие Клавиши:** Настройка горячих клавиш для быстрого доступа к общим действиям, таким как добавление, запуск или удаление скриптов.
- **Поддержка Тем:** Выбор из множества тем для персонализации внешнего вида приложения.
- **Постоянная Конфигурация:** Все настройки, включая темы, пути к скриптам, размер окна и горячие клавиши, сохраняются в файле `config.json`.
- **Отображение Документации:** Автоматически извлекает и отображает docstring из ваших скриптов для быстрого ознакомления.
- **Изменяемый Размер Окна:** Регулировка размера окна приложения по вашему предпочтению.

## Установка

`python -m venv venv`

`source venv/bin/activate`

На Windows: `venv\Scripts\activate`

---

### Установка Зависимостей:

Убедитесь, что у вас установлена версия **Python 3.6** или выше. Затем установите необходимые пакеты Python:

`pip install -r requirements.txt`

Если файл **requirements.txt** не предоставлен, установите зависимости вручную:

`pip install ttkbootstrap tkinterdnd2`

На Linux: `sudo apt-get install python3.11-tk`

## Использование

### Запуск Приложения

Запустите основной скрипт для запуска приложения:

`python main.py`

---

### Добавление Скриптов

Есть несколько способов добавить скрипты в приложение:

- **Кнопка "Добавить Скрипт":**

  Нажмите на кнопку "Добавить скрипт".
  Откроется диалоговое окно. Перейдите к желаемому Python-скрипту (\*.py) и выберите его.
  Скрипт будет добавлен в список.

- **Drag and Drop:**

  Просто перетащите один или несколько файлов Python-скриптов и отпустите их в область списка скриптов слева.
  Скрипты будут добавлены автоматически.

---

### Запуск Скриптов

Чтобы выполнить скрипт:

1. Выберите желаемый скрипт из списка, кликнув по нему.
2. Нажмите на кнопку "Запустить скрипт" или используйте настроенную горячую клавишу.
3. Появится окно ввода для аргументов командной строки. Введите их, разделяя пробелами, или оставьте поле пустым, если аргументы не требуются.
4. Скрипт запустится в отдельном потоке, и его вывод будет отображён в разделе "Вывод скрипта".

---

### Удаление Скриптов

Чтобы удалить скрипт из списка:

1. Выберите скрипт, который вы хотите удалить, из списка.
2. Нажмите на кнопку "Удалить скрипт" или используйте настроенную горячую клавишу.
3. Подтвердите удаление, когда будет предложено.

---

### Просмотр Документации

Приложение автоматически извлекает и отображает docstring выбранного скрипта:

1. Выберите скрипт из списка.
2. Раздел "Документация" справа отобразит docstring скрипта, если он доступен.

## Конфигурация

Все настройки хранятся в файле config.json, расположенном в корневой директории приложения.
Этот файл управляет темами, путями к скриптам, размером окна и горячими клавишами.

### Файл Конфигурации (config.json)

Ниже приведена примерная структура файла config.json:

```
{
    "theme": "darkly",
    "scripts": [
    "C:/Path/To/Your/Script1.py",
    "C:/Path/To/Your/Script2.py"
    ],
    "window*size": "800x600+100+100",
    "hotkeys": {
        "quit": "Control-q",
        "add_script": "Control-w",
        "run_script": "Control-e",
        "delete_script": "Control-d"
    }
}
```

- **theme:** Текущая тема приложения. Можно изменить на любую из доступных тем ttkbootstrap.

- **scripts:** Список абсолютных путей к добавленным Python-скриптам.

- **window_size:** Размер и положение окна в формате "ширинаxвысота+отступ\*слева+отступ_сверху". Например, "800x600+100+100" означает ширину 800 пикселей, высоту 600 пикселей и позицию окна 100 пикселей от левого края и 100 пикселей от верхнего края экрана.

- **hotkeys:** Сочетания клавиш для различных действий.

---

### Горячие Клавиши

Горячие клавиши позволяют выполнять действия быстро без использования мыши. Их можно настроить через графический интерфейс приложения или вручную, редактируя файл **config.json**.

Настройка Горячих Клавиш через GUI
Перейдите в меню **"Настройки" -> "Настроить Горячие Клавиши"**.
В появившемся окне измените желаемые горячие клавиши.
Нажмите **"Сохранить"**, чтобы применить изменения. Они автоматически сохранятся в **config.json**.

---

### Настройка Горячих Клавиш Вручную

Откройте **config.json** в любом текстовом редакторе.

Найдите раздел **"hotkeys"** и измените сочетания клавиш по своему усмотрению.

Сохраните изменения и перезапустите приложение, чтобы применить новые горячие клавиши.

**Важно**: Убедитесь, что все горячие клавиши уникальны и не конфликтуют друг с другом или с системными сочетаниями клавиш.

## Настройка

### Темы

Приложение поддерживает различные темы, предоставляемые **ttkbootstrap**. Чтобы изменить тему:

- Перейдите в меню "Темы".
- Выберите желаемую тему из списка.
- Внешний вид приложения обновится немедленно.
- Выбранная тема сохраняется в config.json и будет сохраняться при следующих запусках приложения.

## Зависимости

Убедитесь, что у вас установлены следующие Python-пакеты:

**ttkbootstrap** – Улучшенные возможности темизации для tkinter.

**tkinterdnd2** – Поддержка drag and drop в tkinter.

## Устранение Проблем

### Распространённые Проблемы

`AttributeError: 'ScriptRunnerGUI' object has no attribute 'style'`

**Причина:** Метод save_config() был вызван до инициализации self.style.

**Решение:** Убедитесь, что self.style инициализирован до любого вызова метода сохранения конфигурации. Обновлённый код, предоставленный ранее, решает эту проблему путем изменения порядка инициализации в методе load_config().

`Скрипты Не Отображаются Корректно`

**Причина:** Скрипты могли быть перемещены или удалены из исходных путей.

**Решение:** Удалите недействительные записи скриптов из списка или обновите пути через интерфейс приложения.

`Горячие клавиши не работают`

**Причина:** Горячие клавиши могут конфликтовать с системными сочетаниями клавиш или быть некорректно настроены.

**Решение:** Убедитесь, что все горячие клавиши уникальны и не конфликтуют с существующими системными сочетаниями клавиш. Перенастройте горячие клавиши через меню "Настройки" -> "Настроить Горячие Клавиши".
