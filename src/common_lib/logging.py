import logging
from enum import StrEnum

# LOG_FORMAT_DEBUG = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FORMAT_DEBUG = "%(levelname)s:%(message)s:%(pathname)s:%(funcName)s:%(lineno)d"


class LogLevel(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    # CRITICAL = "CRITICAL"


def configure_logging(log_level: LogLevel = LogLevel.DEBUG):
    """
    Configures the logging settings for the application.

    Args:
        log_level (LogLevel): The logging level to set. Defaults to LogLevel.DEBUG.
    """
    log_level = str(log_level).upper()
    log_levels = [level.value for level in LogLevel]
    if log_level not in log_levels:
        logging.basicConfig(level=LogLevel.ERROR)
        return
    if log_level == LogLevel.DEBUG:
        logging.basicConfig(level=log_level, format=LOG_FORMAT_DEBUG)
        return

    # logging.basicConfig(
    #     level=log_level,
    #     format=LOG_FORMAT_DEBUG,
    #     datefmt="%Y-%m-%d %H:%M:%S"
    # )
    logging.basicConfig(
        level=log_level)
    logging.getLogger().setLevel(log_level)
    logging.debug("Logging configured with level: %s", log_level)
