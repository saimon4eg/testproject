from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import ORMBaseModel
from .mixins import IntIdMixin


class Package(ORMBaseModel, IntIdMixin):
    """Модель посылки"""

    __tablename__ = 'packages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    weight = Column(Float, nullable=False)  # вес в кг
    package_type_id = Column(Integer, ForeignKey('package_types.id'), nullable=False)
    content_cost_usd = Column(Float, nullable=False)  # стоимость содержимого в долларах
    delivery_cost_rub = Column(Float, nullable=True)  # стоимость доставки в рублях
    session_id = Column(String(255), nullable=False)  # ID сессии пользователя
    transport_company_id = Column(Integer, nullable=True)  # ID транспортной компании
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # relationship
    package_type = relationship("PackageType", back_populates="packages")
    
    def __repr__(self):
        return f"<Package(id={self.id}, name='{self.name}', weight={self.weight})>"
