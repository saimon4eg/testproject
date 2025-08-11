import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.database import get_db_session_manager

logger = logging.getLogger(__name__)

class DatabaseMiddleware(BaseHTTPMiddleware):
    """Middleware для управления сессиями базы данных"""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        db_session_manager = get_db_session_manager()

        try:
            response = await call_next(request)

            if 200 <= response.status_code < 300:
                await db_session_manager.commit()
            else:
                await db_session_manager.rollback()

        except Exception as e:
            logger.error(f'Исключение в обработке запроса: {e}')
            await db_session_manager.rollback()
            raise
        finally:
            # Всегда закрываем сессию
            await db_session_manager.close()

        return response