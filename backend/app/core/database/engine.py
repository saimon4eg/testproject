from functools import lru_cache
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.settings import DATABASE_URL

@lru_cache()
def get_engine():
    """Создает и кэширует асинхронный движок SQLAlchemy"""
    return create_async_engine(DATABASE_URL)

def get_session() -> AsyncSession:
    """Создает новую асинхронную сессию"""
    engine = get_engine()
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False
    )
    return async_session()
