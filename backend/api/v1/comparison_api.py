"""API endpoints для сравнения документов 1С 7.7 и 1С 8."""

import logging

from fastapi import APIRouter, HTTPException

from backend.api.v1.comparison import compare_documents
from backend.api.v1.documents_1c8 import fetch_invoices_1c8, fetch_realizations_1c8
from backend.api.v1.documents_77 import _fetch_invoices_sync, _fetch_realizations_sync
from backend.models import DocumentFilter
from backend.api.v1.comparison import ComparisonResult

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["Comparison"])


@router.post("/compare/realizations", response_model=ComparisonResult)
async def compare_realizations(filter: DocumentFilter, firm_prefix: str | None = None):
    """
    Сравнить документы Реализация из 1С 7.7 и 1С 8.
    
    Args:
        filter: Фильтр с датами начала и конца периода
        firm_prefix: Префикс фирмы для фильтрации (опционально)
    
    Returns:
        Результат сравнения документов
    """
    try:
        logger.info("Сравнение документов Реализация: %s - %s", filter.start_date, filter.end_date)
        
        # Получаем документы из обеих баз
        docs_77 = _fetch_realizations_sync(filter.start_date, filter.end_date)
        docs_8 = await fetch_realizations_1c8(filter.start_date, filter.end_date, firm_prefix)
        
        # Сравниваем
        result = compare_documents(docs_77, docs_8, "realizations")
        
        return result
        
    except Exception as e:
        logger.exception("Ошибка при сравнении документов Реализация")
        raise HTTPException(status_code=500, detail=f"Ошибка при сравнении: {str(e)}")


@router.post("/compare/invoices", response_model=ComparisonResult)
async def compare_invoices(filter: DocumentFilter, firm_prefix: str | None = None):
    """
    Сравнить документы Счет-фактура выданный из 1С 7.7 и 1С 8.
    
    Args:
        filter: Фильтр с датами начала и конца периода
        firm_prefix: Префикс фирмы для фильтрации (опционально)
    
    Returns:
        Результат сравнения документов
    """
    try:
        logger.info("Сравнение документов Счет-фактура: %s - %s", filter.start_date, filter.end_date)
        
        # Получаем документы из обеих баз
        docs_77 = _fetch_invoices_sync(filter.start_date, filter.end_date)
        docs_8 = await fetch_invoices_1c8(filter.start_date, filter.end_date, firm_prefix)
        
        # Сравниваем
        result = compare_documents(docs_77, docs_8, "invoices")
        
        return result
        
    except Exception as e:
        logger.exception("Ошибка при сравнении документов Счет-фактура")
        raise HTTPException(status_code=500, detail=f"Ошибка при сравнении: {str(e)}")
