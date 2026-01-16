"""Helper around logging"""
import sys
import inspect
import logging
import lully as ll
from typing import Union, Callable


def log(*args, **kwargs):
    "Log function for the poor: just call it and you get to write in stderr asap"
    kwargs.setdefault('file') = sys.stderr
    kwargs.setdefault('flush') = True
    return print(*args, **kwargs)


class HandMadeLogger:
    def __init__(self, logfunc = print):
        self.logfunc = logfunc
        self.supp_kwargs = {}
        if ll.funcmore.has_param(logfunc, 'file'):
            self.supp_kwargs['file'] = sys.stderr
        if ll.funcmore.has_param(logfunc, 'flush'):
            self.supp_kwargs['flush'] = True
    def log(self, *args, **kwargs):
        return self.logfunc(*args, **self.supp_kwargs, **kwargs)
    debug = info = warning = warn = error = critical = log

def logger_from(obj: Union[Callable, logging.Logger] = print) -> Union[logging.Logger, HandMadeLogger]:
    """Return an object able to log using .debug, .info, .warning etc."""

    if obj is print or obj is None or obj is HandMadeLogger:
        return HandMadeLogger()

    elif type(obj) is type(logger_from) and callable(obj):  # is a function
        return HandMadeLogger(logfunc=obj)

    elif isinstance(obj, HandMadeLogger):
        return obj

    elif isinstance(obj, logging.Logger):
        return obj

    elif hasattr(obj, 'logger'):
        return logger_from(obj.logger)

    elif hasattr(obj, 'log'):
        return logger_from(obj.log)

    raise ValueError(f"Cannot handle {obj=} of type {type(obj)}")

