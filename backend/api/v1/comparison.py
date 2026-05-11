"""Модуль для сравнения документов 1С 7.7 и 1С 8."""

import logging
from typing import Literal
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class DocumentComparison(BaseModel):
    """Результат сравнения одного документа."""
    
    number: str = Field(..., description="Номер документа")
    date_77: str = Field(default="", description="Дата в 1С 7.7")
    date_8: str = Field(default="", description="Дата в 1С 8")
    sum_77: float = Field(default=0.0, description="Сумма в 1С 7.7")
    sum_8: float = Field(default=0.0, description="Сумма в 1С 8")
    contractor: str = Field(default="", description="Контрагент")
    has_mismatch: bool = Field(default=False, description="Есть ли расхождения")
    mismatch_type: str = Field(default="", description="Тип расхождения")
    source: Literal["77", "8", "both"] = Field(default="both", description="Источник документа")
    

class ComparisonResult(BaseModel):
    """Результат сравнения наборов документов."""
    
    total_77: int = Field(..., description="Всего документов в 1С 7.7")
    total_8: int = Field(..., description="Всего документов в 1С 8")
    matched: int = Field(..., description="Совпавших документов")
    mismatched: int = Field(..., description="Документов с расхождениями")
    only_in_77: int = Field(..., description="Только в 1С 7.7")
    only_in_8: int = Field(..., description="Только в 1С 8")
    documents: list[DocumentComparison] = Field(default_factory=list, description="Детали сравнения")
    sequence_errors: list[dict] = Field(default_factory=list, description="Ошибки последовательности нумерации")


def compare_documents(
    docs_77: list[dict],
    docs_8: list[dict],
    doc_type: str = "realizations"
) -> ComparisonResult:
    """
    Сравнить документы из 1С 7.7 и 1С 8.
    
    Args:
        docs_77: Список документов из 1С 7.7
        docs_8: Список документов из 1С 8
        doc_type: Тип документа (realizations или invoices)
    
    Returns:
        Результат сравнения
    """
    logger.info("Сравнение документов: %s", doc_type)
    logger.info("1С 7.7: %d документов, 1С 8: %d документов", len(docs_77), len(docs_8))
    
    # Создаем словари для быстрого поиска по номеру
    dict_77 = {doc["number"]: doc for doc in docs_77}
    dict_8 = {doc["number"]: doc for doc in docs_8}
    
    all_numbers = set(dict_77.keys()) | set(dict_8.keys())
    
    comparisons = []
    matched = 0
    mismatched = 0
    only_in_77 = 0
    only_in_8 = 0
    
    for number in sorted(all_numbers):
        doc_77 = dict_77.get(number)
        doc_8 = dict_8.get(number)
        
        if doc_77 and doc_8:
            # Документ есть в обеих базах - сравниваем
            has_mismatch = False
            mismatch_type = ""
            
            # Сравниваем суммы (с допустимой погрешностью 0.01)
            sum_diff = abs(doc_77.get("sum", 0) - doc_8.get("sum", 0))
            if sum_diff > 0.01:
                has_mismatch = True
                mismatch_type = "Разная сумма"
            
            comparison = DocumentComparison(
                number=number,
                date_77=doc_77.get("date", ""),
                date_8=doc_8.get("date", ""),
                sum_77=doc_77.get("sum", 0),
                sum_8=doc_8.get("sum", 0),
                contractor=doc_77.get("contractor") or doc_8.get("contractor", ""),
                has_mismatch=has_mismatch,
                mismatch_type=mismatch_type,
                source="both"
            )
            
            if has_mismatch:
                mismatched += 1
            else:
                matched += 1
                
        elif doc_77:
            # Только в 1С 7.7
            comparison = DocumentComparison(
                number=number,
                date_77=doc_77.get("date", ""),
                sum_77=doc_77.get("sum", 0),
                contractor=doc_77.get("contractor", ""),
                has_mismatch=True,
                mismatch_type="Отсутствует в 1С 8",
                source="77"
            )
            only_in_77 += 1
            
        else:
            # Только в 1С 8
            comparison = DocumentComparison(
                number=number,
                date_8=doc_8.get("date", ""),
                sum_8=doc_8.get("sum", 0),
                contractor=doc_8.get("contractor", ""),
                has_mismatch=True,
                mismatch_type="Отсутствует в 1С 7.7",
                source="8"
            )
            only_in_8 += 1
        
        comparisons.append(comparison)
    
    # Проверяем последовательность нумерации
    sequence_errors = check_sequence_numbering(docs_77, docs_8, doc_type)
    
    result = ComparisonResult(
        total_77=len(docs_77),
        total_8=len(docs_8),
        matched=matched,
        mismatched=mismatched,
        only_in_77=only_in_77,
        only_in_8=only_in_8,
        documents=comparisons,
        sequence_errors=sequence_errors
    )
    
    logger.info(
        "Результат сравнения: совпало=%d, расхождений=%d, только в 7.7=%d, только в 8=%d",
        matched, mismatched, only_in_77, only_in_8
    )
    
    return result


def check_sequence_numbering(
    docs_77: list[dict],
    docs_8: list[dict],
    doc_type: str
) -> list[dict]:
    """
    Проверить последовательность нумерации документов.
    
    Args:
        docs_77: Документы из 1С 7.7
        docs_8: Документы из 1С 8
        doc_type: Тип документа
    
    Returns:
        Список ошибок последовательности
    """
    errors = []
    
    # Извлекаем префиксы и номера
    def extract_prefix_and_number(doc_number: str) -> tuple[str, int]:
        """Извлечь префикс и номер из строки вида 'ПРЕФИКС-123' или '123'."""
        if '-' in doc_number:
            parts = doc_number.split('-', 1)
            prefix = parts[0]
            try:
                number = int(parts[1])
                return prefix, number
            except ValueError:
                return doc_number, 0
        else:
            try:
                return "", int(doc_number)
            except ValueError:
                return doc_number, 0
    
    for source_name, docs in [("1С 7.7", docs_77), ("1С 8", docs_8)]:
        # Группируем по префиксам
        by_prefix: dict[str, list[tuple[str, int]]] = {}
        for doc in docs:
            prefix, number = extract_prefix_and_number(doc.get("number", ""))
            if prefix not in by_prefix:
                by_prefix[prefix] = []
            by_prefix[prefix].append((doc.get("number", ""), number))
        
        # Проверяем последовательность внутри каждого префикса
        for prefix, items in by_prefix.items():
            # Сортируем по номерам
            sorted_items = sorted(items, key=lambda x: x[1])
            
            for i in range(1, len(sorted_items)):
                prev_number = sorted_items[i-1][1]
                curr_number = sorted_items[i][1]
                
                # Пропускаем нулевые номера (не удалось распарсить)
                if prev_number == 0 or curr_number == 0:
                    continue
                
                # Проверяем разрыв в нумерации
                if curr_number - prev_number > 1:
                    missing_count = curr_number - prev_number - 1
                    errors.append({
                        "source": source_name,
                        "prefix": prefix or "без префикса",
                        "error_type": "gap",
                        "description": f"Пропуск номеров между {sorted_items[i-1][0]} и {sorted_items[i][0]}",
                        "missing_count": missing_count,
                        "from_number": sorted_items[i-1][0],
                        "to_number": sorted_items[i][0]
                    })
                
                # Проверяем дубликаты
                if curr_number == prev_number:
                    errors.append({
                        "source": source_name,
                        "prefix": prefix or "без префикса",
                        "error_type": "duplicate",
                        "description": f"Дубликат номера {sorted_items[i][0]}",
                        "number": sorted_items[i][0]
                    })
    
    return errors
