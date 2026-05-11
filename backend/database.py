"""Модуль для работы с SQLite базой данных."""

import logging
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class Database:
    """Класс для работы с SQLite базой данных."""

    def __init__(self, db_path: str = "documents.db"):
        """
        Инициализация базы данных.

        Args:
            db_path: Путь к файлу базы данных
        """
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def get_connection(self):
        """Контекстный менеджер для подключения к БД."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        """Инициализация схемы базы данных."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Таблица для документов 1С 7.7
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents_77 (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    doc_type TEXT NOT NULL,
                    number TEXT NOT NULL,
                    date TEXT NOT NULL,
                    sum REAL NOT NULL,
                    contractor TEXT,
                    contract TEXT,
                    warehouse TEXT,
                    currency TEXT,
                    doc_base TEXT,
                    firm_prefix TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(doc_type, number, date)
                )
            """)

            # Таблица для документов 1С 8
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents_1c8 (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    doc_type TEXT NOT NULL,
                    number TEXT NOT NULL,
                    date TEXT NOT NULL,
                    sum REAL NOT NULL,
                    contractor TEXT,
                    contract TEXT,
                    warehouse TEXT,
                    currency TEXT,
                    doc_base TEXT,
                    firm_prefix TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(doc_type, number, date)
                )
            """)

            # Таблица для результатов сравнения
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS comparison_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    doc_type TEXT NOT NULL,
                    number TEXT NOT NULL,
                    date TEXT NOT NULL,
                    sum_77 REAL,
                    sum_1c8 REAL,
                    has_difference BOOLEAN NOT NULL,
                    difference_amount REAL,
                    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Индексы для ускорения поиска
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_documents_77_number 
                ON documents_77(number)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_documents_77_date 
                ON documents_77(date)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_documents_77_type 
                ON documents_77(doc_type)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_documents_77_prefix 
                ON documents_77(firm_prefix)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_documents_1c8_number 
                ON documents_1c8(number)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_documents_1c8_date 
                ON documents_1c8(date)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_documents_1c8_type 
                ON documents_1c8(doc_type)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_documents_1c8_prefix 
                ON documents_1c8(firm_prefix)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_comparison_number 
                ON comparison_results(number)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_comparison_type 
                ON comparison_results(doc_type)
            """)

            conn.commit()
            logger.info("База данных инициализирована: %s", self.db_path)

    def save_documents_77(self, documents: list[dict], doc_type: str, firm_prefix: Optional[str] = None):
        """
        Сохранение документов из 1С 7.7.

        Args:
            documents: Список документов
            doc_type: Тип документа ('realization' или 'invoice')
            firm_prefix: Префикс фирмы
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            for doc in documents:
                try:
                    cursor.execute("""
                        INSERT OR REPLACE INTO documents_77 
                        (doc_type, number, date, sum, contractor, contract, warehouse, currency, doc_base, firm_prefix)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        doc_type,
                        doc.get('number', ''),
                        doc.get('date', ''),
                        doc.get('sum', 0),
                        doc.get('contractor', ''),
                        doc.get('contract', ''),
                        doc.get('warehouse', ''),
                        doc.get('currency', ''),
                        doc.get('doc_base', ''),
                        firm_prefix
                    ))
                except Exception as e:
                    logger.error("Ошибка сохранения документа 77: %s", e)

            conn.commit()
            logger.info("Сохранено документов 7.7 (%s): %d", doc_type, len(documents))

    def save_documents_1c8(self, documents: list[dict], doc_type: str, firm_prefix: Optional[str] = None):
        """
        Сохранение документов из 1С 8.

        Args:
            documents: Список документов
            doc_type: Тип документа ('realization' или 'invoice')
            firm_prefix: Префикс фирмы
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            for doc in documents:
                try:
                    cursor.execute("""
                        INSERT OR REPLACE INTO documents_1c8 
                        (doc_type, number, date, sum, contractor, contract, warehouse, currency, doc_base, firm_prefix)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        doc_type,
                        doc.get('number', ''),
                        doc.get('date', ''),
                        doc.get('sum', 0),
                        doc.get('contractor', ''),
                        doc.get('contract', ''),
                        doc.get('warehouse', ''),
                        doc.get('currency', ''),
                        doc.get('doc_base', ''),
                        firm_prefix
                    ))
                except Exception as e:
                    logger.error("Ошибка сохранения документа 1C8: %s", e)

            conn.commit()
            logger.info("Сохранено документов 1C8 (%s): %d", doc_type, len(documents))

    def save_comparison_result(
        self,
        doc_type: str,
        number: str,
        date: str,
        sum_77: Optional[float],
        sum_1c8: Optional[float],
        has_difference: bool,
        difference_amount: float
    ):
        """
        Сохранение результата сравнения документов.

        Args:
            doc_type: Тип документа
            number: Номер документа
            date: Дата документа
            sum_77: Сумма из 1С 7.7
            sum_1c8: Сумма из 1С 8
            has_difference: Есть ли расхождение
            difference_amount: Величина расхождения
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO comparison_results 
                (doc_type, number, date, sum_77, sum_1c8, has_difference, difference_amount)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                doc_type,
                number,
                date,
                sum_77,
                sum_1c8,
                has_difference,
                difference_amount
            ))
            conn.commit()

    def get_documents_77(
        self,
        doc_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        firm_prefix: Optional[str] = None
    ) -> list[dict]:
        """
        Получение документов из 1С 7.7.

        Args:
            doc_type: Тип документа
            start_date: Дата начала
            end_date: Дата конца
            firm_prefix: Префикс фирмы

        Returns:
            Список документов
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            query = "SELECT * FROM documents_77 WHERE 1=1"
            params = []

            if doc_type:
                query += " AND doc_type = ?"
                params.append(doc_type)
            if start_date:
                query += " AND date >= ?"
                params.append(start_date)
            if end_date:
                query += " AND date <= ?"
                params.append(end_date)
            if firm_prefix:
                query += " AND firm_prefix = ?"
                params.append(firm_prefix)

            query += " ORDER BY date, number"

            cursor.execute(query, params)
            rows = cursor.fetchall()

            return [dict(row) for row in rows]

    def get_documents_1c8(
        self,
        doc_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        firm_prefix: Optional[str] = None
    ) -> list[dict]:
        """
        Получение документов из 1С 8.

        Args:
            doc_type: Тип документа
            start_date: Дата начала
            end_date: Дата конца
            firm_prefix: Префикс фирмы

        Returns:
            Список документов
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            query = "SELECT * FROM documents_1c8 WHERE 1=1"
            params = []

            if doc_type:
                query += " AND doc_type = ?"
                params.append(doc_type)
            if start_date:
                query += " AND date >= ?"
                params.append(start_date)
            if end_date:
                query += " AND date <= ?"
                params.append(end_date)
            if firm_prefix:
                query += " AND firm_prefix = ?"
                params.append(firm_prefix)

            query += " ORDER BY date, number"

            cursor.execute(query, params)
            rows = cursor.fetchall()

            return [dict(row) for row in rows]

    def get_comparison_history(
        self,
        doc_type: Optional[str] = None,
        only_differences: bool = False
    ) -> list[dict]:
        """
        Получение истории сравнений.

        Args:
            doc_type: Тип документа
            only_differences: Только расхождения

        Returns:
            Список результатов сравнения
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            query = "SELECT * FROM comparison_results WHERE 1=1"
            params = []

            if doc_type:
                query += " AND doc_type = ?"
                params.append(doc_type)
            if only_differences:
                query += " AND has_difference = 1"
                params.append(1)

            query += " ORDER BY checked_at DESC"

            cursor.execute(query, params)
            rows = cursor.fetchall()

            return [dict(row) for row in rows]

    def clear_old_data(self, days: int = 30):
        """
        Очистка старых данных.

        Args:
            days: Количество дней для хранения
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Удаляем старые результаты сравнения
            cursor.execute("""
                DELETE FROM comparison_results 
                WHERE checked_at < datetime('now', ?)
            """, (f'-{days} days',))

            conn.commit()
            logger.info("Очищены старые данные сравнений (> %d дней)", days)


# Глобальный экземпляр базы данных
db = Database()
