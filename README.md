# 77-8DOC: Веб-приложение для работы с документами 1С 7.7 и 1С 8

Веб-приложение для выгрузки и просмотра документов из 1С 7.7 (через COM) и 1С 8 (через OData).

## Возможности

### Фаза 1 (текущая): 1С 7.7
- Выгрузка документов "Реализация" за период
- Выгрузка документов "Счет-фактура выданный" за период
- Просмотр шапки и табличной части документов
- Веб-интерфейс с фильтрами по датам

### Фаза 2 (планируется): 1С 8
- Интеграция с 1С 8 через OData
- Сравнение данных между версиями

## Требования

- Windows (для работы с 1С 7.7 через COM)
- Python 3.11+
- Установленная 1С 7.7 с зарегистрированным COM-сервером
- Доступ к базе 1С 7.7

## Установка

1. Клонировать репозиторий
2. Создать виртуальное окружение:
```bash
python -m venv venv
venv\Scripts\activate
```

3. Установить зависимости:
```bash
pip install -r requirements.txt
```

4. Скопировать `.env.example` в `.env` и настроить параметры:
```bash
copy .env.example .env
```

5. Отредактировать `.env`:
```
DB_PATH_77=D:\Path\To\Your\1C77\Database
DB_USER_77=YourUsername
DB_PASSWORD_77=YourPassword
```

## Запуск

```bash
uvicorn backend.main:app --reload
```

Приложение будет доступно по адресу: http://localhost:8100

## Структура проекта

```
77-8DOC/
├── backend/
│   ├── main.py              # FastAPI приложение
│   ├── config.py            # Конфигурация
│   ├── models.py            # Pydantic модели
│   ├── ole_1c77/            # Модуль работы с 1С 7.7
│   │   ├── connection.py    # Подключение к 1С
│   │   ├── documents.py     # Работа с документами
│   │   └── utils.py         # Утилиты
│   └── api/v1/              # API endpoints
│       ├── documents_77.py  # Endpoints для 1С 7.7
│       └── health.py        # Health check
├── frontend/
│   ├── templates/
│   │   └── index.html       # Главная страница
│   └── static/
│       ├── js/app.js        # Alpine.js логика
│       └── css/style.css    # Стили
├── logs/                    # Логи приложения
├── requirements.txt
├── .env.example
└── README.md
```

## API Endpoints

### GET /
Главная страница веб-интерфейса

### GET /api/v1/health
Health check endpoint

### POST /api/v1/realizations
Получить документы "Реализация" за период

**Request body:**
```json
{
  "start_date": "01.05.2026",
  "end_date": "10.05.2026"
}
```

**Response:**
```json
[
  {
    "number": "00000000123",
    "date": "05.05.2026",
    "contractor": "ООО Рога и Копыта",
    "contract": "Основной договор",
    "warehouse": "Основной склад",
    "sum": 125000.50,
    "table_part": [
      {
        "nomenclature": "Товар 1",
        "quantity": 10.0,
        "price": 1000.0,
        "sum": 10000.0
      }
    ]
  }
]
```

### POST /api/v1/invoices
Получить документы "Счет-фактура выданный" за период

Аналогичный формат запроса и ответа.

## Технологии

- **Backend**: FastAPI, Pydantic, pywin32
- **Frontend**: Bootstrap 5, Alpine.js
- **1С 7.7**: COM (V77.Application)

## Разработка

### Логирование
Все логи сохраняются в `logs/app.log`

### Отладка
Запуск с автоперезагрузкой:
```bash
uvicorn backend.main:app --reload --log-level debug
```

## Лицензия

MIT
