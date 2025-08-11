from pydantic import BaseModel, Field


class PackageTypeBase(BaseModel):
    """Базовая схема типа посылки"""

    name: str = Field(description="Название типа посылки")


class PackageTypeCreate(PackageTypeBase):
    """Схема для создания типа посылки"""


class PackageTypeResponse(PackageTypeBase):
    """Схема ответа типа посылки"""
    id: int = Field(description="ID типа посылки")

    class Config:
        from_attributes = True
