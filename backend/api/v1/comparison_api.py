"""API endpoints для сравнения документов 1С 7.7 и 1С 8."""

import logging

from fastapi import APIRouter, HTTPException

from backend.api.v1.comparison import compare_documents
from backend.api.v1.documents_1c8 import fetch_invoices_1c8, fetch_realizations_1c8
from backend.api.v1.documents_77 import _fetch_invoices_sync, _fetch_realizations_sync
from backend.models import DocumentFilter
from backend.api.v1.comparison import ComparisonResult
from backend.database import db

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
        
        # Сохраняем в БД
        db.save_documents_77(docs_77, "realization", firm_prefix)
        db.save_documents_1c8(docs_8, "realization", firm_prefix)
        
        # Сравниваем
        result = compare_documents(docs_77, docs_8, "realizations")
        
        # Сохраняем результаты сравнения
        for doc in result.mismatches + result.only_in_77 + result.only_in_8:
            sum_77 = doc.get('sum_77')
            sum_1c8 = doc.get('sum_1c8')
            has_diff = sum_77 is not None and sum_1c8 is not None and abs(sum_77 - sum_1c8) > 0.01
            diff_amount = abs(sum_77 - sum_1c8) if has_diff else 0.0
            
            db.save_comparison_result(
                doc_type="realization",
                number=doc.get('number', ''),
                date=doc.get('date', ''),
                sum_77=sum_77,
                sum_1c8=sum_1c8,
                has_difference=has_diff,
                difference_amount=diff_amount
            )
        
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
        
        # Сохраняем в БД
        db.save_documents_77(docs_77, "invoice", firm_prefix)
        db.save_documents_1c8(docs_8, "invoice", firm_prefix)
        
        # Сравниваем
        result = compare_documents(docs_77, docs_8, "invoices")
        
        # Сохраняем результаты сравнения
        for doc in result.mismatches + result.only_in_77 + result.only_in_8:
            sum_77 = doc.get('sum_77')
            sum_1c8 = doc.get('sum_1c8')
            has_diff = sum_77 is not None and sum_1c8 is not None and abs(sum_77 - sum_1c8) > 0.01
            diff_amount = abs(sum_77 - sum_1c8) if has_diff else 0.0
            
            db.save_comparison_result(
                doc_type="invoice",
                number=doc.get('number', ''),
                date=doc.get('date', ''),
                sum_77=sum_77,
                sum_1c8=sum_1c8,
                has_difference=has_diff,
                difference_amount=diff_amount
            )
        
        return result
        
    except Exception as e:
        logger.exception("Ошибка при сравнении документов Счет-фактура")
        raise HTTPException(status_code=500, detail=f"Ошибка при сравнении: {str(e)}")


@router.get("/db/history", response_model=list)
async def get_comparison_history(doc_type: str | None = None, only_differences: bool = False):
    """
    Получить историю сравнений из базы данных.
    
    Args:
        doc_type: Тип документа (realization или invoice)
        only_differences: Только расхождения
    
    Returns:
        Список результатов сравнения
    """
    try:
        return db.get_comparison_history(doc_type, only_differences)
    except Exception as e:
        logger.exception("Ошибка при получении истории сравнений")
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")


@router.get("/db/documents/77", response_model=list)
async def get_documents_77_from_db(
    doc_type: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    firm_prefix: str | None = None
):
    """
    Получить документы 1С 7.7 из базы данных.
    
    Args:
        doc_type: Тип документа
        start_date: Дата начала
        end_date: Дата конца
        firm_prefix: Префикс фирмы
    
    Returns:
        Список документов
    """
    try:
        return db.get_documents_77(doc_type, start_date, end_date, firm_prefix)
    except Exception as e:
        logger.exception("Ошибка при получении документов 7.7 из БД")
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")


@router.get("/db/documents/1c8", response_model=list)
async def get_documents_1c8_from_db(
    doc_type: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    firm_prefix: str | None = None
):
    """
    Получить документы 1С 8 из базы данных.
    
    Args:
        doc_type: Тип документа
        start_date: Дата начала
        end_date: Дата конца
        firm_prefix: Префикс фирмы
    
    Returns:
        Список документов
    """
    try:
        return db.get_documents_1c8(doc_type, start_date, end_date, firm_prefix)
    except Exception as e:
        logger.exception("Ошибка при получении документов 1C8 из БД")
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")
