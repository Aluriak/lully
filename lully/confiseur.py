"""
"""

import os
import copy
import json
import configparser
from collections import ChainMap


AVAILABLE_FILETYPES = 'json', 'ini'
TYPE_TYPE = type  # type is exposed in interface, so using TYPE_TYPE will lift ambiguities
__version__ = '0.0.1'


def parse_string(string: str, filetype: str) -> dict:
    if filetype == 'ini':
        cfg = configparser.ConfigParser()
        cfg.read_string(string)
        return {
            section: {sub: val for sub, val in cfg[section].items()}
            for section in cfg.sections()
        }
    elif filetype == 'json':
        return json.loads(string)
    elif filetype in AVAILABLE_FILETYPES:
        raise NotImplementedError(f"Filetype {filetype} is said to be an available filetype, but its parsing is not handled !")
    assert False, "shouldn't happen (unless a subclass is doing some black magic with filetypes?)"


def parse_file(fname: str, filetype: str) -> dict:
    if filetype == 'ini':
        cfg = configparser.ConfigParser()
        cfg.read(input_file)
        return {
            section: {sub: val for sub, val in cfg[section].items()}
            for section in cfg.sections()
        }
    elif filetype == 'json':
        with open(input_file) as fd:
            return json.load(fd)
    elif filetype in AVAILABLE_FILETYPES:
        raise NotImplementedError(f"Filetype {filetype} is said to be an available filetype, but its parsing is not handled !")
    assert False, "shouldn't happen (unless a subclass is doing some black magic with filetypes?)"


def is_input_file(fname: str) -> bool:
    return fname and os.path.isfile(fname)


def filetype_of(fname: str, hint: str, isfile: bool) -> str:
    filetype = None
    if isfile:
        filetype = hint or os.path.splitext(fname)[1].lstrip('.').lower()
    else:
        try:
            json.loads(fname)
        except json.JSONDecodeError:
            try:
                configparser.ConfigParser().read_string(fname)
            except json.JSONDecodeError:
                raise ValueError(f"Given object {str(fname)[:20]} cannot be understood. It is not a file, nor a json formatted string, nor an ini formatted string.")
            else:
                filetype = 'ini'
        else:
            filetype = 'json'
    if filetype not in AVAILABLE_FILETYPES:
        raise NotImplementedError(f"Filetype {filetype} is not handled. Available: {', '.join(AVAILABLE_FILETYPES)}")
    return filetype


class Bonbon:
    """A bonbon describes an option, with many options and potential use

    A Confiseur will provide multiple Bonbon instances.

    """
    def __init__(self, key: str, subkey: str, default=None, type = None, subtypes = None, choices=None, aliases: dict = None, list_as_str: bool = False, dict_as_str: bool = False, is_collection: bool = False):
        self.key, self.subkey = key, subkey
        self.type, self.subtypes = type, subtypes  # if given, subtypes indicate the expected type of items of the value, if that value is a collection
        if self.type is None:
            self.type = str if default is None else TYPE_TYPE(default)  # by default, we manipulate strings
        self.choices = choices
        self.default = default
        self.aliases = aliases or {}
        self.list_as_str = list_as_str  # if true, say that the input value must be a list, but that it may come as a string where items are separated by a comma
        self.dict_as_str = dict_as_str  # if true, say that the input value must be a dict, coming as a string encoded like `key1=val1,key2=val2,…`
        # collections must be detected and treated differently
        self.is_collection = self.list_as_str or self.dict_as_str or isinstance(default, (list, tuple, set, frozenset, dict)) or is_collection
        if self.is_collection and subtypes is None:
            self.subtypes = self.type
            if self.list_as_str:
                self.type = list
            elif self.dict_as_str:
                self.type = dict
            else:
                self.type = type(default)


    def value_in(self, d: dict) -> object:
        return d[self.key][self.subkey]

    def expand_alias(self, d: dict):
        value = self.value_in(d)
        if isinstance(value, str) and value in self.aliases:
            self.put_on(d, self.aliases[value])

    def put_default_on(self, d: dict):
        return self.put_on(d, self.default, exists_ok=True, invalid_ok=False)

    @property
    def has_choice(self) -> bool:
        return bool(self.choices)

    @property
    def is_typed(self) -> bool:
        return bool(self.type)

    def accepts_typed(self, value: object) -> bool:
        "True if given value is of acceptable type"
        assert self.type is not None, self.type
        ok = isinstance(value, self.type)
        if ok and self.is_collection:
            ok = all(isinstance(v, self.subtypes) for v in (value.values() if isinstance(value, dict) else value))
        return ok

    def put_on(self, d: dict, value: object, exists_ok: bool = True, invalid_ok: bool = False):
        key, subkey = self.key, self.subkey
        print(f'PUT_ON: setting {value=} for {key=} {subkey=} and {d=}')
        if key in d and isinstance(d[key], dict):
            pass  # ok
        elif key in d:
            if not invalid_ok:
                raise ValueError(f"Given dictionnary can't welcome {self} because key {key} is already here, associated with a {type(d[key])} (of value {d[key]}), not a dictionnary.")
            # else:  nothing to do
        else:
            d[key] = {}
        if subkey in d[key]:
            if not exists_ok:
                raise ValueError(f"Given dictionnary can't welcome {self} because subkey {subkey} is already here, associated with a {type(d[key][subkey])} of value {d[key][subkey]}.")
            # else:  nothing to do
        else:
            if self.list_as_str and isinstance(value, str):
                value = value.split(',')
                value = list(map(self.type, value)) if self.type else value
            elif self.dict_as_str and isinstance(value, str):
                value_as_dict = {}
                for pair in value.split(','):
                    _key, _val = pair.split('=' if '=' in value else ':')
                    value_as_dict[_key] = self.subtypes(_val) if self.type else _val
                value = value_as_dict
            else:  # must be castable directly if any type is provided
                value = self.type(value) if self.type else value

            print(f'Setting {value=} for {key=} {subkey=} and {d=}')
            d[key][subkey] = value

    def __str__(self):
        rep = ''.join((
            ('' if getattr(self, field, None) is None else f' {field}={getattr(self, field)}')
            for field in ('value', 'type', 'choices', 'default')
        ))
        if rep:
            rep = ' with' + rep
        return f'<Bonbon {repr(self.key)}.{repr(self.subkey)}{rep}>'


class Confiseur:
    """An abstract class for configuration file automatic handling.

    Subclasses must provide an iterable of Bonbon instances returned
    by the called-only-once method bonbons().

    Other methods can be overwritten, such as set_defaults(), derive_values(),
    derive_types(), validate() and init(), each of them being called at
    a specific time of option parsing, namely default propagation,
    aliasing resolution, casting and validation, allowing subclasses to
    implement virtually any supplementary behavior they may need.

    """
    def __init__(self, *input_files: str, filetype: str = None):
        self.input_files = tuple(input_files)
        self.filetype_hint = filetype
        self.errors = []  # list of error messages, populated during validation
        self.__bonbons = tuple(self.__gen_bonbons())
        self.__raw_config = self.__parse_inputs()
        self.config = copy.deepcopy(self.__raw_config)
        self.__set_defaults()
        self.__derive_values()
        self.__derive_types()
        # function that may be implemented by subclasses
        self.validate(self.config)
        self.init()

    def add_error(self, message: str):
        self.errors.append(message)

    @property
    def has_error(self) -> bool:
        return bool(self.errors)

    @property
    def raw(self) -> dict:
        return self.__raw_config

    def __gen_bonbons(self) -> [Bonbon]:
        for bonbon in self.bonbons():
            if isinstance(bonbon, (tuple, list)) and 2 < len(bonbon) < 5:
                yield Bonbon(*bonbon)
            elif isinstance(bonbon, Bonbon):
                yield bonbon
            else:
                raise TypeError(f"Don't know what that is, but that's not a bonbon: {bonbon}")

    def __getitem__(self, key):
        return self.config[key]

    def init(self):
        pass  # implementation left as an exercise for the subclass

    def validate(self, config: dict):
        pass  # implementation left as an exercise for the subclass

    def __parse_inputs(self):
        def gen_dicts():
            for input_file in self.input_files:
                isfile = is_input_file(input_file)
                filetype = filetype_of(input_file, hint=self.filetype_hint, isfile=isfile)
                yield (parse_file if isfile else parse_string)(input_file, filetype)
        return dict(ChainMap(*gen_dicts()).items())

    def set_defaults(self, config: dict):
        pass  # implementation left as an exercise for the subclass
    def __set_defaults(self):
        "Called after file parsing to put the default values into all fields"
        for bonbon in self.__bonbons:
            bonbon.put_default_on(self.config)
        self.set_defaults(self.config)


    def derive_values(self, config: dict):
        pass  # implementation left as an exercise for the subclass
    def __derive_values(self):
        "Its here that the aliases are expanded"
        for bonbon in self.__bonbons:
            bonbon.expand_alias(self.config)
        self.derive_values(self.config)


    def derive_types(self, config: dict):
        pass  # implementation left as an exercise for the subclass
    def __derive_types(self):
        for bonbon in self.__bonbons:
            value = bonbon.value_in(self.config)
            if bonbon.has_choice and not value in bonbon.choices:
                self.add_error(f"Bonbon {bonbon} expected one of {len(bonbon.choices)}, got {value}, which is not valid. Must be one of: {', '.join(map(str, bonbon.choices))}")
            elif not bonbon.accepts_typed(value):
                self.add_error(f"Bonbon {bonbon} expected type {bonbon.type}, got {value} of type {type(value)}")
        self.derive_types(self.config)


    def bonbons(self) -> [Bonbon]:
        raise NotImplementedError(f"Subclasses of Confiseur must have a collection of Bonbon instances.")
