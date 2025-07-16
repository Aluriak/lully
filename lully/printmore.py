import re
import json

def markoji(text: str) -> str:
    "format from markdown and emojize"
    import markdown
    return markdown.markdown(emojize(text))

def emojize(text: str) -> str:
    try:
        import emoji  # type: ignore[import-not-found]
    except ImportError:
        return text

    if ':' in text:
        text = emoji.emojize(text)
    if ':' in text:
        text = emoji.emojize(text, language='alias')
    return text


def hrlist(l: list[str], fsep=' and ', fmt='') -> str:
    if fmt:
        l = [fmt + e + fmt for e in l if e.strip()]
    if len(l) > 1:
        *firsts, last = l
        return ', '.join(elm for elm in firsts) + ' et ' + last
    else:
        return ''.join(l)


def datatype_to_hname(name: str) -> str:
    """
    >>> datatype_to_hname('uint64')
    'Nombre entier positif'
    >>> datatype_to_hname('int64')
    'Nombre entier'
    >>> datatype_to_hname('float32') == datatype_to_hname('double')
    True
    >>> datatype_to_hname('str') == datatype_to_hname('string')
    True
    """
    name = name.lower()
    if name == 'null':
        return 'Indéfini'
    if name in {'str', 'string', 'large_string', 'chaine', 'chaîne'}:
        return 'Texte'
    if match := re.fullmatch(r'(u)?(int|char|float|double)([0-9]*)', name):
        unsigned, kind, size = match.groups()
        kind = 'Nombre entier' if kind in {'int', 'char'} else 'Nombre'
        unsigned = ' positif' if unsigned else ''
        return kind + unsigned
    if match := re.fullmatch(r'(timestamp|time)([0-9]*)(\[([a-z]+)\])?', name):
        # resolution = match.groups(0)
        return 'Date'
    return name


def curl_command(url: str, *, headers: dict = {}, data: dict = {}, post=None) -> str:
    "Show the curl command for get or post request ; very basic"
    _headers = ' '.join(f"-H '{k}: {v}'" for k, v in headers.items())
    post: bool = bool(data if post is None else post)
    _data = f"--data '{json.dumps(data)}'" if data else ''
    return f"""curl -X{'POST' if post else 'GET'} {_headers} {_data} {url}"""
