
import itertools
import collections

def window(it:iter, size:int=2):
    it = iter(it)
    window = collections.deque(itertools.islice(it, 0, size), maxlen=size)
    while True:
        yield tuple(window)
        try:
            window.append(next(it))
        except StopIteration:
            return
