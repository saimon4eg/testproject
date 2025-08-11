import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Request, Query, Depends
from fastapi.responses import JSONResponse

from app.core.rabbitmq_service import RabbitMQService
from app.schemas import (
    PackageTypeResponse,
    PackageCreate,
    PackageResponse,
    PackageDetailResponse,
    PackageListResponse,
    PackageFilter,
    TransportCompanyAssign
)
from app.business.package_service import PackageService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["packages"])


def get_package_filter(
    package_type_id: Optional[int] = Query(None, description="Фильтр по типу посылки"),
    has_delivery_cost: Optional[bool] = Query(None, description="Фильтр по наличию рассчитанной стоимости доставки")
) -> PackageFilter:
    """Создает объект фильтра из query параметров"""
    return PackageFilter(package_type_id=package_type_id, has_delivery_cost=has_delivery_cost)


@router.post("/packages/", response_model=PackageResponse, summary="Зарегистрировать посылку")
async def create_package(
    package_data: PackageCreate,
    request: Request
):
    """Регистрирует новую посылку."""
    try:
        session_id = request.state.session_id
        package = await PackageService().create_package(package_data, session_id)

        logger.info(f"Создана посылка {package.id} для сессии {session_id}")

        return PackageResponse(
            id=package.id,
            name=package.name,
            weight=package.weight,
            package_type_id=package.package_type_id,
            content_cost_usd=package.content_cost_usd,
            delivery_cost_rub=package.delivery_cost_rub,
            transport_company_id=package.transport_company_id,
            created_at=package.created_at,
            updated_at=package.updated_at,
            package_type=None
        )

    except ValueError as e:
        logger.warning(f"Ошибка валидации при создании посылки: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Неожиданная ошибка при создании посылки: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.post("/packages/async", summary="Зарегистрировать посылку асинхронно")
async def create_package_async(
    package_data: PackageCreate,
    request: Request
):
    """Регистрирует новую посылку асинхронно через RabbitMQ."""
    try:
        session_id = request.state.session_id

        # Отправляем сообщение в RabbitMQ
        rabbitmq_service = RabbitMQService()

        message = {
            "type": "package_registration",
            "package_data": package_data.model_dump(),
            "session_id": session_id
        }

        await rabbitmq_service.publish_message(
            queue_name="package_registration",
            message=message
        )

        logger.info(f"Отправлено сообщение о регистрации посылки в RabbitMQ для сессии {session_id}")

        return JSONResponse(
            content={
                "message": "Посылка поставлена в очередь для асинхронной обработки",
                "session_id": session_id,
                "status": "queued"
            },
            status_code=202
        )

    except ValueError as e:
        logger.warning(f"Ошибка валидации при асинхронном создании посылки: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка при отправке в RabbitMQ: {e}")
        raise HTTPException(status_code=500, detail="Не удалось поставить посылку в очередь")


@router.get("/package-types/", response_model=list[PackageTypeResponse], summary="Получить все типы посылок")
async def get_package_types():
    """Возвращает все доступные типы посылок с их ID."""
    try:
        package_types = await PackageService().get_package_types()
        return [
            PackageTypeResponse(id=pt.id, name=pt.name)
            for pt in package_types
        ]
    except Exception as e:
        logger.error(f"Ошибка при получении типов посылок: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.get("/packages/", response_model=PackageListResponse, summary="Получить список своих посылок")
async def get_packages(
    request: Request,
    page: int = Query(1, ge=1, description="Номер страницы"),
    size: int = Query(20, ge=1, le=100, description="Размер страницы"),
    filters: PackageFilter = Depends(get_package_filter)
):
    """Возвращает список посылок текущего пользователя с пагинацией и фильтрацией."""
    try:
        session_id = request.state.session_id
        packages, total = await PackageService().get_user_packages(
            session_id, page, size, filters
        )

        # Рассчитываем общее количество страниц
        pages = (total + size - 1) // size if total > 0 else 0

        package_responses = []
        for package in packages:
            package_type_response = None
            if package.package_type:
                package_type_response = PackageTypeResponse(
                    id=package.package_type.id,
                    name=package.package_type.name
                )

            package_responses.append(PackageResponse(
                id=package.id,
                name=package.name,
                weight=package.weight,
                package_type_id=package.package_type_id,
                content_cost_usd=package.content_cost_usd,
                delivery_cost_rub=package.delivery_cost_rub,
                transport_company_id=package.transport_company_id,
                created_at=package.created_at,
                updated_at=package.updated_at,
                package_type=package_type_response
            ))

        return PackageListResponse(
            items=package_responses,
            total=total,
            page=page,
            size=size,
            pages=pages
        )

    except Exception as e:
        logger.error(f"Ошибка при получении списка посылок: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.get("/packages/{package_id}", response_model=PackageDetailResponse, summary="Получить данные о посылке")
async def get_package(package_id: int, request: Request):
    """Возвращает подробные данные о посылке по её ID."""

    try:
        session_id = request.state.session_id
        package = await PackageService().get_package_by_id(package_id, session_id)

        if not package:
            raise HTTPException(status_code=404, detail="Посылка не найдена")

        package_type_response = None
        if package.package_type:
            package_type_response = PackageTypeResponse(
                id=package.package_type.id,
                name=package.package_type.name
            )

        return PackageDetailResponse(
            id=package.id,
            name=package.name,
            weight=package.weight,
            package_type_id=package.package_type_id,
            content_cost_usd=package.content_cost_usd,
            delivery_cost_rub=package.delivery_cost_rub,
            transport_company_id=package.transport_company_id,
            created_at=package.created_at,
            updated_at=package.updated_at,
            package_type=package_type_response
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при получении посылки {package_id}: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.post("/packages/{package_id}/assign-transport", summary="Привязать транспортную компанию")
async def assign_transport_company(
    package_id: int,
    company_data: TransportCompanyAssign,
    request: Request
):
    """Привязывает транспортную компанию к посылке."""

    try:
        session_id = request.state.session_id
        success = await PackageService().assign_transport_company(
            package_id, session_id, company_data.company_id
        )

        if not success:
            package = await PackageService().get_package_by_id(package_id, session_id)
            if not package:
                raise HTTPException(status_code=404, detail="Посылка не найдена")
            if package.transport_company_id:
                raise HTTPException(
                    status_code=409,
                    detail=f"Посылка уже привязана к транспортной компании {package.transport_company_id}"
                )

            raise HTTPException(status_code=400, detail="Не удалось привязать транспортную компанию")

        return JSONResponse(
            content={"message": f"Посылка успешно привязана к транспортной компании {company_data.company_id}"},
            status_code=200
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при привязке транспортной компании к посылке {package_id}: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")
