from config import settings
from fastapi import FastAPI


def start_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
    )
    return app


app = start_app()


@app.get("/ping")
async def pong():
    return {"msg": "pong"}
