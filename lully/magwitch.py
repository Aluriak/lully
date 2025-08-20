"""The Magwitch class definition, with some helpers and the API around it.

"""

import inspect
from functools import wraps, partial
from itertools import zip_longest


class Magwitch:
    """Decorator for a function. Can be generated with staticmethod `build`.

    """

    def __init__(self, func:callable, enablers:dict, disablers:dict,
                 make_not_value:callable=lambda x: not x,
                 values:dict={}, set_params:dict={}):
        """Unless you know what you do, use Magwitch.build to build instances.

        func -- the wrapped function
        enablers -- map from attribute to enable to the parameter to set to True
        disablers -- like enablers, but to set parameter to False
        make_not_value -- function mapping a value with its deactivated state
        values -- value to use in place of True, if given
        set_params -- parameters already set by previous wrappers

        """
        self.__func = func
        self.__set_params = set_params
        self.__enablers, self.__disablers = enablers, disablers
        self.__values = values
        self.__make_not_value = make_not_value


    def __call__(self, *args, **kwargs):
        return self.__func(*args, **self.__set_params, **kwargs)

    def __getattr__(self, name:str):
        if name in self.__enablers:
            access, make_val = self.__enablers, lambda x:x
        elif name in self.__disablers:
            access, make_val = self.__disablers, self.__make_not_value
        else:
            raise AttributeError
        # print('ATTR:', name, access[name], self.__values)
        return self.__with_switch({access[name]: make_val(self.__values.get(access[name], True))})


    def __with_switch(self, switches:dict):
        return Magwitch(self.__func, self.__enablers, self.__disablers,
                        self.__make_not_value, self.__values,
                        set_params={**self.__set_params, **switches})

    @staticmethod
    def build(func, enable:str='', disable:str=('no_', 'not_'), use_defaults:bool=False,
              make_not_value:callable=None):
        """Return a brand new Magwitch for given function.

        func -- the wrapped function
        enable -- prefix(es) to give to each boolean parameter to set it to True
        disable -- like enable, but to deactivate them
        use_defaults -- use the default value as truthy value
        make_not_value -- function mapping a value with its deactivated state

        By default use_defaults is False, motivated by this use case:
        def save_figure(in_png:bool=False): ...
        Here, save_figure.in_png should map the parameter in_png to True.

        Also make_not_value is by default equivalent to lambda x: not x.
        You can use it as a hook to perform more complex behavior.

        """
        if use_defaults:
            switches = dict(_boolean_args_and_options(func))
            kwargs = {'values': switches}
        else:
            switches = frozenset(_boolean_args(func))
            kwargs = {'values': {}}
        enables = {enable} if isinstance(enable, str) else frozenset(enable)
        disables = {disable} if isinstance(disable, str) else frozenset(disable)
        # verify the validity of prefixes
        for enable in enables:
            if enable.startswith('_'):
                raise ValueError("Given prefix for enabling switches is non-valid,"
                                 " because starting by '_': {}".format(enable))
        for disable in disables:
            if disable.startswith('_'):
                raise ValueError("Given prefix for disabling switches is non-valid,"
                                 " because starting by '_': {}".format(disable))
        # compute the attributes
        enablers = {enable + switch: switch  for switch in switches for enable in enables}
        disablers = {disable + switch: switch for switch in switches for disable in disables}
        # print(func)
        # print(enablers)
        # print(disablers)
        # print(kwargs)
        if make_not_value:
            kwargs['make_not_value'] = make_not_value
        return Magwitch(func, enablers, disablers, **kwargs)


def _boolean_args(func:callable) -> [str]:
    """Yield all boolean args of given funtion.

    See _boolean_args_and_options for a more complex behavior

    """
    annotations = inspect.getfullargspec(func).annotations
    yield from (arg for arg, type in annotations.items() if type is bool)


def _boolean_args_and_options(func:callable, default_bool_value=True) -> [(str, object)]:
    """Yield pairs (boolean argument, default value) for given function.

    Note that arguments are not yield in the real order.

    """
    specs = inspect.getfullargspec(func)
    # print('FUNC SPECS:', specs)
    annotations = specs.annotations
    switches = {arg for arg, type in annotations.items() if type is bool}
    null = type('NULL', (), {})()
    # positional args
    for posarg, option in zip_longest(reversed(specs.args), reversed(specs.defaults), fillvalue=null):
        if posarg in switches:
            yield posarg, default_bool_value if option is null else option
    # kwonly args
    for kwarg in specs.kwonlyargs:
        if kwarg in switches:
            yield kwarg, specs.kwonlydefaults.get(kwarg, default_bool_value)


@wraps(Magwitch.build)
def on_with(*args, **kwargs):
    return lambda func: Magwitch.build(func, *args, **kwargs)


def on(func):
    """Like on_with, but with default parameters only."""
    return on_with()(func)
