from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import ORMBaseModel
from .mixins import IntIdMixin


class PackageType(ORMBaseModel, IntIdMixin):
    """Модель типа посылки"""
    __tablename__ = 'package_types'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)

    # relationship
    packages = relationship("Package", back_populates="package_type")

    def __repr__(self):
        return f"<PackageType(id={self.id}, name='{self.name}')>"
