
import itertools
import xml.etree.ElementTree as ET


def asdict(xml: str, *, sep: str = '/', del_brace_tag: bool = True, whole_keys: bool = False) -> dict:
    """Return a dict equivalent to input XML.

    del_brace_tag -- False to not keep the braced namespace identifiers
    whole_keys -- True to keep the full identifiers, not removing the non-discriminating ones

    """
    out = _asdict(ET.fromstring(xml), root=[], sep=sep, del_brace_tag=del_brace_tag)
    if whole_keys:
        return out
    # remove non-discriminating levels
    ret = {}
    for level in itertools.count(1):
        if not out: break
        key_sub_and_dat = [(k, k[-level:], v) for k, v in out.items()]
        found = [sk for _, sk, __ in key_sub_and_dat]
        for k, sk, v in key_sub_and_dat:
            assert found.count(sk) >= 1, found
            if found.count(sk) == 1:  # no doublons !
                ret['/'.join(sk)] = v
                del out[k]
    return ret


def _asdict(xml: ET.Element, root: list[str], sep: str, del_brace_tag: bool) -> dict:
    "The recursive XML reader implementation ; WARNING: it is dumb"
    newroot = root + [xml.tag.split('}')[-1] if del_brace_tag else xml.tag]
    if len(xml) == 0:
        return {tuple(newroot): xml.text}
    ret = {}
    for sub in xml:
        ret.update(_asdict(sub, newroot, sep, del_brace_tag))
    return ret
