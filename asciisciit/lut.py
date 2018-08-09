"""
lut.py

Look up tables for asciisciit.

"""
from bisect import bisect

# LUMINANCE LUTS
LUM = {
    'SIMPLE': (
        " .'-:;!~*+em68g#WM@",
        [15, 25, 45, 60, 75, 90, 100, 115, 135, 155, 170, 185, 205, 220, 235, 245, 250]
    ),
    'BINARY': (
        " @",
        [128]
    ),
}

# COLOR

def bars(lut):
    """ Draws bars using the specified lut.
    """
    chars, lums = LUM[lut.upper()]
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


