"""
Полностью изолированная конфигурация тестов без предупреждений SQLAlchemy
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.asgi import app


@pytest_asyncio.fixture
async def async_client():
    """Асинхронный HTTP клиент для тестирования"""

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def sample_package_data():
    """Тестовые данные для создания посылки"""

    return {
        "name": "Тестовая посылка",
        "weight": 2.5,
        "package_type_id": 1,
        "content_cost_usd": 150.0
    }


@pytest.fixture
def async_package_data():
    """Тестовые данные для асинхронного создания посылки"""

    return {
        "name": "Асинхронная тестовая посылка",
        "weight": 3.0,
        "package_type_id": 1,
        "content_cost_usd": 200.0
    }


@pytest.fixture
def transport_company_data():
    """Тестовые данные для привязки транспортной компании"""

    return {"company_id": 42}
