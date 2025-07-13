import logging
from enum import StrEnum
from rich.logging import RichHandler
from rich.console import Console
from rich.traceback import Traceback
import threading

_trace_local = threading.local()  # For adding trace id for every transaction

console = Console()


# LOG_FORMAT_DEBUG = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
# LOG_FORMAT_DEBUG = "%(levelname)s:%(message)s:%(pathname)s:%(funcName)s:%(lineno)d"
# LOG_FORMAT_DEBUG = "%(asctime)s | %(levelname)s | %(name)s |  %(message)s | %(pathname)s | %(funcName)s | %(lineno)d"


class TraceIdFilter(logging.Filter):
    def filter(self, record):
        record.trace_id = getattr(_trace_local, "trace_id", None)
        # trace_id = getattr(request.state, "trace_id", None)
        return True


class LogLevel(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    # CRITICAL = "CRITICAL"


LOG_FORMAT_DEBUG = "%(asctime)s |   %(trace_id)s |    %(message)s | %(name)s |%(funcName)s | %(lineno)d"


def configure_logging(log_level: LogLevel = LogLevel.DEBUG):
    """
    Configures the logging settings for the application.

    Args:
        log_level (LogLevel): The logging level to set. Defaults to LogLevel.DEBUG.
    """
    log_level = str(log_level).upper()
    log_levels = [level.value for level in LogLevel]
    logging.getLogger().addFilter(TraceIdFilter())  # <-- Add this line
    if log_level not in log_levels:
        logging.basicConfig(level=LogLevel.ERROR,
                            handlers=[RichHandler(console=console,
                                                  markup=True,
                                                  rich_tracebacks=True,
                                                  tracebacks_show_locals=True)])

        return
    if log_level == LogLevel.DEBUG:
        logging.basicConfig(level=log_level, format=LOG_FORMAT_DEBUG,
                            handlers=[RichHandler(console=console,
                                                  markup=True,
                                                  rich_tracebacks=True,
                                                  tracebacks_show_locals=True)])
        return

    # logging.basicConfig(
    #     level=log_level,
    #     format=LOG_FORMAT_DEBUG,
    #     datefmt="%Y-%m-%d %H:%M:%S"
    # )
    logging.basicConfig(
        level=log_level,
        handlers=[RichHandler(console=console,
                              markup=True,
                              rich_tracebacks=True,
                              tracebacks_show_locals=True)])
    logging.getLogger().setLevel(log_level)

    logging.debug("Logging configured with level: %s", log_level)

#
# # ********************Critical handler code ******************
#
# import logging
#
# def notify_critical(msg):
#     # Your notification logic here
#     print(f"CRITICAL notification: {msg}")
#
# class CriticalHandler(logging.Handler):
#     def emit(self, record):
#         if record.levelno == logging.CRITICAL:
#             notify_critical(self.format(record))
#
# # Add the handler to the root logger
# critical_handler = CriticalHandler()
# critical_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
# logging.getLogger().addHandler(critical_handler)
#
# # ****************************************
