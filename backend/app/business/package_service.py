import logging
from typing import Optional, Tuple, Sequence

from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.business.currency_service import CurrencyService
from app.core import get_db_session_manager
from app.models import Package, PackageType
from app.schemas import PackageCreate, PackageFilter
from app.utils import Singleton

logger = logging.getLogger(__name__)


class PackageService(metaclass=Singleton):
    """Сервис для работы с посылками"""

    @staticmethod
    async def create_package(package_data: PackageCreate, session_id: str) -> Package:
        """Создает новую посылку"""
        db_session_manager = get_db_session_manager()
        session = db_session_manager.session

        # Проверяем существование типа посылки
        package_type = await session.get(PackageType, package_data.package_type_id)
        if not package_type:
            raise ValueError(f"Тип посылки с ID {package_data.package_type_id} не найден")

        # Создаем посылку
        package = Package(
            name=package_data.name,
            weight=package_data.weight,
            package_type_id=package_data.package_type_id,
            content_cost_usd=package_data.content_cost_usd,
            session_id=session_id
        )

        session.add(package)
        await db_session_manager.flush()

        await session.refresh(package)

        logger.info(f"Создана посылка ID {package.id} для сессии {session_id}")
        return package

    @staticmethod
    async def get_package_types() -> Sequence[PackageType]:
        """Получает все типы посылок"""
        db_session_manager = get_db_session_manager()
        session = db_session_manager.session

        result = (await session.scalars(
            select(PackageType).order_by(PackageType.id)
        )).all()

        return result

    @staticmethod
    async def get_user_packages(
        session_id: str,
        page: int = 1,
        size: int = 20,
        filters: Optional[PackageFilter] = None
    ) -> Tuple[Sequence[Package], int]:
        """Получает список посылок пользователя с пагинацией и фильтрами"""

        def _filter_query(sa_query, _filters):
            if _filters.package_type_id:
                sa_query = sa_query.where(Package.package_type_id == _filters.package_type_id)

            if _filters.has_delivery_cost is not None:
                if _filters.has_delivery_cost:
                    sa_query = sa_query.where(Package.delivery_cost_rub.isnot(None))
                else:
                    sa_query = sa_query.where(Package.delivery_cost_rub.is_(None))

            return sa_query

        db_session_manager = get_db_session_manager()
        session = db_session_manager.session

        query = select(Package).options(selectinload(Package.package_type)).where(
            Package.session_id == session_id
        )
        query = _filter_query(query, filters)

        # Запрос для подсчета общего количества
        count_query = select(func.count(Package.id)).where(Package.session_id == session_id)
        count_query = _filter_query(count_query, filters)

        total_result = await session.execute(count_query)
        total = total_result.scalar() or 0

        # Пагинация
        offset = (page - 1) * size
        query = query.order_by(Package.created_at.desc()).offset(offset).limit(size)

        packages = (await session.scalars(
            query
        )).all()

        return packages, total

    @staticmethod
    async def get_package_by_id(package_id: int, session_id: str) -> Optional[Package]:
        """Получает посылку по ID для конкретной сессии пользователя"""

        db_session_manager = get_db_session_manager()
        session = db_session_manager.session

        return (await session.scalars(
            select(Package).where(
                Package.id == package_id,
                Package.session_id == session_id
            ).options(
                selectinload(Package.package_type)
            )
        )).one_or_none()

    @staticmethod
    async def calculate_delivery_cost(package: Package) -> Optional[float]:
        """
        Рассчитывает стоимость доставки для посылки
        Формула: (вес в кг * 0.5 + стоимость содержимого в долларах * 0.01) * курс доллара к рублю
        """
        usd_rate = await CurrencyService().get_usd_to_rub_rate()
        if not usd_rate:
            logger.error(f"Не удалось получить курс валют для расчета доставки посылки {package.id}")
            return None

        delivery_cost = (package.weight * 0.5 + package.content_cost_usd * 0.01) * usd_rate
        logger.info(f"Рассчитана стоимость доставки для посылки {package.id}: {delivery_cost:.2f} руб.")

        return round(delivery_cost, 2)

    async def calculate_delivery_costs(self) -> int:
        """
        Обновляет стоимость доставки для всех посылок без рассчитанной стоимости.
        Возвращает количество обработанных посылок.
        """

        db_session_manager = get_db_session_manager()
        session = db_session_manager.session

        packages = (await session.scalars(
            select(Package).where(Package.delivery_cost_rub.is_(None))
        )).all()

        if not packages:
            logger.info("Нет посылок для обновления стоимости доставки")
            return 0

        usd_rate = await CurrencyService().get_usd_to_rub_rate()
        if not usd_rate:
            logger.error("Не удалось получить курс валют для обновления стоимости доставки")
            return 0

        updated_count = 0
        for package in packages:
            delivery_cost = await self.calculate_delivery_cost(package)
            if delivery_cost:
                package.delivery_cost_rub = delivery_cost
                updated_count += 1

        await db_session_manager.flush()
        logger.info(f"Обновлена стоимость доставки для {updated_count} посылок")

        return updated_count

    @staticmethod
    async def assign_transport_company(package_id: int, session_id: str, company_id: int) -> bool:
        """
        Привязывает транспортную компанию к посылке.
        Обеспечивает гарантию, что первая обратившаяся компания закрепит посылку используя SELECT FOR UPDATE.
        """
        db_session_manager = get_db_session_manager()
        session = db_session_manager.session

        try:
            package = (await session.scalars(
                select(Package)
                .where(
                    Package.id == package_id,
                    Package.session_id == session_id
                )
                .with_for_update(nowait=True)
            )).one_or_none()

            if not package:
                logger.warning(f"Посылка {package_id} не найдена для сессии {session_id}")
                return False

            if package.transport_company_id is not None:
                logger.info(f"Посылка {package_id} уже привязана к компании {package.transport_company_id}")
                return False

            package.transport_company_id = company_id
            await db_session_manager.flush()

            logger.info(f"Посылка {package_id} успешно привязана к транспортной компании {company_id}")
            return True

        except Exception as e:
            logger.error(f"Ошибка при привязке транспортной компании к посылке {package_id}: {e}")
            return False


# Глобальный экземпляр сервиса посылок
package_service = PackageService()
