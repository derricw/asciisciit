'''
ASCII Art maker
Creates an ascii art image from an arbitrary image
Created on 7 Sep 2009

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

    def __init__(self, *args, **kwargs):
        self.data = image_to_ascii(*args, **kwargs)

    def __repr__(self):
        return self.data

    def __getattribute__(self, name):
        if name == "size":
            lines = self.data.split("\n")
            rows = len(lines)
            columns = len(lines[0])
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
            elif ext == ".mp4":
                self.play = self._play_movie
        else:
            raise("movie_path must be a string")

        self.frame_intervals = []

    def _play_gif(self, fps=15, repeats=1):
        for i in range(repeats):
            playSequence(self.sequence, fps)

    def _play_movie(self, fps=15, repeats=1):
        for i in range(repeats):
            self.video = cv2.VideoCapture(self.movie_path)
            frame = 0
            while 1:
                t = time.clock()
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
                    time.sleep(1.0/fps)
                    frame += 1
                else:
                    break
                interval = time.clock()-t
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
        while 1:
            t = time.clock()
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
                time.sleep(1.0/fps)
                frame += 1
            else:
                break
            interval = time.clock()-t
            self.frame_intervals.append(interval)
        print("Total frames displayed:", frame)
        print("Avg frame interval:", np.mean(self.frame_intervals))
        print("Max frame interval:", np.max(self.frame_intervals))
        print("Min frame interval:", np.min(self.frame_intervals))

        self.video.release()


def generateSequence(imageseq, scalefactor=0.1, lut_type='uniform'):
    seq = []
    for im in imageseq:
        seq.append(AsciiImage(im,scalefactor,lut_type))
    return seq


def playSequence(seq, fps=30, repeats=1):
    shape = seq[0].size
    set_terminal_size(shape)
    for im in seq:
        clear_term()
        print(im)
        time.sleep(1.0/fps)



if __name__ == '__main__':

    """ SINGLE IMAGE
    img = "/home/derricw/Images/1367475599016.jpg"
    text = AsciiImage(img)
    print text
    print text.size
    print text.derp
    """
    """ GIF
    #gif_to_convert = "/home/derricw/Pictures/2zHFLFx.gif"
    gif_to_convert = r"C:\Users\derricw\Pictures\wrestler.gif"
    
    movie = AsciiMovie(gif_to_convert, scalefactor=0.5)
    movie.play(repeats=4)

    """
    """ MATPLOTLIB PLOT
    import matplotlib.pyplot as plt
    f = plt.figure()
    x = np.arange(0,10,0.1)
    y = np.sin(x)
    plt.plot(x,y, linewidth=5.0)
    #plt.axis("off")
    ascii_fig = figure_to_ascii(f)
    print ascii_fig
    """
    #""" MOVIE
    movie_path = "/home/derricw/Downloads/20131014 GomSweater.mp4"
    movie = AsciiMovie(movie_path, scalefactor=0.15)
    movie.play(fps=30.0)
    #"""

    """ WEBCAM
    movie = AsciiCamera(0, scalefactor=0.20)
    movie.stream(fps=15.0)
    """