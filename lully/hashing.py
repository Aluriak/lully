import uuid
import hashlib
import functools
from warnings import warn
from typing import Union
from .words import NOUNS, ADJECTIVES


def human_code(value: Union[str, uuid.UUID], *, CHUNK_SIZE: int = 40, method_sum: bool = False) -> str:
    if method_sum:
        warn(f"Sum method is not statistically sound. You will see a sur-representation of some indexes, thus a increase in collision number")
    if isinstance(value, uuid.UUID):
        value: str = str(value)
    h = hashlib.blake2b(digest_size=CHUNK_SIZE, usedforsecurity=False)
    h.update(str(value).encode())
    if method_sum:
        for val in h.digest():
            assert val >= 0, val
        vals = [int(val if val > 0 else 1) for val in h.digest()]
        assert len(vals) == CHUNK_SIZE
        noun_vals, adj_vals = sum(vals[:CHUNK_SIZE//2]), sum(vals[CHUNK_SIZE//2:])
    else:
        noun_vals = int.from_bytes(h.digest()[:CHUNK_SIZE//2], byteorder='big')
        adj_vals  = int.from_bytes(h.digest()[CHUNK_SIZE//2:], byteorder='big')
    return f'{NOUNS[noun_vals % len(NOUNS)]} {ADJECTIVES[adj_vals % len(ADJECTIVES)]}'

