import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class SessionMiddleware(BaseHTTPMiddleware):
    """Middleware для работы с сессиями пользователей"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        # Получаем session_id из cookies или создаем новый
        session_id = request.cookies.get("session_id")
        
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Добавляем session_id в state запроса
        request.state.session_id = session_id
        
        # Выполняем запрос
        response = await call_next(request)
        
        # Устанавливаем cookie с session_id если его не было
        if not request.cookies.get("session_id"):
            response.set_cookie(
                key="session_id",
                value=session_id,
                max_age=30 * 24 * 60 * 60,  # 30 дней
                httponly=True,
                samesite="lax"
            )
        
        return response
