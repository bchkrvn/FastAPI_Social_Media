import logging
import traceback

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from application.admin.router import admin_router
from application.auth.routers import auth_router
from application.config import settings
from application.post.routers import post_router
from application.subscription.routers import subscription_router
from application.user.routers import user_router
from logs import LOG_NAME
from logs.logger import configurate_logs

log = logging.getLogger(LOG_NAME)


def start_app() -> FastAPI:
    configurate_logs(settings.LOG_LEVEL)
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        debug=settings.DEBUG,
    )
    log.info(f'Запуск сервера в режиме "{settings}"')
    include_routers(app)
    return app


def include_routers(app: FastAPI):
    routers = (
        user_router,
        auth_router,
        admin_router,
        post_router,
        subscription_router,
    )
    for r in routers:
        app.include_router(r)


app = start_app()


@app.get("/ping", tags=["Проверка работоспособности"])
async def pong():
    return {"msg": "pong"}


@app.exception_handler(HTTP_500_INTERNAL_SERVER_ERROR)
async def internal_server_error_handler(request: Request, exc: Exception):
    traceback_str = "".join(traceback.format_tb(exc.__traceback__))
    log.error(f"Ошибка сервера: {request.url}, {str(exc)}, {traceback_str}")
    return JSONResponse(status_code=500, content={"detail": "Ошибка сервера"})
