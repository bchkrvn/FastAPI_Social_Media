import logging
from logging.config import dictConfig
from logging.handlers import RotatingFileHandler
from pathlib import Path

from logs import LOG_NAME


def configurate_logs(log_level: str = "INFO"):
    dir_path = Path(__file__).resolve().parent
    dir_path.joinpath("uvicorn").mkdir(exist_ok=True)
    dir_path.joinpath("info").mkdir(exist_ok=True)
    uvicorn_path = dir_path.joinpath(Path("uvicorn", "requests.log"))
    info_path = dir_path.joinpath(Path("info", "info.log"))

    uvicorn_format = logging.Formatter("%(levelname)s -- %(asctime)s -- %(message)s")
    uvicorn_handler = RotatingFileHandler(
        filename=uvicorn_path,
        mode="a",
        maxBytes=1_048_576,
        backupCount=10,
    )

    uvicorn_handler.setFormatter(uvicorn_format)
    uvicorn_logger = logging.getLogger("uvicorn.access")
    uvicorn_logger.addHandler(uvicorn_handler)

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "info": {
                "format": "[%(levelname)s] -- %(asctime)s -- %(filename)s.%(funcName)s(%(lineno)d) -- %(message)s"
            },
        },
        "handlers": {
            "console": {
                "level": log_level,
                "formatter": "info",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "level": log_level,
                "formatter": "info",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": info_path,
                "mode": "a",
                "maxBytes": 1048576,
                "backupCount": 10,
            },
        },
        "loggers": {
            LOG_NAME: {
                "level": log_level,
                "handlers": [
                    "console",
                    "file",
                ],
            },
        },
    }

    dictConfig(config)
