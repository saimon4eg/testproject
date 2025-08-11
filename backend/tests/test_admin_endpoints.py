import pytest


class TestAdminEndpoints:
    """Тесты для административных эндпоинтов"""

    @pytest.mark.asyncio
    async def test_manual_calculate_delivery_costs_success(self, async_client):
        """Тест ручного запуска расчета стоимости доставки"""
        response = await async_client.post("/backend/api/admin/calculate-delivery-costs")
        assert response.status_code == 202

        data = response.json()
        assert "message" in data
        assert "task_id" in data
        assert "status" in data
        assert data["status"] == "pending"
        assert isinstance(data["task_id"], str)
        assert len(data["task_id"]) > 0

    @pytest.mark.asyncio
    async def test_get_task_status_success(self, async_client):
        """Тест получения статуса задачи"""
        # 1. Сначала запускаем задачу
        create_task_response = await async_client.post("/backend/api/admin/calculate-delivery-costs")
        assert create_task_response.status_code == 202

        task_data = create_task_response.json()
        task_id = task_data["task_id"]

        # 2. Получаем статус задачи
        status_response = await async_client.get(f"/backend/api/admin/task/{task_id}")
        assert status_response.status_code == 200

        status_data = status_response.json()
        assert "task_id" in status_data
        assert "status" in status_data
        assert status_data["task_id"] == task_id
        assert status_data["status"] in ["PENDING", "SUCCESS", "FAILURE", "RETRY"]

    @pytest.mark.asyncio
    async def test_get_task_status_invalid_task_id(self, async_client):
        """Тест получения статуса несуществующей задачи"""
        fake_task_id = "invalid-task-id-12345"
        response = await async_client.get(f"/backend/api/admin/task/{fake_task_id}")
        assert response.status_code == 200  # Celery возвращает PENDING для несуществующих задач

        data = response.json()
        assert data["status"] == "PENDING"

    @pytest.mark.asyncio
    async def test_concurrent_assignment_not_found(self, async_client):
        """Тест конкурентной привязки для несуществующей посылки"""
        response = await async_client.post(
            "/backend/api/admin/test-concurrent-assignment/99999"
        )
        assert response.status_code == 404
