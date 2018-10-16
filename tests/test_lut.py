from asciisciit import lut
import pytest


@pytest.mark.parametrize("lut_name", ("simple", "binary", "\u3105\u3106\u3107"))
def test_bars(lut_name):
    lut.bars(lut_name)


def test_linear_lut():
    l = lut.linear_lut("123456789")
    assert(len(l._chars) == 9)
    assert(len(l._bins) == 8)


def test_get_lut():
    assert(u"\u3105\u3106\u3107\u3108" not in lut.ASCII_LUTS)
    l1 = lut.get_lut("\u3105\u3106\u3107\u3108")
    assert(u"\u3105\u3106\u3107\u3108" in lut.ASCII_LUTS)
    l2 = lut.get_lut("\u3105\u3106\u3107\u3108")


def test_lut():
    with pytest.raises(AssertionError):
        l = lut.LUT("abc", [1])
    with pytest.raises(AssertionError):
        l = lut.LUT("abc", [1, 2, 3])
    with pytest.raises(AssertionError):
        l = lut.LUT("abc", [1, 2, 3, 4])
    # mix a narrow character with a wide character
    with pytest.raises(ValueError):
        l = lut.LUT("\uff73\u3106\u4e19", [1, 2])
    # unsupported character width
    with pytest.raises(ValueError):
        l = lut.LUT("\u22d8\u22d8\u22d8", [1, 2])
