"""

misc.py

@author: derricw

Miscellaneous IO functions.

"""

import sys
import io
if sys.version_info < (3, 0):
    from urllib2 import urlopen
else:
    from urllib.request import urlopen

import cv2
from PIL import Image


def open_pil_img(path, *args, **kwargs):
    """
    Opens a PIL image from a file or the web. We have to do this because
        PIL doesn't (yet) support web paths.

    Parameters
    ----------
    path : str
        File or web path to open

    All other arguments are passed to Image.open()

    """
    try:
        #probably a file
        img = Image.open(path, *args, **kwargs)
    except IOError:
        #perhaps it is a web address?
        fd = urlopen(path)
        image_file = io.BytesIO(fd.read())
        img = Image.open(image_file, *args, **kwargs)
    return img


def get_movie_size_pix(movie_path):
    video = cv2.VideoCapture(movie_path)
    _, frame = video.read()
    shape = frame.shape
    video.release()
    return (shape[1], shape[0])  # reversed because numpy


def get_gif_size_pix(gif_path):
    gif = open_pil_img(gif_path)
    shape = gif.size
    return (shape[0], shape[1])


def get_img_size_pix(img_path):
    img = open_pil_img(img_path)
    shape = img.size
    return (shape[0], shape[1])


def get_ascii_image_size(text):
    lines = text.split("\n")
    rows = len(lines)
    columns = len(lines[1])
    return (rows, columns)


def get_length_of_gif(gif):
    if type(gif) == str:
        gif = open_pil_img(gif)
    else:
        gif = gif
    frames = 0
    while gif:
        try:
            gif.seek(frames)
            frames += 1
        except EOFError:
            break
    gif.seek(0)
    return frames


class StatusBar(object):

    def __init__(self, length=0, text=""):
        self.length = length
        self.text = text

    def update(self, index):
        percent_complete = 1.0*index/self.length*100
        sys.stdout.write("\r%s%d%% " % (self.text, percent_complete))
        sys.stdout.flush()

    def complete(self):
        sys.stdout.write("\r%s%d%% " % (self.text, 100))
        sys.stdout.flush()
        print("...FINISHED")

    def update_custom(self, index):
        sys.stdout.write("\r%s%d " % (self.text, index))


if __name__ == '__main__':
    pass
