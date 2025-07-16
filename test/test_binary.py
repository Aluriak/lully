
import sys
from lully import xor_merge

def test_xor_merge():
    # key is cycled to get enough bytes to xor the whole text:
    assert xor_merge('aa', 'b') == xor_merge(text='aa', key='bb')
    # xor same data leads to zero bytes
    assert int.from_bytes(xor_merge('a', 'a'), byteorder=sys.byteorder) == 0
