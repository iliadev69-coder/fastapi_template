import logging
import sys

from app.core.config import env_secrets


def setup_logger(
    module_name: str,
    log_level: int | str | None = None,
    log_file: str | None = None,
) -> logging.Logger:
    logger = logging.getLogger(module_name)
    log_format = (
        env_secrets.LOGGING_FORMAT or '[%(name)s] [%(levelname)s] [%(asctime)s] %(message)s'
    )
    logger.handlers.clear()

    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(logging.Formatter(log_format))
    logger.addHandler(sh)

    if log_file:
        fh = logging.FileHandler(log_file, encoding='utf-8')
        fh.setFormatter(logging.Formatter(log_format))
        logger.addHandler(fh)

    logger.setLevel(log_level or env_secrets.LOGGING_LEVEL)
    return logger
