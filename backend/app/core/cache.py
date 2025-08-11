import json
import logging
from typing import Optional, Any
from redis.asyncio import Redis
from app.settings import REDIS_URL
from app.utils import Singleton

logger = logging.getLogger(__name__)


class Cache(metaclass=Singleton):
    """Класс для работы с кэшом Redis"""
    
    def __init__(self):
        self._redis: Optional[Redis] = None
    
    async def _get_redis(self) -> Redis:
        """Получает подключение к Redis"""

        if self._redis is None:
            self._redis = Redis.from_url(REDIS_URL, decode_responses=True)
        return self._redis
    
    async def get(self, key: str) -> Optional[Any]:
        """Получает значение из кэша по ключу"""

        try:
            redis = await self._get_redis()
            value = await redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Ошибка при получении данных из кэша для ключа {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, expire_seconds: Optional[int] = None) -> bool:
        """Сохраняет значение в кэш"""

        try:
            redis = await self._get_redis()
            json_value = json.dumps(value, ensure_ascii=False)
            
            if expire_seconds:
                await redis.setex(key, expire_seconds, json_value)
            else:
                await redis.set(key, json_value)
            
            logger.debug(f"Данные сохранены в кэш для ключа {key}")
            return True
        except Exception as e:
            logger.error(f"Ошибка при сохранении данных в кэш для ключа {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Удаляет значение из кэша"""

        try:
            redis = await self._get_redis()
            result = await redis.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Ошибка при удалении данных из кэша для ключа {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Проверяет существование ключа в кэше"""

        try:
            redis = await self._get_redis()
            result = await redis.exists(key)
            return result > 0
        except Exception as e:
            logger.error(f"Ошибка при проверке существования ключа {key}: {e}")
            return False
    
    async def close(self):

        """Закрывает подключение к Redis"""
        if self._redis:
            await self._redis.close()
