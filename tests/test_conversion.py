import itertools
from asciisciit import conversions as conv
from unicodedata import east_asian_width as eaw
import numpy as np
import pytest


@pytest.mark.parametrize("invert,equalize,lut",
                         itertools.product((True, False),
                                           (True, False),
                                           (u"simple", u"binary", u"\u3105\u3106\u3107")))
def test_pil_to_ascii(invert, equalize, lut):
    if eaw(lut[0]) in ["W", "F"]:
        correction = 2*conv.DEFAULT_ASPECT_CORRECTION_FACTOR
    else:
        correction = conv.DEFAULT_ASPECT_CORRECTION_FACTOR
    img = np.random.randint(0, 255, (480, 640), dtype=np.uint8)
    h, w = img.shape
    expected_len = int(h*0.5*correction)*(int(w*0.5)+1)+1
    img = conv.numpy_to_pil(img)
    text = conv.pil_to_ascii(img, 0.5, invert, equalize, lut)
    assert(len(text) == expected_len)


@pytest.mark.parametrize("invert,equalize,lut",
                         itertools.product((True, False),
                                           (True, False),
                                           (u"simple", u"binary", u"\u3105\u3106\u3107")))
def test_numpy_to_ascii(invert, equalize, lut):
    if eaw(lut[0]) in ["W", "F"]:
        correction = 2*conv.DEFAULT_ASPECT_CORRECTION_FACTOR
    else:
        correction = conv.DEFAULT_ASPECT_CORRECTION_FACTOR
    img = np.random.randint(0, 255, (480, 640), dtype=np.uint8)
    h, w = img.shape
    expected_len = int(h*0.5*correction)*(int(w*0.5)+1)+1
    text = conv.numpy_to_ascii(img, 0.5, invert, equalize, lut)
    assert(len(text) == expected_len)
