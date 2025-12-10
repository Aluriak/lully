"""Populate caller global with (cabalistic) aliases"""
import os
import sys
import lully as ll
import shutil
import inspect
import functools
import itertools
import subprocess
import collections


def popglob(*, show: bool = False, in_repl: bool = False):
    """Populate caller global with (cabalistic) aliases

    show -- set to True to print to stdout a list of added aliases

    Do not use this seriously. It's a toy.

    """
    if in_repl and ll.is_repl():
        caller_globals = inspect.stack()[-1].frame.f_globals
    else:

        for frame in inspect.stack():
            if frame.function == 'popglob':
                continue
            # we should be at the caller frame ; lets populate its globals
            caller_globals = frame.frame.f_globals
            break

    g: dict[str, object] = {}  # aliases that will be added to the caller globals


    # Itertools aliases
    g['itertools'] = g['it'] = itertools
    g['c'] = g['chain'] = itertools.chain
    g['ċ'] = itertools.chain.from_iterable
    g['zil'] = itertools.zip_longest
    g['i'] = g['islice'] = itertools.islice

    # Collections aliases
    g['collections'] = collections
    g['deque'], g['defaultdict'], g['namedtuple'] = collections.deque, collections.defaultdict, collections.namedtuple

    # Other stdlib aliases
    g['os'] = os
    g['sys'] = sys
    g['shutil'] = shutil
    g['Popen'] = subprocess.Popen
    g['partial'] = functools.partial

    # Lully aliases
    g['ll'] = ll
    g['x'], g['ẋ'], g['ẍ'] = ll.x, None, ll.ẍ
    g['y'], g['ẏ'], g['ÿ'] = ll.y, None, ll.ÿ
    g['fief'] = ll.fief
    g['Otom'] = ll.Otom
    g['human_hashed'] = g['human_code'] = ll.human_code

    g['first'], g['last'], g['zip_with_next'] = ll.first, ll.last, ll.zip_with_next
    g['groupby'], g['chunks'], g['window'], g['divide'], g['flatten'], g['ncycles'], g['reversemap'] = ll.groupby, ll.chunks, ll.window, ll.divide, ll.flatten, ll.ncycles, ll.reversemap


    # TODO: set the following to useful values
    g['ı'] = itertools.chain
    g['ï'] = lambda: True


    if show:
        for alias, value in g.items():
            print('\t', alias, '=', value)
    caller_globals.update(g)
