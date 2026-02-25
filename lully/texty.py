"""Wrapper around textx lib, covering 90% of my use cases"""

import glob
import textx
from textx import metamodel_from_str
from typing import Union

METAMODEL = None
def parse_text(text:str, **kwargs):
    global METAMODEL
    if not METAMODEL:
        METAMODEL = metamodel_from_str(read_grammar(**kwargs), classes=Rule.CLASSES)
    model = METAMODEL.model_from_str(text)
    # print('MODEL:', model, type(model), dir(model))
    return model


def read_grammar(files: Union[str,list[str]] = [], inline: str = '', outfile: str = None) -> str:
    base_rules = ' | '.join(r.__name__ for r in Rule.CLASSES if getattr(r, 'is_base', False))
    rules = [f"Model:\n    {base_rules} \n;"]
    for f in sorted(glob.glob(files) if isinstance(files, str) else files):
        with open(f) as fd:
            rules.append(fd.read())
    for cls in Rule.CLASSES:
        if getattr(cls, 'grammar_in_doc', True) and getattr(cls, '__doc__', None):
            rules.append(f"{cls.__name__}:\n{cls.__doc__}\n;")
    grammar = '\n'.join(rules) + '\n' + (inline or '')
    if outfile:
        with open(outfile, 'w') as fd:
            fd.write(grammar)
    return grammar


class Rule:
    CLASSES = []

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __init_subclass__(cls, base: bool = None, grammar_in_doc: bool = True, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.is_base = cls.__name__.startswith('Base') if base is None else bool(base)  # type: ignore[attr-defined]
        cls.grammar_in_doc = bool(grammar_in_doc)  # type: ignore[attr-defined]
        Rule.CLASSES.append(cls)
