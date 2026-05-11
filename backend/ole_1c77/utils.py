"""Утилиты для работы с 1С 7.7 через COM (адаптировано из dolg_json.py)."""

from datetime import date, datetime


def safe_getattr(obj, name, default=None):
    """Безопасное получение атрибута COM-объекта."""
    try:
        return getattr(obj, name)
    except Exception:
        return default


def com_invoke_date(obj, prop_name):
    """
    Низкоуровневый COM-вызов для получения даты.
    В PyInstaller-сборке getattr(doc, "ДатаДок") может возвращать пустую строку
    вместо даты. Прямой Invoke с VT_DATE обходит эту проблему.
    """
    if obj is None:
        return None
    try:
        dispid = obj._oleobj_.GetIDsOfNames(prop_name)
        # VT_DATE = 7, диспатч PROPERTYGET = 2
        raw = obj._oleobj_.InvokeTypes(dispid, 0, 2, (7, 0), ())
        return raw
    except Exception:
        return None


def normalize_1c_date(value):
    """Нормализация даты из 1С в datetime объект."""
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        # Приводим aware datetime к naive
        return value.replace(tzinfo=None) if value.tzinfo is not None else value
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day)
    txt = str(value).strip()
    patterns = (
        "%Y-%m-%d %H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%d.%m.%Y %H:%M:%S",
        "%d.%m.%Y %H:%M",
        "%d.%m.%Y",
    )
    for pattern in patterns:
        try:
            dt = datetime.strptime(txt, pattern)
            return dt.replace(tzinfo=None) if dt.tzinfo is not None else dt
        except ValueError:
            continue
    return None


def date_to_ru(value):
    """Форматирование даты в формат дд.мм.гггг."""
    dt = normalize_1c_date(value)
    return dt.strftime("%d.%m.%Y") if dt else None


def to_float(value, default=0.0):
    """Безопасное преобразование значения в float."""
    if value in (None, ""):
        return default
    txt = str(value).strip()
    txt = txt.replace(" ", "").replace(" ", "").replace("'", "")
    if not txt:
        return default

    # Поддержка форматов: 2'300.00, 2 300,00, 2,300.00, 2300
    if "," in txt and "." in txt:
        if txt.rfind(",") > txt.rfind("."):
            # 1.234,56 -> 1234.56
            txt = txt.replace(".", "").replace(",", ".")
        else:
            # 1,234.56 -> 1234.56
            txt = txt.replace(",", "")
    elif "," in txt:
        txt = txt.replace(",", ".")

    try:
        return float(txt)
    except ValueError:
        return default


def to_int(value, default=0):
    """Безопасное преобразование значения в int."""
    if value in (None, ""):
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        try:
            return int(float(str(value).replace(",", ".")))
        except (TypeError, ValueError):
            return default


def convert_1c_value(value):
    """
    Универсальное преобразование значения из 1С в Python-тип.
    Обрабатывает даты, справочники, документы, простые типы.
    """
    if value is None:
        return None
    if isinstance(value, (int, float, bool, str)):
        return value

    # Попытка преобразовать в дату
    dt = normalize_1c_date(value)
    if dt:
        return dt.strftime("%d.%m.%Y")

    # Попытка получить представление объекта через стандартные атрибуты
    for attr_name in ("Наименование", "Код", "НомерДок"):
        attr_val = safe_getattr(value, attr_name)
        if attr_val not in (None, ""):
            return str(attr_val)

    return str(value)


def execute_query(v7, query_text):
    """
    Выполнение запроса 1С 7.7.
    Возвращает (query_object, success).
    """
    query = v7.CreateObject("Запрос")
    # В 1С 7.7 через pywin32 метод может конфликтовать с одноименным свойством
    dispid_execute = query._oleobj_.GetIDsOfNames("Выполнить")
    res = query._oleobj_.InvokeTypes(
        dispid_execute,
        0,
        1,
        (11, 0),   # VT_BOOL
        ((8, 1),), # VT_BSTR input
        query_text,
    )
    return query, bool(res)
