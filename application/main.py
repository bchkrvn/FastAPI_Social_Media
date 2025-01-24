from fastapi import FastAPI

from application.admin.routers import admin_router
from application.auth.router import auth_router
from application.config import settings
from application.user.router import user_router


def start_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        debug=settings.DEBUG,
    )
    include_routers(app)
    return app


def include_routers(app: FastAPI):
    routers = (
        user_router,
        auth_router,
        admin_router,
    )
    for r in routers:
        app.include_router(r)


app = start_app()


@app.get("/ping", tags=["Проверка работоспособности"])
async def pong():
    return {"msg": "pong"}
