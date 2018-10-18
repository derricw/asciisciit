import itertools
from asciisciit import asciiart as aart
import numpy as np
import pytest


@pytest.mark.parametrize("output,scalefactor,invert,equalize,lut",
                         itertools.product((True, False),
                                           (0.1, 0.2),
                                           (True, False),
                                           (True, False),
                                           (u"simple", u"binary", u"\u3105\u3106\u3107")))
def test_ascii_image(output, scalefactor, invert, equalize, lut, tmpdir_factory):
    # basic integration test to confirm this doesn't completely fall down
    img = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    aimg = aart.AsciiImage(img, scalefactor, invert, equalize, lut)
    assert(aimg.data)
    assert(aimg.lut == lut)
    if aart.PY2:
        assert(unicode(aimg) == aimg.data)
        assert(str(aimg))
    else:
        assert(str(aimg) == aimg.data)
    if output:
        tpath = str(tmpdir_factory.mktemp("test").join("test.txt"))
        aimg.to_file(tpath)
        ipath = str(tmpdir_factory.mktemp("test").join("test.png"))
        aimg.render(ipath)
