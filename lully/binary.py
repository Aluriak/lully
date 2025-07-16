import itertools
from typing import Union

def xor_merge(text: Union[str, bytes], key: Union[str, bytes]) -> bytes:
    """XOR on given text with key, the latter being repeated if necessary"""
    if isinstance(text, str):
        text = text.encode()
    if isinstance(key, str):
        key = key.encode()
    return bytes(a ^ b for a, b in zip(text, itertools.cycle(key)))
