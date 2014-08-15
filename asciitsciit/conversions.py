"""

conversions.py

@author: derricw

Bunch of random conversion functions.

"""

from PIL import Image, ImageOps
import numpy as np
from bisect import bisect
import random
import cv2
import matplotlib.pyplot as plt


GREYSCALE_RANDOM = [
    " ",
    ". ",
    ",-",
    "_ivc=!/|\\~",
    "gjezt*+",
    "2](YL)[T7Vf",
    "mdK4",
    "mdK4ZGbN",
    "DXY5P"
    "#%$"
    "W8KMA",

    ]

GREYSCALE_UNIFORM = [
    " ",
    ".",
    "'",
    "-",
    ":",
    ";",
    "!",
    "~",
    "*",
    "+",
    "e",
    "m",
    "6",
    "8",
    "g",
    "#",
    "W",
    "M",
    "@",
]

BINS = [15, 25, 45, 60, 75, 90, 100, 115, 135, 155, 170, 185, 205, 220, 235,
        245, 250]

ASPECTCORRECTIONFACTOR = 6.0/11.0  # because text pixels are rectangular


def image_to_ascii(img, scalefactor=0.1, invert=False, equalize=True):
    """
    Generates and ascii string from an image of some kind.
    """
    if type(img) == str:
        img=Image.open(img)
        text = pil_to_ascii(img, scalefactor, invert, equalize)
    elif type(img) == np.ndarray:
        #text = numpy_to_ascii(img, scalefactor, invert, equalize)  #WHY IS THIS SLOWER?
        text = pil_to_ascii(numpy_to_pil(img), scalefactor, invert, equalize)
    else:
        try:
            pil_to_ascii(img, scalefactor, invert, equalize)
        except:
            raise TypeError("That image type doesn't work.  Try PIL, Numpy, or file path...")
    return text


def pil_to_ascii(img, scalefactor=0.1, invert=False, equalize=True):
    """
    Generates an ascii string from a PIL image.

    Parameters
    ----------
    img : PIL.Image
        PIL image to transform.
    scalefactor : float
        ASCII characters per pixel
    invert : bool
        Invert luminance?
    equalize : bool
        equalize histogram (for best results do this)

    Returns
    -------
    str

    Examples
    --------

    >>> from PIL import Image
    >>> img = Image.open("some_image.png")
    >>> text_img = pil_to_ascii(img)

    """
    size = img.size
    img=img.resize((int(img.size[0]*scalefactor), 
        int(img.size[1]*scalefactor*ASPECTCORRECTIONFACTOR)),
        Image.BILINEAR)
    img=img.convert("L") # convert to mono
    if equalize:
        img=ImageOps.equalize(img)

    if invert:
        img = ImageOps.invert(img)

    text=""

    ##TODO: custom LUT
    lut = GREYSCALE_UNIFORM

    #SLOW REWRITE USING ONLY NUMPY
    for y in range(0,img.size[1]):
        for x in range(0,img.size[0]):
            lum=img.getpixel((x,y))
            row=bisect(BINS,lum)
            character=lut[row]
            text+=character
        text+="\n"

    return text


def numpy_to_ascii(img, scalefactor=0.1, invert=False, equalize=True):
    """
    Generates and ascii string from a numpy image.

    SLOW FOR SOME REASON SO I DONT USE IT.

    """
    size = img.shape 

    img=cv2.resize(img, (int(size[1]*scalefactor), 
        int(size[0]*scalefactor*ASPECTCORRECTIONFACTOR)))

    img = cv2.cvtColor(img,cv2.cv.CV_RGB2GRAY)

    if equalize:
        img=cv2.equalizeHist(img)

    if not invert:
        img = 255-img

    text=""

    lut = GREYSCALE_UNIFORM

    #SLOW REWRITE USING ONLY NUMPY
    for y in range(img.shape[0]):
        for x in range(img.shape[1]):
            lum=img[y,x]
            row=bisect(BINS,lum)
            character=lut[row]
            text+=character
        text+="\n"

    return text


def image_to_numpy(path):
    """
    Image file to numpy matrix.
    """
    img = Image.open(path)
    return np.array(img, dtype=np.uint8)

def numpy_to_pil(nparray):
    """
    Numpy matrix to PIL Image.
    """
    return Image.fromarray(nparray)


def gif_to_numpy(gif_path):
    """
    Converts a GIF into a numpy movie.
    """
    gif = Image.open(gif_path)
    size = gif.size
    frames = []
    frame_count = 0
    while gif:
        new_img = Image.new("RGBA",size)
        new_img.paste(gif)
        frames.append(new_img)
        frame_count += 1
        try:
            gif.seek(frame_count)
        except EOFError:
            break
    final_frame_count = len(frames)
    frame1 = np.array(frames[0])
    shape = frame1.shape
    matrix = np.zeros((final_frame_count,shape[0],shape[1],shape[2]), dtype=np.uint8)
    for i, frame in enumerate(frames):
        img = np.asarray(frame)
        matrix[i] = img
    return matrix

def figure_to_numpy(mpl_figure):
    """
    Converts a matplotlib figure to numpy matrix.
    """
    mpl_figure.tight_layout(pad=0.1)
    mpl_figure.canvas.draw()
    data = np.fromstring(mpl_figure.canvas.tostring_rgb(), dtype=np.uint8, sep='')
    data = data.reshape(mpl_figure.canvas.get_width_height()[::-1]+ (3,))
    return data

def figure_to_ascii(mpl_figure):
    """
    Converts a matplotlib figure to ascii image.
    """
    npy_fig = figure_to_numpy(mpl_figure)
    return image_to_ascii(npy_fig, scalefactor=0.15, invert=False, equalize=False)


if __name__ == '__main__':
    
    path = "/home/derricw/Pictures/derricwcats.jpg"

    ascii = image_to_ascii(path)

    print ascii

    img = image_to_numpy(path)
    ascii = numpy_to_ascii(img, scalefactor=0.1)
    print ascii

