"""Конфигурация приложения."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения."""

    # 1С 7.7
    db_path_77: str = ""
    db_user_77: str = ""
    db_password_77: str = ""

    # 1С 8 OData
    odoo_1c8_url: str = ""
    odoo_1c8_user: str = ""
    odoo_1c8_password: str = ""
    odoo_1c8_published_url: str = ""

    # Сервер
    host: str = "0.0.0.0"
    port: int = 8100

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
