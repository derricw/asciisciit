"""
lut.py

Look up tables for asciisciit.

"""
import os
import sys
import numpy as np
from PIL import ImageFont
from unicodedata import east_asian_width as eaw
from bisect import bisect

PY2 = sys.version_info[0] < 3
RESOURCE_DIR = os.path.join(os.path.dirname(__file__),'res')


RELATIVE_WIDTHS = {
    "W": 2,
    "F": 2,
    "H": 1,
    "Na": 1,
}


def relative_width(char):
    return RELATIVE_WIDTHS.get(eaw(char), None)


class LUT(object):
    def __init__(self, chars, bins):
        if PY2 and isinstance(chars, str):
            chars = chars.decode("unicode_escape")
        assert(len(chars) == len(bins) + 1)
        widths = [relative_width(char) for char in chars]
        if not len(set(widths)) == 1:
            raise ValueError("All characters in lookup must share width (determined from east_asian_width)")
        if widths[0] is None: # don't actually know how wide these are
            raise ValueError("Lookup made of of unsupport width")
        self._chars = np.chararray(len(chars), unicode=True)
        for i, char in enumerate(chars):
            self._chars[i] = char
        self._bins = np.array(bins, dtype=np.uint8)

    @property
    def exemplar(self):
        return self._chars.tolist()[0]

    def legacy_lookup(self):
        """Return legacy LUT form (chars, bins)."""
        return self._chars.tolist(), self._bins.tolist()

    def apply(self, img):
        text = np.chararray((img.shape[0], img.shape[1]+1), unicode=True)
        text[:,-1] = u"\n"
        text[:,:-1] = self._chars[np.digitize(img, self._bins)]

        return text


def linear_lut(chars):
    # probably needs some stricter validation
    width = 255.0 / (len(chars) - 1)
    bins = np.linspace(width/2, 255 - width/2, len(chars) - 1, dtype=np.uint8)
    return LUT(chars, bins)


# LUMINANCE LUTS
UNICODE_LUTS = {
    u'SIMPLE': LUT(
        " .'-:;!~*+em68g#WM@",
        [15, 25, 45, 60, 75, 90, 100, 115, 135, 155, 170, 185, 205, 220, 230, 240, 245, 250]
        ),
    u'BINARY': LUT(
        " @",
        [128]
    ),
    u'CJK': linear_lut(u"\u3000\u4e36\u4e37\u4e4a\u4e41\u4e42\u4e49\u4e46\u4e65\u4eb2\u4eb7")
}


def get_lut(string):
    global UNICODE_LUTS
    if PY2 and isinstance(string, str):
        string = string.decode("unicode_escape")
    lut = UNICODE_LUTS.get(string.upper(), None)
    # Create a linear lookup and name 
    if not lut:
        lut = linear_lut(string)
        UNICODE_LUTS[string.upper()] = lut # cache lookup

    return lut


def bars(lut):
    """ Draws bars using the specified lut."""
    chars, lums = get_lut(lut).legacy_lookup()
    chars = list(chars)
    arr = list(range(0, 255, 2))
    line = ""
    for v in arr:
        row = bisect(lums, v)
        character = chars[row]
        line += character
    for _ in range(5):
        print(line)


def main():
    import sys
    if len(sys.argv) > 1:
        lut = sys.argv[1]
    else:
        lut = 'simple'
    bars(lut)

if __name__ == '__main__':
    main()
