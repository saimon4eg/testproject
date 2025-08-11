import logging
from celery import shared_task
from celery_app.decorators import use_database, run_coroutine
from app.business.package_service import PackageService

logger = logging.getLogger(__name__)


@shared_task(bind=True, name='calculate_delivery_costs')
@run_coroutine
@use_database
async def calculate_delivery_costs_task(self):
    """
    Периодическая задача для расчета стоимости доставки всех необработанных посылок.
    Запускается каждые 5 минут.
    """
    try:
        logger.info("Запуск задачи расчета стоимости доставки")

        updated_count = await PackageService().calculate_delivery_costs()

        if updated_count > 0:
            logger.info(f"Обновлена стоимость доставки для {updated_count} посылок")
        else:
            logger.info("Нет посылок для обновления стоимости доставки")

        return {
            "status": "success",
            "updated_packages": updated_count,
            "message": f"Обработано посылок: {updated_count}"
        }

    except Exception as e:
        logger.error(f"Ошибка в задаче расчета стоимости доставки: {e}")
        # Повторяем задачу через 1 минуту при ошибке (максимум 3 попытки)
        raise self.retry(countdown=60, max_retries=3)
