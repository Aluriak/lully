import re


def rreplace(s: str, old, new, n: int = 1) -> str:
    "Replace the n rightmost old by new (all of them by default)"
    return new.join(s.split(old) if n < 0 else s.rsplit(old, n))


def multi_subs_by_match(text: str, starts: list[int], repls: list[str], ends: list[int], ensure_input_order: bool = True):
    """Sub given text with triplet (start, repl, end)

    Example:

    >>> multi_subs_by_match('hello! peoples,', [5, 7, 14], [',', 'world', '!'], [6, 14, 15])
    'hello, world!'

    """
    # indexes are expected to be ordered, littlest first
    if ensure_input_order:
        starts, ends = list(starts), list(ends)
        assert sorted(starts) == starts, f"starts indexes are not ordered: {starts}"
        assert sorted(ends) == ends, f"ends indexes are not ordered: {ends}"

    def _run():
        curr = 0
        for start, repl, end in zip(starts, repls, ends):
            yield text[curr:start]
            yield repl
            curr = end
        yield text[curr:len(text)]  # yield the remaining text

    return ''.join(_run())


def multi_subs_by_regex(text: str, repls: dict[str, str]):
    """Sub given text with each given pair repl -> regex.

    >>> multi_subs_by_regex('hello world', {r'\\w+': 'gnap', r'\\s': '! ', '$': '!'})
    'gnap! gnap!'

    Warning: repls order has an effect. Example:

    >>> multi_subs_by_regex('ab', {'a': 'c', 'b': 'a'})
    'ca'
    >>> multi_subs_by_regex('ab', {'b': 'a', 'a': 'c'})
    'cc'

    """
    for pattern, repl in repls.items():
        text = re.sub(pattern, repl, text)
    return text


def multi_replace(text: str, words: dict) -> str:
    """Replace all given keys with their value in given text

    >>> multi_replace('aa aa a', {'aa': 'b', 'a': 'c'})
    'b b c'

    Note that the words needs to be separed:

    >>> multi_replace('aaaaa', {'aa': 'b', 'a': 'c'})
    'aaaaa'

    """
    from flashtext import KeywordProcessor
    kp = KeywordProcessor()
    for word, sub in words.items():
        kp.add_keyword(word, sub)
    return kp.replace_keywords(text)
