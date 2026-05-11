"""API endpoints для работы с документами 1С 8 через OData."""

import logging
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException

from backend.config import settings
from backend.models import DocumentFilter, InvoiceDocument, RealizationDocument

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["1C 8 OData Documents"])


def _get_odata_url() -> str:
    """Получить базовый URL OData."""
    return settings.odoo_1c8_url or "http://localhost:8080/hs/odata"


def _get_auth() -> tuple[str, str]:
    """Получить учетные данные для аутентификации."""
    return (settings.odoo_1c8_user or "", settings.odoo_1c8_password or "")


def _convert_date_from_iso(date_str: str) -> str:
    """Конвертировать дату из ISO формата (YYYY-MM-DD) в русский (ДД.ММ.ГГГГ)."""
    if not date_str:
        return ""
    try:
        # Обрезаем до даты и конвертируем
        date_part = date_str[:10]
        parts = date_part.split("-")
        if len(parts) == 3:
            return f"{parts[2]}.{parts[1]}.{parts[0]}"
        return date_part
    except Exception:
        return date_str


async def fetch_realizations_1c8(
    start_date: str,
    end_date: str,
    firm_prefix: Optional[str] = None
) -> list[dict]:
    """
    Получение документов Реализация из 1С 8 через OData.

    Args:
        start_date: Дата начала в формате дд.мм.гггг
        end_date: Дата конца в формате дд.мм.гггг
        firm_prefix: Префикс фирмы (опционально)

    Returns:
        Список словарей с данными документов
    """
    logger.info("Запрос документов Реализация 1С 8: %s - %s", start_date, end_date)

    # Преобразуем даты в формат YYYY-MM-DD для OData фильтра
    try:
        day, month, year = start_date.split('.')
        start_date_odata = f"{year}-{month}-{day}"
        day, month, year = end_date.split('.')
        end_date_odata = f"{year}-{month}-{day}"
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Неверный формат даты: {e}")

    # Формируем фильтр OData
    filter_parts = [f"Date ge datetime'{start_date_odata}T00:00:00'", 
                    f"Date le datetime'{end_date_odata}T23:59:59'"]
    
    if firm_prefix:
        filter_parts.append(f"Organization/Code eq '{firm_prefix}'")

    filter_query = " and ".join(filter_parts)

    url = f"{_get_odata_url()}/РеализацияТоваровУслуг"
    params = {
        "$filter": filter_query,
        "$format": "json"
    }

    try:
        async with httpx.AsyncClient(auth=_get_auth(), timeout=30.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        documents = []
        for item in data.get("value", []):
            # Извлекаем данные с учетом возможной вложенности
            contractor_data = item.get("Контрагент", {})
            contract_data = item.get("Договор", {})
            warehouse_data = item.get("Склад", {})
            currency_data = item.get("Валюта", {})
            
            doc = {
                "number": item.get("Number", ""),
                "date": _convert_date_from_iso(item.get("Date", "")),
                "contractor": contractor_data.get("Description", "") if isinstance(contractor_data, dict) else str(contractor_data),
                "contract": contract_data.get("Description", "") if isinstance(contract_data, dict) else str(contract_data),
                "warehouse": warehouse_data.get("Description", "") if isinstance(warehouse_data, dict) else str(warehouse_data),
                "currency": currency_data.get("Code", "") if isinstance(currency_data, dict) else str(currency_data),
                "sum": float(item.get("СуммаДокумента", 0) or 0),
                "table_part": []
            }
            
            documents.append(doc)

        logger.info("Получено документов Реализация 1С 8: %d", len(documents))
        return documents

    except httpx.HTTPError as e:
        logger.error("Ошибка при запросе к 1С 8 OData: %s", e)
        raise HTTPException(status_code=500, detail=f"Ошибка подключения к 1С 8: {str(e)}")
    except Exception as e:
        logger.exception("Неожиданная ошибка при получении документов 1С 8")
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")


async def fetch_invoices_1c8(
    start_date: str,
    end_date: str,
    firm_prefix: Optional[str] = None
) -> list[dict]:
    """
    Получение документов Счет-фактура выданный из 1С 8 через OData.

    Args:
        start_date: Дата начала в формате дд.мм.гггг
        end_date: Дата конца в формате дд.мм.гггг
        firm_prefix: Префикс фирмы (опционально)

    Returns:
        Список словарей с данными документов
    """
    logger.info("Запрос документов Счет-фактура 1С 8: %s - %s", start_date, end_date)

    # Преобразуем даты в формат YYYY-MM-DD для OData фильтра
    try:
        day, month, year = start_date.split('.')
        start_date_odata = f"{year}-{month}-{day}"
        day, month, year = end_date.split('.')
        end_date_odata = f"{year}-{month}-{day}"
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Неверный формат даты: {e}")

    # Формируем фильтр OData
    filter_parts = [f"Date ge datetime'{start_date_odata}T00:00:00'", 
                    f"Date le datetime'{end_date_odata}T23:59:59'"]
    
    if firm_prefix:
        filter_parts.append(f"Organization/Code eq '{firm_prefix}'")

    filter_query = " and ".join(filter_parts)

    url = f"{_get_odata_url()}/СчетФактураВыданный"
    params = {
        "$filter": filter_query,
        "$format": "json"
    }

    try:
        async with httpx.AsyncClient(auth=_get_auth(), timeout=30.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        documents = []
        for item in data.get("value", []):
            # Извлекаем данные с учетом возможной вложенности
            contractor_data = item.get("Контрагент", {})
            contract_data = item.get("Договор", {})
            base_data = item.get("Основание", {})
            currency_data = item.get("Валюта", {})
            
            doc = {
                "number": item.get("Number", ""),
                "date": _convert_date_from_iso(item.get("Date", "")),
                "contractor": contractor_data.get("Description", "") if isinstance(contractor_data, dict) else str(contractor_data),
                "contract": contract_data.get("Description", "") if isinstance(contract_data, dict) else str(contract_data),
                "doc_base": base_data.get("Description", "") if isinstance(base_data, dict) else str(base_data),
                "currency": currency_data.get("Code", "") if isinstance(currency_data, dict) else str(currency_data),
                "sum": float(item.get("СуммаДокумента", 0) or 0),
                "table_part": []
            }
            
            documents.append(doc)

        logger.info("Получено документов Счет-фактура 1С 8: %d", len(documents))
        return documents

    except httpx.HTTPError as e:
        logger.error("Ошибка при запросе к 1С 8 OData: %s", e)
        raise HTTPException(status_code=500, detail=f"Ошибка подключения к 1С 8: {str(e)}")
    except Exception as e:
        logger.exception("Неожиданная ошибка при получении документов 1С 8")
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")


@router.post("/documents/1c8/realizations", response_model=list[RealizationDocument])
async def get_realizations_1c8(filter: DocumentFilter, firm_prefix: Optional[str] = None):
    """Получить документы Реализация из 1С 8 за период."""
    # Используем firm_prefix из filter если не передан явно
    prefix = firm_prefix or (filter.firm_prefix if hasattr(filter, 'firm_prefix') else None)
    documents = await fetch_realizations_1c8(filter.start_date, filter.end_date, prefix)
    return documents


@router.post("/documents/1c8/invoices", response_model=list[InvoiceDocument])
async def get_invoices_1c8(filter: DocumentFilter, firm_prefix: Optional[str] = None):
    """Получить документы Счет-фактура выданный из 1С 8 за период."""
    # Используем firm_prefix из filter если не передан явно
    prefix = firm_prefix or (filter.firm_prefix if hasattr(filter, 'firm_prefix') else None)
    documents = await fetch_invoices_1c8(filter.start_date, filter.end_date, prefix)
    return documents

