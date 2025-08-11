from celery import Celery
from kombu import Queue
from celery.schedules import crontab

from app.settings import REDIS_URL
from app.configure import configure

configure()

app = Celery('main_app', include=[
    'celery_app.tasks'
])

app.conf.update(
    # Настройки брокера сообщений (Redis)
    broker_url=REDIS_URL,
    broker_transport_options={
        'fanout_prefix': True,
        'fanout_patterns': True,
        'visibility_timeout': 3600,
    },

    # Настройки хранения результатов
    result_backend=REDIS_URL,
    result_expires=3600,

    # Настройки отслеживания задач
    task_track_started=True,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    worker_send_task_events=True,
    task_send_sent_event=True,

    # Определение очередей для задач работы с БД
    task_queues=(
        Queue('main.tasks', routing_key='main.tasks'),
    ),

    # Маршрутизация задач по очередям
    task_routes={
        'celery_app.tasks.*': {'queue': 'main.tasks', 'routing_key': 'main.tasks'},
        'calculate_delivery_costs': {'queue': 'main.tasks', 'routing_key': 'main.tasks'},
    },

    beat_scheduler='redbeat.RedBeatScheduler',
    redbeat_redis_url=REDIS_URL,
    redbeat_key_prefix='redbeat:',

    # Расписание для периодических задач (Celery Beat)
    beat_schedule={
        'calculate-delivery-costs-every-5-minutes': {
            'task': 'calculate_delivery_costs',
            'schedule': crontab(minute='*/5'),  # Каждые 5 минут
        },
    },

    # Настройки производительности
    worker_max_memory_per_child=1024*100,  # 100MB на процесс
    task_time_limit=1200,                  # Лимит времени выполнения (20 минут)

    # Настройки времени и локации
    timezone='UTC',
    enable_utc=True,
)
