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
    """Creates a new, standard logger instance.

    Args:
        logger_name: str
            The name of the logger.

    Returns:
        logging.Logger:
            The logger instance.
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    return logger


__logger__ = create_logger("default")  # The main logger


def get_logger(logger_name: Optional[str]) -> logging.Logger:
    """Gets a logger instance.

    Args:
        logger_name: Optional[str]
            The optional logger name. If not provided, the default logger will be used. If provided,
            a registered logger instance will be returned.

    Returns:
        logging.Logger:
            The desired logger instance.
    """
    if logger_name is None:
        return __logger__
    return logging.getLogger(logger_name)


def set_logger(logger: Union[logging.Logger, str]):
    """Sets a logger to the default logger instance.

    Args:
        logger: Union[logging.Logger, str]
            Either a logger name or a logger instance. If a name is provided, a registered logger instance
            will be set to the default logger.
    """
    if isinstance(logger, (logging.Logger, logging.LoggerAdapter)):
        __logger__ = logger
    else:
        __logger__ = logging.getLogger(logger)


def set_log_level(level: int):
    """Sets a logger level to the default logger instance.

    Args:
        level: int
            The desired logger level.
    """
    __logger__.setLevel(level)


def function_file_line(message: str, stack: inspect.FrameInfo = inspect.stack()[0]) -> str:
    """Prepends the stack frame information to a provided message.

    Args:
        message: str
            A message to append onto the stack information
        stack: inspect.FrameInfo
            The stack frame information.

    Returns:
        str:
            The message with the stack frame information.
    """
    caller = inspect.getframeinfo(stack[0])
    new_message = "\"" + str(caller.filename) + ":" + str(caller.lineno) + "\" - in [" + str(
        caller.function) + "] --- " + message
    return new_message


##########################################################################
# Logging Methods
##########################################################################
def log(*argv, level: int, record_location: bool = False, stack: inspect.FrameInfo = inspect.stack()[1]) -> str:
    """Logs a message to the logger.

    Args:
        *argv:
            The positional arguments to log.
        level: int
            The level in which to log the message.
        record_location: bool
            Indicates whether to record the stack frame information.
        stack: inspect.FrameInfo
            The calling stack frame information.

    Returns:
        str:
            The message that was logged to the logger.
    """
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
        argv:
            List of inputs to be concatenated into a log message.
        record_location: bool
            Record the stack frame from which this log method was invoked iff True (default: False).
        stack: Optional[inspect.FrameInfo]
            The optional stack info for the calling method.

    Returns:
        str:
            Concatenated log message.
    """
    if not __logger__.isEnabledFor(DEBUG):
        return ""
    return log(*argv, level=logging.DEBUG, record_location=record_location,
               stack=stack if stack is not None or not record_location else inspect.stack()[1])


def info(*argv, record_location: bool = False, stack: Optional[inspect.FrameInfo] = None) -> str:
    """Log to the INFO stream.

    Args:
        argv:
            List of inputs to be concatenated into a log message.
        record_location: bool
            Record the stack frame from which this log method was invoked iff True (default: False).
        stack: Optional[inspect.FrameInfo]
            The optional stack info for the calling method.

    Returns:
        str:
            Concatenated log message.
    """
    if not __logger__.isEnabledFor(INFO):
        return ""
    return log(*argv, level=logging.INFO, record_location=record_location,
               stack=stack if stack is not None or not record_location else inspect.stack()[1])


def warning(*argv, record_location: bool = False, stack: Optional[inspect.FrameInfo] = None) -> str:
    """Log to the WARNING stream.

    Args:
        argv:
            List of inputs to be concatenated into a log message.
        record_location: bool
            Record the stack frame from which this log method was invoked iff True (default: False).
        stack: Optional[inspect.FrameInfo]
            The optional stack info for the calling method.

    Returns:
        str:
            Concatenated log message.
    """
    if not __logger__.isEnabledFor(WARNING):
        return ""
    return log(*argv, level=logging.WARNING, record_location=record_location,
               stack=stack if stack is not None or not record_location else inspect.stack()[1])


def error(*argv, record_location: bool = False, stack: Optional[inspect.FrameInfo] = None) -> str:
    """Log to the ERROR stream.

    Args:
        argv:
            List of inputs to be concatenated into a log message.
        record_location: bool
            Record the stack frame from which this log method was invoked iff True (default: False).
        stack: Optional[inspect.FrameInfo]
            The optional stack info for the calling method.

    Returns:
        str:
            Concatenated log message.
    """
    if not __logger__.isEnabledFor(ERROR):
        return ""
    return log(*argv, level=logging.ERROR, record_location=record_location,
               stack=stack if stack is not None or not record_location else inspect.stack()[1])


def critical(*argv, record_location: bool = False, stack: Optional[inspect.FrameInfo] = None) -> str:
    """Log to the CRITICAL stream.

    Args:
        argv:
            List of inputs to be concatenated into a log message.
        record_location: bool
            Record the stack frame from which this log method was invoked iff True (default: False).
        stack: Optional[inspect.FrameInfo]
            The optional stack info for the calling method.

    Returns:
        str:
            Concatenated log message.
    """
    if not __logger__.isEnabledFor(CRITICAL):
        return ""
    return log(*argv, level=logging.CRITICAL, record_location=record_location,
               stack=stack if stack is not None or not record_location else inspect.stack()[1])


def log_and_raise(exception_type: Type[Exception], *args, record_location: bool = True, **kwargs) -> NoReturn:
    """Raise an exception immediately after logging its message to the ERROR stream.

    Args:
        exception_type: Type[Exception]
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
