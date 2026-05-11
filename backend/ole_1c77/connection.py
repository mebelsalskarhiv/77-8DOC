"""Подключение к 1С 7.7 через COM (адаптировано из dolg_json.py)."""

import logging
from contextlib import contextmanager

import pythoncom
import win32com.client

logger = logging.getLogger(__name__)

V7_PROGIDS = ("V77.Application", "V77S.Application", "V77M.Application", "V77L.Application")


def get_1c_progid():
    """Поиск доступного COM ProgID для 1С 7.7."""
    for progid in V7_PROGIDS:
        try:
            app = win32com.client.Dispatch(progid)
            _ = app is not None
            return progid
        except Exception:
            continue
    return None


def build_init_params(db_path, user="", pwd=""):
    """Формирование строки параметров для Initialize()."""
    db_path = (db_path or "").strip()
    user = (user or "").strip()
    pwd = (pwd or "").strip()

    parts = [f'/D"{db_path}"']
    if user:
        parts.append(f'/N"{user}"')
    if pwd:
        parts.append(f'/P"{pwd}"')
    return " ".join(parts)


def connect_1c(db_path, user="", pwd=""):
    """
    Подключение к базе 1С 7.7 через COM.
    Возвращает (app, progid).
    """
    progid = get_1c_progid()
    if not progid:
        raise RuntimeError(
            "Не найден COM ProgID 1С 7.7. Проверьте установку и регистрацию (1cv7s.exe /REGISTER)."
        )

    app = win32com.client.Dispatch(progid)
    params = build_init_params(db_path, user, pwd)

    # Маскируем пароль в логах
    masked = params.replace((pwd or "").strip(), "***") if pwd else params
    logger.info("Подключение к 1С 7.7: %s", masked)

    ok = app.Initialize(app.RMTrade, params, "NO_SPLASH_SHOW")
    if not ok:
        raise RuntimeError(
            "1С вернула отказ в Initialize(). Проверьте доступ к базе, логин/пароль."
        )

    logger.info("Успешное подключение через %s", progid)
    return app, progid


@contextmanager
def get_1c_connection(db_path, user="", pwd=""):
    """
    Контекстный менеджер для работы с 1С 7.7.

    Usage:
        with get_1c_connection(db_path, user, pwd) as v7:
            # работа с v7
            pass
    """
    pythoncom.CoInitialize()
    v7 = None
    try:
        v7, _ = connect_1c(db_path, user, pwd)
        yield v7
    finally:
        v7 = None
        pythoncom.CoUninitialize()


class Connection1C77:
    """
    Singleton для управления подключением к 1С 7.7.
    Держит одно соединение открытым для переиспользования.
    """
    _instance = None
    _v7 = None
    _db_path = None
    _user = None
    _pwd = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def connect(self, db_path, user="", pwd=""):
        """Подключиться к базе (или переиспользовать существующее соединение)."""
        if self._v7 is None or self._db_path != db_path:
            self.disconnect()
            # CoInitialize уже вызван в session()
            self._v7, _ = connect_1c(db_path, user, pwd)
            self._db_path = db_path
            self._user = user
            self._pwd = pwd
        return self._v7

    def disconnect(self):
        """Закрыть соединение."""
        if self._v7 is not None:
            self._v7 = None
            self._db_path = None

    def get_connection(self):
        """Получить текущее соединение (или None если не подключено)."""
        return self._v7

    @contextmanager
    def session(self, db_path, user="", pwd=""):
        """
        Контекстный менеджер для работы с соединением.

        Usage:
            conn = Connection1C77()
            with conn.session(db_path, user, pwd) as v7:
                # работа с v7
                pass
        """
        # Инициализируем COM для текущего потока
        pythoncom.CoInitialize()
        try:
            v7 = self.connect(db_path, user, pwd)
            yield v7
        except Exception:
            # При ошибке закрываем соединение для переподключения
            self.disconnect()
            raise
        finally:
            pythoncom.CoUninitialize()
