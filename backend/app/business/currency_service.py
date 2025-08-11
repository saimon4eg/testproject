import logging
import httpx
from typing import Optional
from app.core.cache import Cache
from app.utils import Singleton

logger = logging.getLogger(__name__)


class CurrencyService(metaclass=Singleton):
    """Сервис для работы с курсами валют"""

    CBR_API_URL = "https://www.cbr-xml-daily.ru/daily_json.js"
    CACHE_KEY = "usd_to_rub_rate"
    CACHE_EXPIRE_SECONDS = 3600  # 1 час

    async def get_usd_to_rub_rate(self) -> Optional[float]:
        """Получает курс доллара к рублю."""

        # Пытаемся получить из кэша
        cached_rate = await Cache().get(self.CACHE_KEY)
        if cached_rate:
            logger.debug(f"Получен курс из кэша: {cached_rate}")
            return float(cached_rate)

        # Если в кэше нет, запрашиваем из API
        rate = await self._fetch_rate_from_api()
        if rate:
            # Сохраняем в кэш
            await Cache().set(self.CACHE_KEY, rate, self.CACHE_EXPIRE_SECONDS)
            logger.info(f"Получен новый курс из API: {rate}")
            return rate

        logger.error("Не удалось получить курс валют")
        return None

    async def _fetch_rate_from_api(self) -> Optional[float]:
        """Получает курс из API ЦБ РФ"""

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.CBR_API_URL)
                response.raise_for_status()

                data = response.json()
                usd_data = data.get("Valute", {}).get("USD")

                if usd_data and "Value" in usd_data:
                    rate = float(usd_data["Value"])
                    logger.info(f"Получен курс USD из API ЦБ: {rate}")
                    return rate

                logger.error("Не найдены данные о курсе USD в ответе API")
                return None

        except httpx.RequestError as e:
            logger.error(f"Ошибка запроса к API ЦБ: {e}")
            return None
        except (ValueError, KeyError) as e:
            logger.error(f"Ошибка парсинга ответа API ЦБ: {e}")
            return None
        except Exception as e:
            logger.error(f"Неожиданная ошибка при получении курса: {e}")
            return None
