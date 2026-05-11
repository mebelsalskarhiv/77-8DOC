"""Pydantic модели для API."""

from pydantic import BaseModel, Field


class DocumentFilter(BaseModel):
    """Фильтр для выборки документов по периоду."""

    start_date: str = Field(..., description="Дата начала периода (дд.мм.гггг)")
    end_date: str = Field(..., description="Дата конца периода (дд.мм.гггг)")


class RealizationDocument(BaseModel):
    """Документ Реализация."""

    number: str = Field(..., description="Номер документа")
    date: str = Field(..., description="Дата документа (дд.мм.гггг)")
    contractor: str = Field(..., description="Контрагент")
    contract: str = Field(..., description="Договор")
    warehouse: str = Field(..., description="Склад")
    currency: str = Field(default="", description="Валюта")
    sum: float = Field(..., description="Сумма взаиморасчетов")
    payment_date: str = Field(default="", description="Дата оплаты")
    table_part: list[dict] = Field(default_factory=list, description="Табличная часть")


class InvoiceDocument(BaseModel):
    """Документ Счет-фактура выданный."""

    number: str = Field(..., description="Номер документа")
    date: str = Field(..., description="Дата документа (дд.мм.гггг)")
    contractor: str = Field(..., description="Контрагент")
    contract: str = Field(..., description="Договор")
    doc_base: str = Field(default="", description="Документ-основание")
    currency: str = Field(default="", description="Валюта")
    payment_doc_number: str = Field(default="", description="Номер платежного документа")
    payment_doc_date: str = Field(default="", description="Дата платежного документа")
    sum: float = Field(..., description="Сумма документа")
    table_part: list[dict] = Field(default_factory=list, description="Табличная часть")


class ErrorResponse(BaseModel):
    """Ответ с ошибкой."""

    detail: str = Field(..., description="Описание ошибки")
