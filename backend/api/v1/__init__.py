"""API v1 package."""

from .documents_77 import router as documents_77_router
from .documents_1c8 import router as documents_1c8_router
from .comparison_api import router as comparison_router
from .health import router as health_router

__all__ = ["documents_77_router", "documents_1c8_router", "comparison_router", "health_router"]
