"""
日志配置模块
提供统一的日志格式和文件/控制台输出。
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from config import get_settings

_CONFIGURED = False


class _ExtraFormatter(logging.Formatter):
    """自定义格式器，确保 wxid 字段始终存在"""
    def format(self, record):
        if not hasattr(record, "wxid"):
            record.wxid = "-"
        return super().format(record)


def configure_logging(name: str) -> logging.Logger:
    """配置并返回指定名称的 logger

    Args:
        name: logger 名称，通常为模块名

    Returns:
        logging.Logger: 配置好的 logger
    """
    global _CONFIGURED
    settings = get_settings()
    settings.log_dir.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger()
    if not _CONFIGURED:
        root.setLevel(logging.INFO)
        root.handlers.clear()

        formatter = _ExtraFormatter(
            fmt="%(asctime)s %(levelname)s [%(name)s] [wxid=%(wxid)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root.addHandler(console_handler)

        _CONFIGURED = True

    logger = logging.getLogger(name)
    logfile = str(Path(settings.log_dir) / f"{name}.log")

    if not any(
        isinstance(h, RotatingFileHandler) and getattr(h, "baseFilename", None) == logfile
        for h in logger.handlers
    ):
        file_handler = RotatingFileHandler(
            logfile,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setFormatter(
            _ExtraFormatter(
                fmt="%(asctime)s %(levelname)s [%(name)s] [wxid=%(wxid)s]: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        logger.addHandler(file_handler)

    logger.propagate = True
    return logger
