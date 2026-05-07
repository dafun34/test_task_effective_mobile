import sys

from loguru import logger as loguru_logger
from app.core.config import settings


class Logger:
    def __init__(self):
        loguru_logger.remove()  # Удаляем стандартный вывод loguru
        loguru_logger.add(
            sys.stdout,
            level=settings.LOGGING_LEVEL,
            colorize=True,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{module}</cyan>:<cyan>{line}</cyan> | "
                "<magenta>{message}</magenta> | "
                "<yellow>{extra}</yellow>"
            ),
        )
        self._logger = loguru_logger

    def info(self, message, **extra):
        """Логирует информационное сообщение с дополнительными данными."""
        self._logger.bind(**extra).info(message)

    def debug(self, message, **extra):
        """Логирует отладочное сообщение с дополнительными данными."""
        self._logger.bind(**extra).debug(message)

    def warning(self, message, **extra):
        """Логирует предупреждающее сообщение с дополнительными данными."""
        self._logger.bind(**extra).warning(message)

    def error(self, message, **extra):
        """Логирует сообщение об ошибке с дополнительными данными."""
        self._logger.bind(**extra).error(message)

    def critical(self, message, **extra):
        """Логирует критическое сообщение с дополнительными данными."""
        self._logger.bind(**extra).critical(message)


logger = Logger()
