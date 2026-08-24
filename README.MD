# System Monitor

Приложение для мониторинга состояния системы с графическим интерфейсом на PySide6.

## Возможности

- Мониторинг CPU и RAM
- Использование диска
- Скорость сети
- Ping
- Load Average
- Uptime системы
- Температура CPU и скорость вентиляторов
- Чтение данных из USB-файла
- Запуск и остановка мониторинга через GUI

## Архитектура

Проект разделён на несколько слоёв:

- `domain` — бизнес-модели, Value Objects и интерфейсы
- `infra` — работа с системой и реализация источников данных
- `presentation` — графический интерфейс
- `tests` — unit-тесты

## Установка

### Клонирование репозитория

```bash
git clone <repository-link>
```

### Создание виртуального окружения

```bash
python -m venv venv
```

### Активация

```bash
# Windows
venv\Scripts\activate
# Linux
source venv/bin/activate
```

### Установка зависимостей

```bash
pip install -r requirements.txt
```

## Запуск приложения

```bash
python main.py
```

## Запуск тестов

```bash
pytest -v
```