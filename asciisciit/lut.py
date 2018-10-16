"""
lut.py

Look up tables for asciisciit.

"""
import sys
import numpy as np
from unicodedata import east_asian_width as eaw
from bisect import bisect

PY2 = sys.version_info[0] < 3


class LUT(object):
    def __init__(self, chars, bins):
        if PY2 and isinstance(chars, str):
            chars = chars.decode("unicode_escape")
        assert(len(chars) == len(bins) + 1)
        widths = [eaw(char) for char in chars]
        if not len(set(widths)) == 1:
            raise ValueError("All characters in lookup must share east_asian_width")
        if widths[0] in ["A", "N"]: # don't actually know how wide these are
            raise ValueError("Lookup made of of unsupport width {}".format(widths[0]))
        self._chars = np.chararray(len(chars), unicode=True)
        for i, char in enumerate(chars):
            self._chars[i] = char
        self._bins = np.array(bins, dtype=np.uint8)

    def native_data(self):
        """Return legacy LUT form (chars, bins)."""
        return self._chars.tolist(), self._bins.tolist()

    def apply(self, img):
        text = np.chararray((img.shape[0], img.shape[1]+1), unicode=True)
        text[:,-1] = u"\n"
        text[:,:-1] = self._chars[np.digitize(img, self._bins)]

        return text


# LUMINANCE LUTS
ASCII_LUTS = {
    'SIMPLE': LUT(
        " .'-:;!~*+em68g#WM@",
        [15, 25, 45, 60, 75, 90, 100, 115, 135, 155, 170, 185, 205, 220, 230, 240, 245, 250]
        ),
    'BINARY': LUT(
        " @",
        [128]
    )
}


def linear_lut(chars):
    # probably needs some stricter validation
    width = 255.0 / (len(chars) - 1)
    bins = np.linspace(width/2, 255 - width/2, len(chars) - 1, dtype=np.uint8)
    return LUT(chars, bins)


def get_lut(string):
    lut = ASCII_LUTS.get(string.upper(), None)
    if lut:
        print(u"Using predefined LUT '{}'".format(string))
    else:
        print(u"Creating linear LUT from string '{}'".format(string))
        if PY2:
            string = string.decode("unicode_escape")
        lut = linear_lut(string)

    return lut


def bars(lut):
    """ Draws bars using the specified lut."""
    chars, lums = get_lut(lut).native_data()
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
