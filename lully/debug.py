import os
import marshal
import requests

def get_cached(url: str, local_fname: str = 'todel.answer.data', kind: str = '', **kwargs) -> requests.Request:
    kind = kind or ('json' if url.endswith('.json') else 'text')
    if os.path.exists(local_fname):
        with open(local_fname, 'rb') as fd:
            data = marshal.load(fd)
    else:
        ans = requests.get(url)
        data = ans.json() if kind == 'json' else ans.text
        with open(local_fname, 'wb') as fd:
            marshal.dump(data, fd)
    return data


def shobj(obj, discard='_', maxwidth=100, indent='\t', print=print):
    print(indent, f"obj {obj} of type {type(obj)}:", sep='')
    for attr in dir(obj):
        if not attr.startswith(discard):
            v = repr(getattr(obj, attr))
            if isinstance(v, (bytes, str)) and len(v) > maxwidth:
                v = v[:30] + '[…]' + v[-30:]
            print(indent+indent, attr, v)
