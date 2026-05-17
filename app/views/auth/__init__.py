from fastapi import APIRouter

from app.views.auth.logout import router as logout_router
from app.views.auth.refresh import router as refresh_router
from app.views.auth.sign_in import router as sign_in_router

router = APIRouter(prefix='/auth', tags=['Auth'])

router.include_router(sign_in_router)
router.include_router(refresh_router)
router.include_router(logout_router)
