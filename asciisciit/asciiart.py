'''

ASCII Toolbox for Converting Images, Movies, Gifs, and Video Feed

Created on 14 Aug 2014

@author: Derric Williams

'''

import time
import os
import platform
import cv2
from PIL import Image, ImageOps
import numpy as np

from conversions import *

if "linux" in platform.system().lower():
    from linux_backend import *
else:
    from windows_backend import *


class AsciiImage(object):
    """
    An image representation of single frame or image file.

    Parameters
    ----------
    image : str, np.ndarray, PIL.Image
        Image to convert to text
    scalefactor : float
        Scale factor for image.  Units are chars/pixel, automatically adjusted
        for the rectangular-ness of characters.
    invert : bool
        Whether to invert the intensity values
    equalize : True
        Equalize the image histogram to increase contrast.  I suggest always
        setting this to true.

    Returns
    -------
    AsciiImage

    Examples
    --------

    >>> ascii = AsciiImage('rubyrhod.jpeg')
    >>> print(ascii)

    """
    def __init__(self, image, scalefactor=0.1, invert=False, equalize=True):
        self.data = image_to_ascii(image, scalefactor, invert, equalize)

    def __repr__(self):
        return self.data

    def __getattribute__(self, name):
        if name == "size":
            lines = self.data.split("\n")
            rows = len(lines)
            columns = len(lines[1])
            return (rows, columns)
        else:
            return object.__getattribute__(self, name)


class AsciiMovie(object):

    def __init__(self, movie_path, scalefactor=0.2, invert=False):
        self.movie_path = movie_path
        self.scalefactor = scalefactor
        self.invert = invert

        if type(self.movie_path) == str:
            # movie is a file
            _,ext = os.path.splitext(self.movie_path)

            if ext == ".gif":
                data = gif_to_numpy(self.movie_path)
                self.sequence = generateSequence(data, scalefactor=scalefactor)
                self.shape = data.shape
                self.play = self._play_gif
            elif ext in  [".mp4", ".avi"]:
                self.play = self._play_movie
        else:
            raise("movie_path must be a string")

        self.frame_intervals = []

    def _play_gif(self, fps=15, repeats=1):
        if repeats < 0:
            while True:
                playSequence(self.sequence, fps)
        else:
            for i in range(repeats):
                playSequence(self.sequence, fps)

    def _play_movie(self, fps=15, repeats=1):
        if repeats < 0:
            repeats = 1  # lets just play movies once by default
        for i in range(repeats):
            self.video = cv2.VideoCapture(self.movie_path)
            frame = 0
            t = time.clock()
            while 1:
                result, image = self.video.read()
                if type(image) != np.ndarray:
                    print("End of movie.")
                    break
                if result:
                    ascii_img = AsciiImage(image, scalefactor=self.scalefactor,
                                           invert=self.invert)
                    #set terminal size on the first image?
                    if frame == 0:
                        try:
                            set_terminal_size(ascii_img.size)
                        except:
                            pass
                    clear_term()
                    print(ascii_img)
                    frame += 1
                else:
                    break
                interval = time.clock()-t
                t = time.clock()
                remaining = 1.0/fps-interval
                if remaining > 0:
                    time.sleep(remaining)
                self.frame_intervals.append(interval)
            print("Total frames displayed:", frame)
            print("Avg frame interval:", np.mean(self.frame_intervals))
            print("Max frame interval:", np.max(self.frame_intervals))
            print("Min frame interval:", np.min(self.frame_intervals))

            self.video.release()

    def render(self, output_path, fourcc=None, fps=15):
        pass

    def _render_gif(self):
        pass

    def _render_movie(self):
        pass


class AsciiCamera(object):

    def __init__(self, camera_id=0, scalefactor=0.2, invert=False):
        self.scalefactor = scalefactor
        self.invert = invert
        self.camera_id = camera_id

        #webcam?
        self.video = cv2.VideoCapture(self.camera_id)

        self.frame_intervals = []

    def stream(self, fps=15.0):
        frame = 0
        t = time.clock()
        while 1:
            result, image = self.video.read()
            if type(image) != np.ndarray:
                if frame == 0:
                    raise IOError("No frames available. Bro, do you even camera?")
                ##TODO: find some way to break out besides ^C
                print("End of movie.")
                break
            if result:
                ascii_img = AsciiImage(image, scalefactor=self.scalefactor,
                                       invert=self.invert)
                #set terminal size on the first image?
                if frame == 0:
                    try:
                        set_terminal_size(ascii_img.size)
                    except:
                        pass
                clear_term()
                print(ascii_img)
                frame += 1
            else:
                break
            interval = time.clock()-t
            t = time.clock()
            remaining = 1.0/fps-interval
            if remaining > 0:
                time.sleep(remaining)
            self.frame_intervals.append(interval)
        print("Total frames displayed:", frame)
        print("Avg frame interval:", np.mean(self.frame_intervals))
        print("Max frame interval:", np.max(self.frame_intervals))
        print("Min frame interval:", np.min(self.frame_intervals))

        self.video.release()


def generateSequence(imageseq, scalefactor=0.1):
    seq = []
    for im in imageseq:
        seq.append(AsciiImage(im, scalefactor))
    return seq


def playSequence(seq, fps=30, repeats=1):
    shape = seq[0].size
    set_terminal_size(shape)
    t = time.clock()
    for im in seq:
        clear_term()
        print(im)
        interval = time.clock()-t
        remaining = 1.0/fps-interval
        if remaining > 0:
            time.sleep(remaining)



if __name__ == '__main__':
    pass