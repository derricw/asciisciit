from asciisciit import conversions as conv
import numpy as np


def test_lookup_method_equivalency():
    img = np.random.randint(0, 255, (300,300), dtype=np.uint8)

    pil_ascii = conv.apply_lut_pil(img)
    np_ascii = conv.apply_lut_numpy(img)
    assert(pil_ascii == np_ascii)

    pil_ascii = conv.apply_lut_pil(img, "binary")
    np_ascii = conv.apply_lut_numpy(img, "binary")
    assert(pil_ascii == np_ascii)