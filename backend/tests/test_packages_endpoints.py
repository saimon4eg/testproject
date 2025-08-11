import pytest


class TestHealthcheckEndpoint:
    """Тесты для healthcheck эндпоинта"""

    @pytest.mark.asyncio
    async def test_healthcheck_success(self, async_client):
        """Тест успешного healthcheck"""
        response = await async_client.get("/backend/api/healthcheck")
        assert response.status_code == 200


class TestPackageTypesEndpoint:
    """Тесты для эндпоинта типов посылок"""

    @pytest.mark.asyncio
    async def test_get_package_types_success(self, async_client):
        """Тест получения всех типов посылок"""

        response = await async_client.get("/backend/api/package-types/")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3  # Должно быть минимум 3 типа из миграций

        # Проверяем структуру первого типа
        if data:
            package_type = data[0]
            assert "id" in package_type
            assert "name" in package_type
            assert isinstance(package_type["id"], int)
            assert isinstance(package_type["name"], str)


class TestPackagesEndpoint:
    """Тесты для эндпоинтов посылок"""

    @pytest.mark.asyncio
    async def test_create_package_sync_success(self, async_client, sample_package_data):
        """Тест синхронного создания посылки"""

        response = await async_client.post(
            "/backend/api/packages/",
            json=sample_package_data
        )
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == sample_package_data["name"]
        assert data["weight"] == sample_package_data["weight"]
        assert data["package_type_id"] == sample_package_data["package_type_id"]
        assert data["content_cost_usd"] == sample_package_data["content_cost_usd"]
        assert "id" in data
        assert isinstance(data["id"], int)
        assert "created_at" in data
        assert "updated_at" in data

    @pytest.mark.asyncio
    async def test_create_package_async_success(self, async_client, async_package_data):
        """Тест асинхронного создания посылки"""

        response = await async_client.post(
            "/backend/api/packages/async",
            json=async_package_data
        )
        assert response.status_code == 202

        data = response.json()
        assert "message" in data
        assert "session_id" in data
        assert "status" in data
        assert data["status"] == "queued"

    @pytest.mark.asyncio
    async def test_get_packages_list_success(self, async_client):
        """Тест получения списка посылок"""

        response = await async_client.get("/backend/api/packages/")
        assert response.status_code == 200

        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert "pages" in data
        assert isinstance(data["items"], list)
        assert isinstance(data["total"], int)

    @pytest.mark.asyncio
    async def test_get_packages_list_with_filters(self, async_client):
        """Тест получения списка посылок с фильтрами"""

        response = await async_client.get(
            "/backend/api/packages/?page=1&size=10&package_type_id=1"
        )
        assert response.status_code == 200

        data = response.json()
        assert "items" in data
        assert data["page"] == 1
        assert data["size"] == 10

    @pytest.mark.asyncio
    async def test_get_packages_list_invalid_page(self, async_client):
        """Тест получения списка посылок с невалидной страницей"""

        response = await async_client.get("/backend/api/packages/?page=0")
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_get_package_by_id_not_found(self, async_client):
        """Тест получения несуществующей посылки"""
        response = await async_client.get("/backend/api/packages/99999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_assign_transport_company_not_found(self, async_client, transport_company_data):
        """Тест привязки транспортной компании к несуществующей посылке"""

        response = await async_client.post(
            "/backend/api/packages/99999/assign-transport",
            json=transport_company_data
        )
        assert response.status_code == 404
