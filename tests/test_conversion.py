import itertools
from asciisciit import conversions as conv
import numpy as np
import pytest


@pytest.mark.parametrize("invert,equalize,lut,lookup_func",
                         itertools.product((True, False),
                                           (True, False),
                                           ("simple", "binary"),
                                           (None, conv.apply_lut_pil)))
def test_pil_to_ascii(invert, equalize, lut, lookup_func):
    img = np.random.randint(0, 255, (480, 640), dtype=np.uint8)
    h, w = img.shape
    expected_len = int(h*0.5*conv.ASPECTCORRECTIONFACTOR)*(int(w*0.5)+1)+1
    img = conv.numpy_to_pil(img)
    text = conv.pil_to_ascii(img, 0.5, invert, equalize, lut, lookup_func)
    assert(len(text) == expected_len)


@pytest.mark.parametrize("invert,equalize,lut",
                         itertools.product((True, False),
                                           (True, False),
                                           ("simple", "binary")))
def test_numpy_to_ascii(invert, equalize, lut):
    img = np.random.randint(0, 255, (480, 640), dtype=np.uint8)
    h, w = img.shape
    expected_len = int(h*0.5*conv.ASPECTCORRECTIONFACTOR)*(int(w*0.5)+1)+1
    text = conv.numpy_to_ascii(img, 0.5, invert, equalize, lut)
    assert(len(text) == expected_len)


def test_lookup_method_equivalency():
    img = np.random.randint(0, 255, (300,300), dtype=np.uint8)

    pil_ascii = conv.apply_lut_pil(img)
    np_ascii = conv.apply_lut_numpy(img)
    assert(pil_ascii == np_ascii)

    pil_ascii = conv.apply_lut_pil(img, "binary")
    np_ascii = conv.apply_lut_numpy(img, "binary")
    assert(pil_ascii == np_ascii)
