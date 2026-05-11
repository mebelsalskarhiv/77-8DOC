"""API endpoints для работы с документами 1С 7.7."""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, HTTPException

from backend.config import settings
from backend.models import DocumentFilter, InvoiceDocument, RealizationDocument
from backend.ole_1c77 import Connection1C77, fetch_invoices, fetch_realizations
from backend.database import db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["1C 7.7 Documents"])

# Executor для выполнения синхронных COM-операций в отдельном потоке
executor = ThreadPoolExecutor(max_workers=1)

# Singleton соединения с 1С
connection = Connection1C77()


async def run_in_executor(func, *args):
    """Выполнить синхронную функцию в executor."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, func, *args)


def _fetch_realizations_sync(start_date: str, end_date: str) -> list[dict]:
    """Синхронная обертка для fetch_realizations."""
    with connection.session(
        settings.db_path_77,
        settings.db_user_77,
        settings.db_password_77
    ) as v7:
        return fetch_realizations(v7, start_date, end_date)


def _fetch_invoices_sync(start_date: str, end_date: str) -> list[dict]:
    """Синхронная обертка для fetch_invoices."""
    with connection.session(
        settings.db_path_77,
        settings.db_user_77,
        settings.db_password_77
    ) as v7:
        return fetch_invoices(v7, start_date, end_date)


@router.post("/documents/77/realizations", response_model=list[RealizationDocument])
async def get_realizations(filter: DocumentFilter):
    """
    Получить документы Реализация за период.

    Args:
        filter: Фильтр с датами начала и конца периода

    Returns:
        Список документов Реализация
    """
    try:
        logger.info(
            "Запрос документов Реализация: %s - %s",
            filter.start_date,
            filter.end_date
        )
        documents = await run_in_executor(
            _fetch_realizations_sync,
            filter.start_date,
            filter.end_date
        )
        
        # Фильтрация по префиксу фирмы если указан
        if hasattr(filter, 'firm_prefix') and filter.firm_prefix:
            prefix = filter.firm_prefix.upper().strip()
            documents = [d for d in documents if d.get('number', '').upper().startswith(prefix)]
        
        # Сохраняем в БД
        db.save_documents_77(documents, "realization", filter.firm_prefix if hasattr(filter, 'firm_prefix') else None)
        
        return documents
    except Exception as e:
        logger.exception("Ошибка при получении документов Реализация")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении документов: {str(e)}"
        )


@router.post("/documents/77/invoices", response_model=list[InvoiceDocument])
async def get_invoices(filter: DocumentFilter):
    """
    Получить документы Счет-фактура выданный за период.

    Args:
        filter: Фильтр с датами начала и конца периода

    Returns:
        Список документов Счет-фактура выданный
    """
    try:
        logger.info(
            "Запрос документов СчетФактураВыданный: %s - %s",
            filter.start_date,
            filter.end_date
        )
        documents = await run_in_executor(
            _fetch_invoices_sync,
            filter.start_date,
            filter.end_date
        )
        
        # Фильтрация по префиксу фирмы если указан
        if hasattr(filter, 'firm_prefix') and filter.firm_prefix:
            prefix = filter.firm_prefix.upper().strip()
            documents = [d for d in documents if d.get('number', '').upper().startswith(prefix)]
        
        # Сохраняем в БД
        db.save_documents_77(documents, "invoice", filter.firm_prefix if hasattr(filter, 'firm_prefix') else None)
        
        return documents
    except Exception as e:
        logger.exception("Ошибка при получении документов СчетФактураВыданный")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении документов: {str(e)}"
        )
