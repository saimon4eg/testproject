import logging
from functools import wraps

from app.core import get_db_session_manager

logger = logging.getLogger(__name__)


def use_database(func):
    """
    Декоратор для управления подключением к базе данных в задачах Celery.
    Повторяет логику DatabaseMiddleware для обеспечения корректной работы с БД.
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        db_session_manager = get_db_session_manager()

        try:
            logger.debug('Создана сессия БД для Celery задачи')

            # Выполняем функцию задачи
            result = await func(*args, **kwargs)

            # При успешном выполнении коммитим транзакцию
            await db_session_manager.commit()
            logger.debug('Транзакция подтверждена')

            return result

        except Exception as e:
            logger.error(f'Ошибка в Celery задаче: {e}')
            # При ошибке откатываем транзакцию
            await db_session_manager.rollback()
            raise

        finally:
            # Всегда закрываем сессию
            await db_session_manager.close()
            logger.debug('Сессия БД закрыта')

    return wrapper
