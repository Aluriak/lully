
def with_scheme(url: str, *, scheme: str = 'https://') -> str:
    """
    >>> with_scheme('dataio.chu-brest.fr')
    'https://dataio.chu-brest.fr'
    >>> with_scheme('https://dataio.chu-brest.fr')
    'https://dataio.chu-brest.fr'
    >>> with_scheme('http://dataio.chu-brest.fr')
    'https://http://dataio.chu-brest.fr'
    """
    return url if url.startswith(scheme) else (scheme + url)

def without_scheme(url: str) -> str:
    """
    >>> without_scheme('dataio.chu-brest.fr')
    'dataio.chu-brest.fr'
    >>> without_scheme('https://dataio.chu-brest.fr')
    'dataio.chu-brest.fr'
    """
    for scheme in ('http://', 'https://'):
        if url.startswith(scheme):
            return url[len(scheme):]
    return url

