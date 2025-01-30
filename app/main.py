from fastapi import FastAPI
from fastapi import status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic_settings import BaseSettings
from loguru import logger
from fastapi_utils.tasks import repeat_every
from contextlib import asynccontextmanager

from app.db.admin import attach_admin_panel
from app.services.stats import StatsService


class ProjectSettings(BaseSettings):
    LOCAL_MODE: bool = False


def register_exception(application):
    @application.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
        # or logger.error(f'{exc}')
        logger.debug(f'{exc}')
        content = {'status_code': 422, 'message': exc_str, 'data': None}
        return JSONResponse(
            content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )

    application.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


def register_cors(application):
    application.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )


@repeat_every(seconds=6 * 60 * 60)
async def update_user_stats():
    try:
        await StatsService.update_stats()
    except Exception as e:
        logger.exception(e)


@asynccontextmanager
async def lifespan(app):
    await update_user_stats()
    yield


def init_web_application():
    project_settings = ProjectSettings()
    application = FastAPI(
        openapi_url='/openapi.json',
        docs_url='/docs',
        redoc_url='/redoc',
        lifespan=lifespan
    )

    if project_settings.LOCAL_MODE:
        register_exception(application)
        register_cors(application)

    from app.routes.user import router as user_router
    from app.routes.stats import router as stats_router

    application.include_router(user_router)
    application.include_router(stats_router)

    attach_admin_panel(application)

    return application


def run() -> FastAPI:
    application = init_web_application()
    return application


fastapi_app = run()
