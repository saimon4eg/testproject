import logging
import asyncio
from celery import shared_task
from celery_app.decorators import use_database, run_coroutine
from app.core.rabbitmq_service import RabbitMQService
from app.business.package_service import PackageService
from app.schemas import PackageCreate

logger = logging.getLogger(__name__)


@shared_task(bind=True, name='process_package_from_rabbitmq')
@run_coroutine
@use_database
async def process_package_from_rabbitmq_task(self, package_data: dict, session_id: str):
    """
    Задача для обработки посылки из RabbitMQ.
    Создает посылку в БД и сразу рассчитывает стоимость доставки.
    """
    try:
        logger.info(f"Обработка посылки из RabbitMQ для сессии {session_id}")

        # Валидируем данные посылки
        validated_package = PackageCreate(**package_data)

        # Создаем посылку в БД
        package = await PackageService().create_package(validated_package, session_id)

        # Сразу рассчитываем стоимость доставки
        delivery_cost = await PackageService().calculate_delivery_cost(package)
        if delivery_cost:
            package.delivery_cost_rub = delivery_cost

            from app.core.database import get_db_session_manager
            db_session_manager = get_db_session_manager()
            await db_session_manager.flush()

            logger.info(f"Посылка {package.id} создана и стоимость доставки рассчитана: {delivery_cost} руб.")
        else:
            logger.warning(f"Не удалось рассчитать стоимость доставки для посылки {package.id}")

        return {
            "status": "success",
            "package_id": package.id,
            "delivery_cost_rub": delivery_cost,
            "message": f"Посылка {package.id} успешно обработана"
        }

    except Exception as e:
        logger.error(f"Ошибка при обработке посылки из RabbitMQ: {e}")
        raise self.retry(countdown=30, max_retries=3)


@shared_task(name='start_rabbitmq_consumer')
@run_coroutine
async def start_rabbitmq_consumer_task():
    """
    Задача для запуска потребителя сообщений из RabbitMQ.
    Слушает очередь package_registration и обрабатывает сообщения.
    """
    try:
        logger.info("Запуск RabbitMQ потребителя для очереди package_registration")

        async def handle_package_message(message_data: dict, message):
            """Обработчик сообщений из очереди package_registration"""
            try:
                if message_data.get('type') == 'package_registration':
                    package_data = message_data.get('package_data', {})
                    session_id = message_data.get('session_id')

                    if not session_id:
                        logger.error("Отсутствует session_id в сообщении")
                        return

                    # Запускаем задачу обработки посылки асинхронно
                    process_package_from_rabbitmq_task.delay(package_data, session_id)
                    logger.info(f"Задача обработки посылки запущена для сессии {session_id}")
                else:
                    logger.warning(f"Неизвестный тип сообщения: {message_data.get('type')}")

            except Exception as e:
                logger.error(f"Ошибка при обработке сообщения из RabbitMQ: {e}")
                raise

        # Подключаемся к RabbitMQ и слушаем очередь
        await RabbitMQService().consume_messages('package_registration', handle_package_message)

        # Держим соединение активным
        logger.info("RabbitMQ потребитель активен и слушает сообщения...")
        while True:
            await asyncio.sleep(1)

    except Exception as e:
        logger.error(f"Ошибка в RabbitMQ потребителе: {e}")
        raise
