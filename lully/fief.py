"""Implementation of Fief"""

import sys
import inspect
from typing import Callable, Generic, TypeVar
from functools import wraps


T = TypeVar('T')

class fief(Generic[T]):

    def __init__(self, func: Callable[..., T]):
        """Decorator that filter out parameters in kwargs that are not related to
        any formal parameter of the given function.

        """
        @wraps(func)
        def wrapped(*args, **kwargs):
            # print('######   ######')
            # print(func, type(func), args, kwargs)
            sig = signature_of(func)
            # print(sig)
            # for argname, arg in sig.parameters.items():
                # print(argname, arg, arg.kind)
            allparams = tuple(sig.parameters.items())
            pos_args = [kwargs[pname] for pname, p in allparams[len(args):] if pname in kwargs and p.kind == p.POSITIONAL_ONLY]
            kwo_args = {pname: kwargs[pname] for pname, p in allparams if pname in kwargs and (p.kind == p.POSITIONAL_OR_KEYWORD or p.kind == p.KEYWORD_ONLY)}
            # print(f'CALLING {func} with {args}, {pos_args}, {kwo_args}')
            return func(*args, *pos_args, **kwo_args)
        self._func = func
        self._wrapped = wrapped

    def __call__(self, *args, **kwargs) -> T:
        return self._wrapped(*args, **kwargs)

    @staticmethod
    def call(f: Callable[..., T], *args, **kwargs) -> T:
        return fief(f)(*args, **kwargs)



def old_call(f: Callable[..., T], **kwargs) -> T:
    spec = inspect.getfullargspec(f)
    pos_args = [kwargs[arg] for arg in spec.args if arg in kwargs]
    kwo_args = {arg: kwargs[arg] for arg in spec.kwonlyargs if arg in kwargs}
    return f(*pos_args, **kwo_args)


def signature_of(func: Callable) -> inspect.Signature:
    "If possible, return the signature of given python callable"
    S = inspect.Signature
    P = inspect.Parameter
    if func is str:
        return S([
            P('object', kind=P.POSITIONAL_OR_KEYWORD),
        ], return_annotation=str)
    elif func is int:
        return S([
            P('object', kind=P.POSITIONAL_ONLY),
            P('base', kind=P.KEYWORD_ONLY, default=10, annotation=int),
        ], return_annotation=int)
    elif func is print:
        return S([
            P('value', kind=P.VAR_POSITIONAL),
            P('sep', kind=P.KEYWORD_ONLY, default=' ', annotation=str),
            P('end', kind=P.KEYWORD_ONLY, default='\n', annotation=str),
            P('file', kind=P.KEYWORD_ONLY, default=sys.stdout),
            P('flush', kind=P.KEYWORD_ONLY, default=False, annotation=bool),
        ])
    else:  # let's hope it's a good old python function
        return inspect.signature(func)
