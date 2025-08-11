import logging
from contextvars import ContextVar
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from .engine import get_session

logger = logging.getLogger(__name__)

# Контекстная переменная для хранения сессии БД для каждого пользователя/запроса
_db_session: ContextVar[Optional[AsyncSession]] = ContextVar('db_session', default=None)


class DBSessionManager:
    """Менеджер для управления сессией базы данных"""

    def __init__(self):
        self._session: Optional[AsyncSession] = None

    @property
    def session(self) -> AsyncSession:
        """Получает существующую сессию или создает новую"""

        session = _db_session.get()
        if session is None:
            session = get_session()
            _db_session.set(session)
            logger.debug("Создана новая сессия БД")
        return session

    async def commit(self):
        """Подтверждает транзакцию и сохраняет изменения в БД"""
        session = _db_session.get()
        if session:
            try:
                await session.flush()  # Отправляем изменения в БД
                await session.commit()  # Подтверждаем транзакцию
                logger.debug("Транзакция подтверждена")
            except Exception as e:
                logger.error(f"Ошибка при коммите: {e}")
                await self.rollback()
                raise

    @staticmethod
    async def rollback():
        """Откатывает транзакцию"""
        session = _db_session.get()
        if session:
            try:
                await session.rollback()
                logger.debug("Транзакция откачена")
            except Exception as e:
                logger.error(f"Ошибка при откате: {e}")

    @staticmethod
    async def close():
        """Закрывает сессию"""
        session = _db_session.get()
        if session:
            try:
                await session.close()
                _db_session.set(None)
                logger.debug("Сессия БД закрыта")
            except Exception as e:
                logger.error(f"Ошибка при закрытии сессии: {e}")

    @staticmethod
    async def flush():
        """Отправляет изменения в БД без коммита"""
        session = _db_session.get()
        if session:
            await session.flush()
            logger.debug("Выполнен flush")


def get_db_session_manager() -> DBSessionManager:
    """Возвращает экземпляр менеджера базы данных"""
    return DBSessionManager()
