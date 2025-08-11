import logging
import asyncio
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from app.core.celery_client import backend_celery_app
from app.business.package_service import PackageService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["admin"])


@router.post("/admin/calculate-delivery-costs", summary="Ручной запуск расчета стоимости доставки")
async def manual_calculate_delivery_costs():
    """
    Ручной запуск расчета стоимости доставки для всех необработанных посылок.
    Используется для отладки и тестирования.
    """
    try:
        # Запускаем задачу асинхронно через backend Celery client
        task = backend_celery_app.send_task('calculate_delivery_costs_task')

        logger.info(f"Запущена ручная задача расчета стоимости доставки, ID: {task.id}")

        return JSONResponse(
            content={
                "message": "Задача расчета стоимости доставки запущена",
                "task_id": task.id,
                "status": "pending"
            },
            status_code=202
        )

    except Exception as e:
        logger.error(f"Ошибка при запуске ручной задачи расчета стоимости доставки: {e}")
        raise HTTPException(status_code=500, detail="Не удалось запустить задачу")


@router.get("/admin/task/{task_id}", summary="Получить статус задачи")
async def get_task_status(task_id: str):
    """Получает статус выполнения задачи по её ID."""

    try:
        task_result = backend_celery_app.AsyncResult(task_id)

        if task_result.state == 'PENDING':
            response = {
                'task_id': task_id,
                'status': task_result.state,
                'message': 'Задача ожидает выполнения'
            }
        elif task_result.state == 'SUCCESS':
            response = {
                'task_id': task_id,
                'status': task_result.state,
                'result': task_result.result
            }
        else:
            response = {
                'task_id': task_id,
                'status': task_result.state,
                'error': str(task_result.info)
            }

        return response

    except Exception as e:
        logger.error(f"Ошибка при получении статуса задачи {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Не удалось получить статус задачи")
