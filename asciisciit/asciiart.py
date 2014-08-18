'''

ASCII Toolbox for Converting Images, Movies, Gifs, and Video Feed

Created on 14 Aug 2014

@author: Derric Williams

'''

import time
import os
import platform
from subprocess import Popen, PIPE
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
            return get_ascii_image_size(self.data)
        else:
            return object.__getattribute__(self, name)

    def to_file(self, path):
        with open(path, "w+") as f:
            f.write(self.data)

    def render(self, path, font_size=10, bg_color=(20,20,20), fg_color=(255,255,255)):
        img = ascii_to_pil(self.data, font_size, bg_color, fg_color)
        img.save(path)

    def show(self):
        print(self.data)


class AsciiMovie(object):
    """
    Movie object for playing and rendering movies.

    Parameters
    ----------
    movie_path : str
        File path for movie
    scalefactor : float
        Scale of the image in chars / pixel
    invert : bool
        Invert image before processing

    Examples
    --------

    

    """

    def __init__(self, movie_path, scalefactor=0.2, invert=False):
        self.movie_path = movie_path
        self.scalefactor = scalefactor
        self.invert = invert

        if type(self.movie_path) == str:
            # movie is a file
            _,ext = os.path.splitext(self.movie_path)

            if ext == ".gif":
                self.data = gif_to_numpy(self.movie_path)
                self.shape = self.data.shape
                self.play = self._play_gif
                self.render = self._render_to_gif
            elif ext in  [".mp4", ".avi"]:
                self.play = self._play_movie
                self.render = self._render_to_movie
        else:
            raise("movie_path must be a string")

        self.frame_intervals = []
        self.draw_times = []

    def _play_gif(self, fps=15, repeats=1):
        seq = generateSequence(self.data, scalefactor=self.scalefactor)
        if repeats < 0:
            while True:
                playSequence(seq, fps)
        else:
            for i in range(repeats):
                playSequence(seq, fps)

    def _play_movie(self, fps=15, repeats=1):
        if repeats < 0:
            repeats = 1  # lets just play movies once by default
        for i in range(repeats):
            video = cv2.VideoCapture(self.movie_path)
            frame = 0
            t = time.clock()
            while 1:
                result, image = video.read()
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
                draw_time = time.clock()-t
                t = time.clock()
                remaining = 1.0/fps-draw_time
                if remaining > 0:
                    time.sleep(remaining)
                    interval = draw_time+remaining
                else:
                    interval = draw_time
                self.frame_intervals.append(interval)
                self.draw_times.append(draw_time)

            print("Total frames displayed:", frame)
            print("Avg draw time:", np.mean(self.draw_times))
            print("Avg frame interval:", np.mean(self.frame_intervals))
            print("Max frame interval:", np.max(self.frame_intervals))
            print("Min frame interval:", np.min(self.frame_intervals))

            video.release()

    def _render_to_gif(self, output_path, font_size=10):
        """
        Render text to gif of text.

        Parameters
        ----------
        output_path : str
            Where to write the gif.

        """
        seq = generateSequence(self.data, scalefactor=self.scalefactor)
        ascii_seq_to_gif(seq, output_path, font_size=font_size)

    def _render_to_movie(self, output_path, fourcc=None, fps=24,
                         font_size=10):
        """

        """
        video = cv2.VideoCapture(self.movie_path)
        frames = 0
        
        status = StatusBar(text='Counting frames: ')

        #get # of frames and img size
        while 1:
            result, frame = video.read()
            if type(frame) != np.ndarray:
                break
            if frames == 0:
                #get resulting image size once
                ascii_img = AsciiImage(frame, scalefactor=self.scalefactor,
                       invert=self.invert)
                pil_img = ascii_to_pil(ascii_img.data)
                img_size = pil_img.size
            frames += 1
            status.update_custom(frames)
        video.release()

        status.complete()

        #status = StatusBar(frames, "Rendering frames: ")

        video = cv2.VideoCapture(self.movie_path)

        # opencv solution?
        # if not fourcc:
        #     fourcc = fourcc = cv2.cv.CV_FOURCC(*'MPEG')
        # output = cv2.VideoWriter(output_path, -1, fps, img_size, 1)

        # ffmpeg solution
        p = Popen(['ffmpeg', '-y', '-f', 'image2pipe', '-vcodec',
                   'mjpeg', '-r', str(fps), '-i', '-', '-vcodec',
                   'mpeg4', '-qscale', '5', '-r', str(fps), output_path],
                   stdin=PIPE)

        for i in range(frames):
            result, frame = video.read()
            if type(frame) != np.ndarray:
                break
            if result:
                ascii_img = AsciiImage(frame, scalefactor=self.scalefactor,
                                       invert=self.invert)
                pil_img = ascii_to_pil(ascii_img.data, font_size=font_size)
                pil_img.save(p.stdin, 'JPEG')
                #numpy_img = np.array(pil_img)
                #output.write(numpy_img)  # opencv
                #status.update(i)
            else:
                break

        video.release()
        #output.release()  # opencv
        p.stdin.close()
        p.wait()

        #status.complete()


class AsciiCamera(object):

    def __init__(self, camera_id=0, scalefactor=0.2, invert=False):
        self.scalefactor = scalefactor
        self.invert = invert
        self.camera_id = camera_id

        #webcam?
        self.video = cv2.VideoCapture(self.camera_id)

        self.frame_intervals = []
        self.draw_times = []

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
            draw_time = time.clock()-t
            t = time.clock()
            remaining = 1.0/fps-draw_time
            if remaining > 0:
                time.sleep(remaining)
                interval = draw_time+remaining
            else:
                interval = draw_time
            self.frame_intervals.append(interval)
            self.draw_times.append(draw_time)

        print("Total frames displayed:", frame)
        print("Avg draw time:", np.mean(self.draw_times))
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