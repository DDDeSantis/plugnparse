import inspect
import logging
from typing import Type, Optional, NoReturn, Union

##########################################################################
# Levels
##########################################################################
CRITICAL = logging.CRITICAL
FATAL = logging.FATAL
ERROR = logging.ERROR
WARNING = logging.WARNING
WARN = logging.WARN
INFO = logging.INFO
DEBUG = logging.DEBUG
NOTSET = logging.NOTSET


##########################################################################
# Logger Methods
##########################################################################
def create_logger(logger_name: str) -> logging.Logger:
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    return logger


__logger__ = create_logger("default")  # The main logger


def get_logger(logger_name: Optional[str]) -> logging.Logger:
    if logger_name is None:
        return __logger__
    return logging.getLogger(logger_name)


def set_logger(logger: Union[logging.Logger, str]):
    if isinstance(logger, (logging.Logger, logging.LoggerAdapter)):
        __logger__ = logger
    else:
        __logger__ = logging.getLogger(logger)


def set_log_level(level: int):
    __logger__.setLevel(level)


def function_file_line(message: str, stack=inspect.stack()[0]):
    caller = inspect.getframeinfo(stack[0])
    _message = "\"" + str(caller.filename) + ":" + str(caller.lineno) + "\" - in [" + str(
        caller.function) + "] --- " + message
    return _message


##########################################################################
# Logging Methods
##########################################################################
def log(*argv, level: int, record_location: bool = False, stack=inspect.stack()[1]) -> str:
    message = ""
    if not __logger__.isEnabledFor(level):
        return message
    for arg in argv:
        message += str(arg)
    if record_location:
        message = function_file_line(message=message, stack=stack)
    __logger__.log(level=level, msg=message)
    return message


def debug(*argv, record_location: bool = False, stack: Optional[inspect.FrameInfo] = None) -> str:
    """Log to the DEBUG stream.

    Args:
        argv: List of inputs to be concatenated into a log message.
        record_location: Record the stack frame from which this log method was invoked iff True.
        stack: Stack info for the calling method.

    Returns:
        (str) Concatenated log message.
    """
    if not __logger__.isEnabledFor(DEBUG):
        return ""
    return log(*argv, level=logging.DEBUG, record_location=record_location, stack=stack if stack is not None or not record_location else inspect.stack()[1])


def info(*argv, record_location: bool = False, stack: Optional[inspect.FrameInfo] = None) -> str:
    """Log to the INFO stream.

    Args:
        argv: List of inputs to be concatenated into a log message.
        record_location: Record the stack frame from which this log method was invoked iff True.
        stack: Stack info for the calling method.

    Returns:
        (str) Concatenated log message.
    """
    if not __logger__.isEnabledFor(INFO):
        return ""
    return log(*argv, level=logging.INFO, record_location=record_location, stack=stack if stack is not None or not record_location else inspect.stack()[1])


def warning(*argv, record_location: bool = False, stack: Optional[inspect.FrameInfo] = None) -> str:
    """Log to the WARNING stream.

    Args:
        argv: List of inputs to be concatenated into a log message.
        record_location: Record the stack frame from which this log method was invoked iff True.
        stack: Stack info for the calling method.

    Returns:
        (str) Concatenated log message.
    """
    if not __logger__.isEnabledFor(WARNING):
        return ""
    return log(*argv, level=logging.WARNING, record_location=record_location, stack=stack if stack is not None or not record_location else inspect.stack()[1])


def error(*argv, record_location: bool = False, stack: Optional[inspect.FrameInfo] = None) -> str:
    """Log to the ERROR stream.

    Args:
        argv: List of inputs to be concatenated into a log message.
        record_location: Record the stack frame from which this log method was invoked iff True.
        stack: Stack info for the calling method.

    Returns:
        (str) Concatenated log message.
    """
    if not __logger__.isEnabledFor(ERROR):
        return ""
    return log(*argv, level=logging.ERROR, record_location=record_location, stack=stack if stack is not None or not record_location else inspect.stack()[1])


def critical(*argv, record_location: bool = False, stack: Optional[inspect.FrameInfo] = None) -> str:
    """Log to the CRITICAL stream.

    Args:
        argv: List of inputs to be concatenated into a log message.
        record_location: Record the stack frame from which this log method was invoked iff True.
        stack: Stack info for the calling method.

    Returns:
        (str) Concatenated log message.
    """
    if not __logger__.isEnabledFor(CRITICAL):
        return ""
    return log(*argv, level=logging.CRITICAL, record_location=record_location, stack=stack if stack is not None or not record_location else inspect.stack()[1])


def log_and_raise(exception_type: Type[Exception], *args, record_location: bool = True, **kwargs) -> NoReturn:
    """Raise an exception immediately after logging its message to the ERROR stream.

    Args:
        exception_type: type
            The type of Exception to raise.
        args: list
            Arguments to concatenate into a string log message.
        record_location: bool
            Record the stack frame from which this log method was invoked iff True.
        kwargs: dict
            Keyword arguments to `error`. Currently only `record_location` is supported.

    Raises:
        Exception:
              A subclass of type `exception_type`. Guaranteed to raise.
    """
    raise exception_type(error(*args, record_location=record_location, stack=inspect.stack()[1]))
