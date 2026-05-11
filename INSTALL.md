# Инструкция по запуску 77-8DOC

## Что готово

✅ Структура проекта создана
✅ Backend модули для работы с 1С 7.7 через COM
✅ FastAPI приложение с API endpoints
✅ Веб-интерфейс с Bootstrap 5 и Alpine.js
✅ Поддержка документов:
  - Реализация товаров и услуг
  - Счет-фактура выданный

## Установка и запуск

### 1. Установите зависимости

```bash
cd E:\WORK_RUCHEEK\1c77\77-8DOC
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Настройте конфигурацию

Скопируйте `.env.example` в `.env`:
```bash
copy .env.example .env
```

Отредактируйте `.env` и укажите путь к вашей базе 1С 7.7:
```ini
DB_PATH_77=E:\WORK_RUCHEEK\1c77\Base77
DB_USER_77=Admin
DB_PASSWORD_77=
```

### 3. Запустите сервер

```bash
python -m uvicorn backend.main:app --reload
```

Или напрямую:
```bash
python backend/main.py
```

### 4. Откройте браузер

Перейдите по адресу: http://localhost:8000

## Использование

1. Выберите период (дата начала и конца)
2. Выберите тип документа (Реализация или Счет-фактура)
3. Нажмите "Загрузить"
4. Просмотрите документы в таблице
5. Кликните на кнопку "глаз" для просмотра табличной части

## API Endpoints

- `GET /` - Главная страница
- `GET /api/v1/health` - Health check
- `POST /api/v1/realizations` - Получить документы Реализация
- `POST /api/v1/invoices` - Получить счета-фактуры

### Пример запроса

```bash
curl -X POST http://localhost:8000/api/v1/realizations \
  -H "Content-Type: application/json" \
  -d '{"start_date": "01.05.2026", "end_date": "10.05.2026"}'
```

## Логи

Все логи сохраняются в `logs/app.log`

## Следующие шаги (Фаза 2)

Для интеграции с 1С 8 через OData:
1. Изучите ваш проект Web1C (D:\Work\Web1C)
2. Адаптируйте OneCClient для работы с документами
3. Создайте модуль `backend/odata_1c8/`
4. Добавьте endpoints `/api/v1/8/realizations` и `/api/v1/8/invoices`
5. Добавьте сравнение данных между 7.7 и 8

## Возможные проблемы

### COM не найден
Убедитесь, что 1С 7.7 зарегистрирована:
```bash
"C:\Program Files\1Cv77\BIN\1cv7s.exe" /REGSERVER
```

### Ошибка подключения к базе
Проверьте:
- Путь к базе в `.env`
- Права доступа к сетевой папке
- Логин и пароль пользователя

### Порт 8000 занят
Измените порт в `.env`:
```ini
PORT=8001
```

## Структура проекта

```
77-8DOC/
├── backend/
│   ├── main.py              # FastAPI приложение
│   ├── config.py            # Конфигурация
│   ├── models.py            # Pydantic модели
│   ├── ole_1c77/            # Модуль работы с 1С 7.7
│   │   ├── connection.py    # Подключение
│   │   ├── documents.py     # Работа с документами
│   │   └── utils.py         # Утилиты
│   └── api/v1/              # API endpoints
├── frontend/
│   ├── templates/
│   │   └── index.html       # Главная страница
│   └── static/
│       ├── js/app.js        # Alpine.js логика
│       └── css/style.css    # Стили
└── logs/                    # Логи
```

## Контакты

При возникновении вопросов обращайтесь к документации или логам приложения.
