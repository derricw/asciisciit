"""

conversions.py

@author: derricw

Conversion functions.

"""
from bisect import bisect
import random
import os
import sys

from PIL import Image, ImageOps, ImageDraw, ImageFont
import numpy as np
import cv2
import imageio

from asciisciit.misc import *
from asciisciit.lut import LUM

RESOURCE_DIR = os.path.join(os.path.dirname(__file__),'res')

ASPECTCORRECTIONFACTOR = 6.0/11.0  # because text pixels are rectangular

PY2 = sys.version_info[0] < 3


def image_to_ascii(img, scalefactor=0.2, invert=False, equalize=True, lut='simple'):
    """
    Generates and ascii string from an image of some kind.

    Parameters
    ----------
    img : str, ndarray, PIL.Image
        Image to convert
    scalefactor : float
        ASCII chars per pixel
    invert : bool
        Invert luminance?
    equalize : bool
        Equalize histogram?

    Returns
    -------
    str

    Examples
    --------

    >>> ascii_img = image_to_ascii("http://i.imgur.com/l2FU2J0.jpg", scalefactor=0.3)
    >>> print(ascii_img)

    """
    if type(img) == str:
        img = open_pil_img(img)
    elif type(img) == np.ndarray:
        img = numpy_to_pil(img)
    try:
        text = pil_to_ascii(img, scalefactor, invert, equalize, lut)
    except:
        raise TypeError("That image type doesn't work.  Try PIL, Numpy, or file path...")
    return text


def pil_to_ascii(img,
                 scalefactor=0.2,
                 invert=False,
                 equalize=True,
                 lut='simple',
                 lookup_func=None
                 ):
    """
    Generates an ascii string from a PIL image.

    Parameters
    ----------
    img : PIL.Image
        PIL image to transform.
    scalefactor : float
        ASCII characters per pixel.
    invert : bool
        Invert luminance?
    equalize : bool
        equalize histogram (for best results do this).
    lut : str
        Name of the lookup table to use. Currently supports 'simple' and
        'binary'.
    lookup_func : function
        Method to use to perform lookup. The function should take an image and
        a lut string and return the converted ascii image. Defaults to
        `apply_lut_numpy`.

    Returns
    -------
    str

    Examples
    --------

    >>> from asciisciit.misc import open_pil_img
    >>> img = open_pil_img("http://i.imgur.com/l2FU2J0.jpg")
    >>> text_img = pil_to_ascii(img, scalefactor=0.3)
    >>> print(text_img)

    >>> from PIL import Image
    >>> img = Image.open("some_image.png")
    >>> text_img = pil_to_ascii(img)
    >>> print(text_img)

    """
    if lookup_func is None:
        lookup_func = apply_lut_numpy
    img = img.resize((int(img.size[0]*scalefactor), 
        int(img.size[1]*scalefactor*ASPECTCORRECTIONFACTOR)),
        Image.BILINEAR)
    img = img.convert("L")  # convert to mono
    if equalize:
        img = ImageOps.equalize(img)

    if invert:
        img = ImageOps.invert(img)

    return lookup_func(img, lut)


def ascii_to_pil(text, font_size=10, bg_color=(20, 20, 20),
                 fg_color=(255, 255, 255), font_path=None):
    """
    Renders Ascii text to an Image of the appropriate size, using text of the
        specified font size.

    Parameters
    ----------
    text : str
        Ascii text to render.
    font_size : int (10)
        Font size for rendered image.
    bg_color : tuple (20,20,20)
        (R,G,B) values for image background.
    fg_color : tuple (255,255,255)
        (R,G,B) values for text color.
    font_path : str
        Use a custom font .ttf file.

    Returns
    -------
    PIL.Image

    Examples
    --------

    >>> ascii = AsciiImage("http://i.imgur.com/l2FU2J0.jpg", scalefactor=0.4)
    >>> pil = ascii_to_pil(ascii.data)
    >>> pil.show()

    """
    #font = ImageFont.load_default()
    if not font_path:
        font_path = os.path.join(RESOURCE_DIR, "Cousine-Regular.ttf")

    font = ImageFont.truetype(font_path, font_size)
    font_width, font_height = font.getsize(" ")  # shape of 1 char

    img_height, img_width = get_ascii_image_size(text)

    y_padding = 1

    out_img = np.zeros(((font_height+y_padding)*img_height, 
                         font_width*img_width,
                         3),
                       dtype=np.uint8)
    out_img[:, :, 0] += bg_color[0]
    out_img[:, :, 1] += bg_color[1]
    out_img[:, :, 2] += bg_color[2]

    img = Image.fromarray(out_img)
    draw = ImageDraw.Draw(img)

    for index, line in enumerate(text.split("\n")):
        y = (font_height+y_padding)*index
        draw.text((0, y), line, fg_color, font=font)
    return img


def ascii_seq_to_gif(seq, output_path, fps=15.0, font_size=10):
    """ Creates a gif from a sequence of ascii images.

        Parameters
        ----------
        output_path : str
            Path for gif output.
        fps : float
            FPS for gif playback.
        font_size : int
            Font size for ascii.
    """
    images = []

    status = StatusBar(len(seq), text="Generating frames: ",)

    for index, ascii_img in enumerate(seq):
        if type(ascii_img) == str:
            #raw text
            text = ascii_img
        else:
            #AsciiImage instance
            text = ascii_img.data
        images.append(ascii_to_pil(text, font_size=font_size))
        status.update(index)

    status.complete()

    duration = 1.0/fps

    images_np = [np.array(img) for img in images]
    imageio.mimsave(output_path, images_np, duration=duration)


def numpy_to_ascii(img,
                   scalefactor=0.2,
                   invert=False,
                   equalize=True,
                   lut="simple"):
    """
    Generates an ascii string from a PIL image.

    Parameters
    ----------
    img : ndarray
        PIL image to transform.
    scalefactor : float
        ASCII characters per pixel.
    invert : bool
        Invert luminance?
    equalize : bool
        equalize histogram (for best results do this).
    lut : str
        Name of the lookup table to use. Currently supports 'simple' and
        'binary'.

    Returns
    -------
    str
    """
    h, w = img.shape

    img=cv2.resize(
        img, (int(w*scalefactor), int(h*scalefactor*ASPECTCORRECTIONFACTOR))
        )

    if img.ndim == 3: # weak check for RGB
        # works in opencv 3.4.3 but who knows, they keep moving/renaming stuff
        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    if equalize:
        img=cv2.equalizeHist(img)

    if invert:
        img = 255-img

    return apply_lut_numpy(img, lut)


def image_to_numpy(path):
    """
    Image file to numpy matrix.
    """
    img = open_pil_img(path)
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
    gif = open_pil_img(gif_path)
    if hasattr(gif, 'info'):
        frame_duration = gif.info.get('duration', None)
    else:
        frame_duration = None
    length = get_length_of_gif(gif)

    size = gif.size
    
    status = StatusBar(length, "Reading frames: ")

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
        status.update(frame_count)

    status.complete()

    assert(length==len(frames))

    final_frame_count = len(frames)
    frame1 = np.array(frames[0])
    shape = frame1.shape
    matrix = np.zeros((final_frame_count,shape[0],shape[1],shape[2]), dtype=np.uint8)
    for i, frame in enumerate(frames):
        img = np.asarray(frame)
        matrix[i] = img
    return matrix, frame_duration

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


def apply_lut_pil(img, lut="simple"):
    """
    Apply an ascii lookup table to an image by looping over pixels.

    Parameters
    ----------
    img : ndarray, PIL.Image
        Greyscale image to directly apply LUT to.
    lut : str
        Name of the lookup table to use. Currently supports 'simple' and
        'binary'.

    Returns
    -------
    str
    """
    if isinstance(img, np.ndarray):
        img = numpy_to_pil(img)

    text = "\n"

    chars, lums = LUM[lut.upper()]
    chars = list(chars)

    #SLOW ##TODO: USE Image.point(lut) instead
    for y in range(0, img.size[1]):
        for x in range(0, img.size[0]):
            lum = img.getpixel((x, y))
            row = bisect(lums, lum)
            character = chars[row]
            text += character
        text += "\n"

    return text


def apply_lut_numpy(img, lut="simple"):
    """
    Apply an ascii lookup table to an image using numpy chararrays.

    Parameters
    ----------
    img : ndarray, PIL.Image
        Greyscale image to directly apply LUT to.
    lut : str
        Name of the lookup table to use. Currently supports 'simple' and
        'binary'.

    Returns
    -------
    str
    """
    if isinstance(img, Image.Image):
        img = np.array(img, dtype=np.uint8)

    chars, lums = LUM[lut.upper()]
    lums = np.array(lums)
    if PY2:
        chars = np.chararray(len(chars), buffer=chars)
    else:
        # all my attempts to read the character buffer as unicode failed to
        # correctly populate the chararray, so here we are...
        chars = np.chararray(len(chars), buffer=bytes(chars, "utf-8"))

    text = np.chararray((img.shape[0], img.shape[1]+1))
    text[:,-1] = "\n"
    text[:,:-1] = chars[np.digitize(img, lums)]

    return "\n" + text.tostring().decode("utf-8")


if __name__ == '__main__':
    pass
