from fastapi import APIRouter, Depends, FastAPI

from app.core.containers import AppContainer, init_di_context
from app.views import router as root_router


def get_router() -> APIRouter:
    router = APIRouter(dependencies=[Depends(init_di_context)])
    router.include_router(root_router)
    return router


def create_app() -> FastAPI:
    app = AppContainer.app_factory.resolve_sync()
    router = get_router()
    app.include_router(router)
    return app
