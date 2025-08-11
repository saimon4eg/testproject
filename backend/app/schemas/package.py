from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .package_type import PackageTypeResponse


class PackageBase(BaseModel):
    """Базовая схема посылки"""

    name: str = Field(description="Название посылки", min_length=1, max_length=255)
    weight: float = Field(description="Вес посылки в кг", gt=0)
    package_type_id: int = Field(description="ID типа посылки", gt=0)
    content_cost_usd: float = Field(description="Стоимость содержимого в долларах", ge=0)


class PackageCreate(PackageBase):
    """Схема для создания посылки"""


class PackageResponse(PackageBase):
    """Схема ответа посылки"""

    id: int = Field(description="ID посылки")
    delivery_cost_rub: Optional[float] = Field(None, description="Стоимость доставки в рублях")
    transport_company_id: Optional[int] = Field(None, description="ID транспортной компании")
    created_at: datetime = Field(description="Дата создания")
    updated_at: Optional[datetime] = Field(None, description="Дата обновления")
    package_type: Optional[PackageTypeResponse] = Field(None, description="Тип посылки")

    class Config:
        from_attributes = True


class PackageDetailResponse(PackageResponse):
    """Детальная схема ответа посылки"""


class PackageListResponse(BaseModel):
    """Схема ответа списка посылок с пагинацией"""

    items: list[PackageResponse] = Field(description="Список посылок")
    total: int = Field(description="Общее количество посылок")
    page: int = Field(description="Номер страницы")
    size: int = Field(description="Размер страницы")
    pages: int = Field(description="Общее количество страниц")


class PackageFilter(BaseModel):
    """Схема фильтров для списка посылок"""

    package_type_id: Optional[int] = Field(None, description="Фильтр по типу посылки")
    has_delivery_cost: Optional[bool] = Field(None, description="Фильтр по наличию рассчитанной стоимости доставки")


class TransportCompanyAssign(BaseModel):
    """Схема для привязки транспортной компании"""

    company_id: int = Field(description="ID транспортной компании", gt=0)
