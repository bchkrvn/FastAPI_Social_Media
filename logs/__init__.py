__all__ = ["log", "LOG_NAME"]

from logging import getLogger

LOG_NAME = "app_logger"
log = getLogger(LOG_NAME)
