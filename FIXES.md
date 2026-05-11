# Исправления

## 2026-05-10: Исправление имени объекта "Запрос"

### Проблема
В `test_connection.bat` использовалось латинское транслитерированное имя `"Zapros"` вместо правильного русского имени `"Запрос"`.

Ошибка:
```
[WARNING] Error creating Query object: Неудачная попытка создания объекта (Zapros)
```

### Причина
1С 7.7 COM API требует использования оригинальных русских имен объектов, а не их транслитераций.

### Решение
Изменено в `test_connection.bat` строка 84:
```batch
# Было:
echo             query = app.CreateObject("Zapros") >> test_connection.py

# Стало:
echo             query = app.CreateObject("Запрос") >> test_connection.py
```

### Проверка
Все остальные файлы уже используют правильные русские имена:
- `backend/ole_1c77/utils.py:133` - `v7.CreateObject("Запрос")`
- `backend/ole_1c77/documents.py` - использует русские имена для всех атрибутов

### Справка
Правильные имена объектов 1С 7.7 (из `v77_connector.py`):
- `"Запрос"` - объект запроса
- `"Документ.ПриходныйКассовыйОрдер"` - документ
- `"Справочник.Контрагенты"` - справочник

## Предыдущие исправления

### 2026-05-10: Удаление BOM и спецсимволов из BAT файлов
- Удалены UTF-8 BOM метки
- Удалены эмодзи и специальные символы
- Причина: Windows Server 2016 не распознавал файлы

### 2026-05-10: Исправление TemplateResponse API
- Изменен вызов с `templates.TemplateResponse("index.html", {"request": request})`
- На `templates.TemplateResponse(request=request, name="index.html")`
- Причина: изменения в API Starlette
