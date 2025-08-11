from celery import Celery
from app.settings import REDIS_URL

# Создаем отдельный экземпляр Celery для использования в backend
# Этот экземпляр используется только для отправки задач, не для их выполнения
backend_celery_app = Celery('backend_client')

backend_celery_app.conf.update(
    broker_url=REDIS_URL,
    result_backend=REDIS_URL,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    # Добавляем маршрутизацию задач в правильную очередь
    task_routes={
        'manual_calculate_delivery_costs': {'queue': 'main.tasks'},
        'calculate_delivery_costs': {'queue': 'main.tasks'},
    },
    task_default_queue='main.tasks',
)
