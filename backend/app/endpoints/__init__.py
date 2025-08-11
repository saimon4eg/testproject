from fastapi import APIRouter

from .healthcheck_endpoint import router as healthcheck_router
from .packages_endpoint import router as packages_router
from .admin_endpoint import router as admin_router

router = APIRouter()
router.include_router(healthcheck_router)
router.include_router(packages_router)
router.include_router(admin_router)
