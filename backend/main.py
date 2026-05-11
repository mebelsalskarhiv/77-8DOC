"""Главное FastAPI приложение."""

import logging
import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from backend.api.v1 import documents_77_router, documents_1c8_router, comparison_router, health_router
from backend.config import settings

# Настройка логирования
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(log_dir / "app.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Создание приложения
app = FastAPI(
    title="77-8DOC API",
    description="API для работы с документами 1С 7.7 и 1С 8",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(health_router)
app.include_router(documents_77_router)
app.include_router(documents_1c8_router)
app.include_router(comparison_router)

# Статические файлы и шаблоны
static_path = Path(__file__).parent.parent / "frontend" / "static"
templates_path = Path(__file__).parent.parent / "frontend" / "templates"

if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

templates = Jinja2Templates(directory=str(templates_path))


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Главная страница."""
    return templates.TemplateResponse(request=request, name="index.html")


@app.on_event("startup")
async def startup_event():
    """Событие при запуске приложения."""
    logger.info("Запуск приложения 77-8DOC")
    logger.info("База 1С 7.7: %s", settings.db_path_77)


@app.on_event("shutdown")
async def shutdown_event():
    """Событие при остановке приложения."""
    logger.info("Остановка приложения 77-8DOC")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
