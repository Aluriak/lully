"""Utilitary around files and dirs and paths"""
import os
import glob as glob_module
from typing import Iterable


def files_in_dir(path: str, glob: str = '*') -> Iterable[str]:
    globs = [glob] if isinstance(glob, str) else list(glob)
    for glob in globs:
        for f in glob_module.glob(os.path.join(path, glob)):
            yield f


def content_of_file(path: str) -> str:
    with open(path) as fd:
        return fd.read()


def write_file(path: str, content: str):
    with open(path, 'w') as fd:
        fd.write(content)
    print(f"{len(content)} bytes written to {path}")
write = write_file


def list_tree(basedir: str, *, subdir: str = '', keep_basedir: bool = False) -> Iterable[str]:
    """From a/, returns a/b, a/c/d, a/e/f/g (or without the leading a/ if keep_basedir left to False)"""
    tdir = os.path.join(basedir, subdir)
    for entry in os.scandir(tdir):
        if entry.is_file():
            fpath = entry.path if keep_basedir else entry.path[len(basedir):]
            yield fpath
        elif entry.is_dir():
            yield from list_tree(basedir, subdir=os.path.join(subdir, entry.name), keep_basedir=keep_basedir)
        else:
            raise NotImplementedError(f"Cannot handle {entry} of type {type(entry)} (not a file nor a dir)")


def splitall_path(p: str) -> list[str]:
    parts = []
    while p and p != '/':
        p, tail = os.path.split(p)
        parts.append(tail)
    return list(reversed(parts))

def path_lsplit(p: str) -> tuple[str, str]:
    head, *tail = splitall_path(p)
    return head, os.path.join(*tail)
