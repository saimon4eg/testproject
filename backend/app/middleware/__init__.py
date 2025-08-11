from starlette.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.errors import ServerErrorMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from app.settings import DEBUG_MODE
from .database import DatabaseMiddleware
from .session import SessionMiddleware


middleware = [
    Middleware(ServerErrorMiddleware, debug=DEBUG_MODE),
    Middleware(ProxyHeadersMiddleware, trusted_hosts='*'),
    Middleware(SessionMiddleware),
    Middleware(DatabaseMiddleware),
]

if DEBUG_MODE:
    cors_settings = {
        'allow_origins': ['*'],
        'allow_credentials': ['*'],
        'allow_methods': ['*'],
        'allow_headers': ['*'],
    }
    middleware.insert(0, Middleware(CORSMiddleware, **cors_settings))
