"""Работа с документами 1С 7.7."""

import logging
from typing import Any

from .utils import (
    convert_1c_value,
    date_to_ru,
    safe_getattr,
    to_float,
)

logger = logging.getLogger(__name__)


def get_document_table_part(doc) -> list[dict]:
    """
    Получение табличной части документа.
    Использует doc.ВыбратьСтроки() для перебора строк.
    """
    table_part = []
    try:
        # Вызываем ВыбратьСтроки через низкоуровневый COM API
        dispid_select_rows = doc._oleobj_.GetIDsOfNames("ВыбратьСтроки")
        doc._oleobj_.InvokeTypes(
            dispid_select_rows,
            0,
            1,  # DISPATCH_METHOD
            (11, 0),  # VT_BOOL return
            ()
        )

        # Получаем dispid для ПолучитьСтроку
        dispid_get_row = doc._oleobj_.GetIDsOfNames("ПолучитьСтроку")

        while True:
            # Вызываем ПолучитьСтроку
            result = doc._oleobj_.InvokeTypes(
                dispid_get_row,
                0,
                1,  # DISPATCH_METHOD
                (3, 0),  # VT_I4 return (integer)
                ()
            )

            if result != 1:
                break

            row = {}
            # Получаем все доступные атрибуты строки
            # Для универсальности пробуем стандартные поля
            for attr in [
                "Номенклатура", "Наименование", "Количество", "Единица",
                "Коэффициент", "Цена", "Сумма", "СтавкаНДС", "СуммаНДС",
                "СтавкаНП", "СуммаНП", "Партия", "ПоставщикТары",
                "СтранаПроисхождения", "ГТД"
            ]:
                val = safe_getattr(doc, attr)
                if val is not None:
                    row[attr] = convert_1c_value(val)

            if row:  # Добавляем только непустые строки
                table_part.append(row)

    except Exception as e:
        logger.warning("Ошибка при чтении табличной части: %s", e)

    return table_part


def fetch_realizations(v7, start_date: str, end_date: str) -> list[dict]:
    """
    Выгрузка документов Реализация за период.

    Args:
        v7: COM-объект V77.Application
        start_date: Дата начала в формате дд.мм.гггг
        end_date: Дата конца в формате дд.мм.гггг

    Returns:
        Список словарей с данными документов
    """
    logger.info("Выгрузка документов Реализация: %s - %s", start_date, end_date)

    documents = []

    try:
        # Создаем объект документа
        doc = v7.CreateObject("Документ.Реализация")

        # Вызываем метод ВыбратьДокументы через низкоуровневый COM API
        dispid_select = doc._oleobj_.GetIDsOfNames("ВыбратьДокументы")
        doc._oleobj_.InvokeTypes(
            dispid_select,
            0,
            1,  # DISPATCH_METHOD
            (11, 0),  # VT_BOOL return
            ((8, 1), (8, 1)),  # два VT_BSTR параметра
            start_date,
            end_date
        )

        # Получаем dispid для ПолучитьДокумент
        dispid_get = doc._oleobj_.GetIDsOfNames("ПолучитьДокумент")

        while True:
            # Вызываем ПолучитьДокумент
            result = doc._oleobj_.InvokeTypes(
                dispid_get,
                0,
                1,  # DISPATCH_METHOD
                (3, 0),  # VT_I4 return (integer)
                ()
            )

            if result != 1:
                break

            # Пропускаем помеченные на удаление
            pom_udal = safe_getattr(doc, "ПометкаУдаления")
            if callable(pom_udal) and pom_udal() == 1:
                continue

            # Пропускаем непроведенные
            proveden = safe_getattr(doc, "Проведен")
            if callable(proveden) and proveden() == 0:
                continue

            number = convert_1c_value(safe_getattr(doc, "НомерДок")) or ""
            date_obj = safe_getattr(doc, "ДатаДок")
            doc_date = date_to_ru(date_obj) or ""
            contractor = convert_1c_value(safe_getattr(doc, "Контрагент")) or ""
            contract = convert_1c_value(safe_getattr(doc, "Договор")) or ""
            warehouse = convert_1c_value(safe_getattr(doc, "Склад")) or ""
            currency = convert_1c_value(safe_getattr(doc, "Валюта")) or ""
            sum_val = round(to_float(safe_getattr(doc, "СуммаВзаиморасчетов")), 2)
            payment_date_obj = safe_getattr(doc, "ДатаОплаты")
            payment_date = date_to_ru(payment_date_obj) or ""

            table_part = get_document_table_part(doc)

            documents.append({
                "number": number,
                "date": doc_date,
                "contractor": contractor,
                "contract": contract,
                "warehouse": warehouse,
                "currency": currency,
                "sum": sum_val,
                "payment_date": payment_date,
                "table_part": table_part
            })

    except Exception as e:
        logger.error("Ошибка при выгрузке документов Реализация: %s", e)
        raise

    logger.info("Выгружено документов Реализация: %d", len(documents))
    return documents


def fetch_invoices(v7, start_date: str, end_date: str) -> list[dict]:
    """
    Выгрузка документов СчетФактураВыданный за период.

    Args:
        v7: COM-объект V77.Application
        start_date: Дата начала в формате дд.мм.гггг
        end_date: Дата конца в формате дд.мм.гггг

    Returns:
        Список словарей с данными документов
    """
    logger.info("Выгрузка документов СчетФактураВыданный: %s - %s", start_date, end_date)

    documents = []

    try:
        # Создаем объект документа
        doc = v7.CreateObject("Документ.СчетФактураВыданный")

        # Вызываем метод ВыбратьДокументы через низкоуровневый COM API
        dispid_select = doc._oleobj_.GetIDsOfNames("ВыбратьДокументы")
        doc._oleobj_.InvokeTypes(
            dispid_select,
            0,
            1,  # DISPATCH_METHOD
            (11, 0),  # VT_BOOL return
            ((8, 1), (8, 1)),  # два VT_BSTR параметра
            start_date,
            end_date
        )

        # Получаем dispid для ПолучитьДокумент
        dispid_get = doc._oleobj_.GetIDsOfNames("ПолучитьДокумент")

        while True:
            # Вызываем ПолучитьДокумент
            result = doc._oleobj_.InvokeTypes(
                dispid_get,
                0,
                1,  # DISPATCH_METHOD
                (3, 0),  # VT_I4 return (integer)
                ()
            )

            if result != 1:
                break

            # Пропускаем помеченные на удаление
            pom_udal = safe_getattr(doc, "ПометкаУдаления")
            if callable(pom_udal) and pom_udal() == 1:
                continue

            # Пропускаем непроведенные
            proveden = safe_getattr(doc, "Проведен")
            if callable(proveden) and proveden() == 0:
                continue

            number = convert_1c_value(safe_getattr(doc, "НомерДок")) or ""
            date_obj = safe_getattr(doc, "ДатаДок")
            doc_date = date_to_ru(date_obj) or ""
            contractor = convert_1c_value(safe_getattr(doc, "Контрагент")) or ""
            contract = convert_1c_value(safe_getattr(doc, "Договор")) or ""
            doc_base = convert_1c_value(safe_getattr(doc, "ДокОснование")) or ""
            currency = convert_1c_value(safe_getattr(doc, "Валюта")) or ""
            payment_doc_number = convert_1c_value(safe_getattr(doc, "НомерПлатРасчДок")) or ""
            payment_doc_date_obj = safe_getattr(doc, "ДатаПлатРасчДок")
            payment_doc_date = date_to_ru(payment_doc_date_obj) or ""

            table_part = get_document_table_part(doc)
            total_sum = round(sum(to_float(row.get("Сумма", 0)) for row in table_part), 2)

            documents.append({
                "number": number,
                "date": doc_date,
                "contractor": contractor,
                "contract": contract,
                "doc_base": doc_base,
                "currency": currency,
                "payment_doc_number": payment_doc_number,
                "payment_doc_date": payment_doc_date,
                "sum": total_sum,
                "table_part": table_part
            })

    except Exception as e:
        logger.error("Ошибка при выгрузке документов СчетФактураВыданный: %s", e)
        raise

    logger.info("Выгружено документов СчетФактураВыданный: %d", len(documents))
    return documents
