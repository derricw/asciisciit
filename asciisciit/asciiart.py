#!/usr/bin/env python
'''

ASCII Toolbox for Converting Images, Movies, Gifs, and Video Feed

Created on 14 Aug 2014

@author: Derric Williams

'''

from __future__ import print_function

import time
import os
import platform
from subprocess import Popen, PIPE
import io

import cv2
import numpy as np

from asciisciit.conversions import *
from asciisciit.lut import get_lut, PY2
import asciisciit.console as console


class AsciiImage(object):
    """
    An image representation of single frame or image file.

    Parameters
    ----------
    image : str, np.ndarray, PIL.Image
        Image to convert to text.  Can be file path, numpy array, or PIL image
    scalefactor : float
        Scale factor for image.  Units are chars/pixel, automatically adjusted
        for the rectangular-ness of characters.
    invert : bool
        Whether to invert the intensity values
    equalize : True
        Equalize the image histogram to increase contrast.  This should be set
        to True for most images.


    Examples
    --------

    >>> ascii = AsciiImage('rubyrhod.jpeg')
    >>> print(ascii)

    """
    def __init__(self,
                 image,
                 scalefactor=0.1,
                 invert=False,
                 equalize=True,
                 lut='simple',
                 font_path=None):
        self.image = image
        self.scalefactor = scalefactor
        self.invert = invert
        self.equalize = equalize
        self.font_path = font_path
        self.aspect_correction_factor = DEFAULT_ASPECT_CORRECTION_FACTOR
        self._lut = None
        self.lut = lut

    @property
    def data(self):
        return image_to_ascii(self.image,
                              self.scalefactor,
                              self.invert,
                              self.equalize,
                              self.lut,
                              self.aspect_correction_factor)

    @property
    def size(self):
        return get_ascii_image_size(self.data)

    @property
    def lut(self):
        return self._lut

    @lut.setter
    def lut(self, val):
        self._lut = val
        lookup = get_lut(val)
        self.aspect_correction_factor = get_aspect_correction_factor(
            lookup.exemplar, self.font_path) # default correction factor for converting

    def __repr__(self):
        if PY2:
            return self.data.encode('utf-8') # error otherwise
        return self.data

    def __unicode__(self):
        return self.data

    def to_file(self, path):
        with io.open(path, "w+") as f:
            f.write(self.data)

    def render(self, path, font_size=10, bg_color=(20,20,20), fg_color=(255,255,255)):
        img = ascii_to_pil(self.data, font_size, bg_color, fg_color, font_path=self.font_path)
        img.save(path)

    def show(self, resize_term=False, rescale=False):
        if resize_term:
            try:
                console.set_terminal_size(self.size)
            except:
                pass
        print(self.data)


class AsciiMovie(object):
    """
    Movie object for playing and rendering movies.

    Parameters
    ----------
    movie_path : str
        File path or web address for movie.
    scalefactor : float
        Scale of the image in chars / pixel
    invert : bool
        Invert image before processing

    Examples
    --------

    >>> movie = AsciiMovie('awesome_movie.avi')
    >>> movie.play(fps=24.0)

    """

    def __init__(self,
                 movie_path,
                 scalefactor=0.2,
                 invert=False,
                 equalize=True,
                 lut='simple',
                 font_path=None):

        self.movie_path = movie_path
        self.scalefactor = scalefactor
        self.invert = invert
        self.equalize = equalize
        self.font_path = font_path
        self.aspect_correction_factor = DEFAULT_ASPECT_CORRECTION_FACTOR
        self._lut = lut
        self.lut = lut
        self.default_fps = 15.0

        if type(self.movie_path) == str:
            # movie is a file
            _ , ext = os.path.splitext(self.movie_path)

            if ext == ".gif":
                self.data, frame_duration = gif_to_numpy(self.movie_path)
                self.default_fps = 1000.0/frame_duration
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

    @property
    def lut(self):
        return self._lut

    @lut.setter
    def lut(self, val):
        self._lut = val
        lookup = get_lut(val)
        self.aspect_correction_factor = get_aspect_correction_factor(
            lookup.exemplar, self.font_path) # default correction factor for converting

    def _play_gif(self, fps=None, repeats=-1):
        fps = fps or self.default_fps
        seq = generate_sequence(self.data,
                                scalefactor=self.scalefactor,
                                invert=self.invert,
                                equalize=self.equalize,
                                lut=self.lut,
                                font_path=self.font_path)
        if repeats < 0:
            while True:
                play_sequence(seq, fps)
        else:
            for i in range(repeats):
                play_sequence(seq, fps)

    def _play_movie(self, fps=None, repeats=1):
        fps = fps or self.default_fps
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
                    ascii_img = AsciiImage(image,
                                           scalefactor=self.scalefactor,
                                           invert=self.invert,
                                           equalize=self.equalize,
                                           lut=self.lut,
                                           font_path=self.font_path)
                    #set terminal size on the first image?
                    if frame == 0:
                        try:
                            console.set_terminal_size(ascii_img.size)
                        except:
                            pass
                    console.clear_term()
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

    def _render_to_gif(self, output_path, fps=None, font_size=10):
        """
        Render text to gif of text.

        Parameters
        ----------
        output_path : str
            Output file path.

        """
        fps = fps or self.default_fps
        seq = generate_sequence(self.data,
                                scalefactor=self.scalefactor,
                                invert=self.invert,
                                equalize=self.equalize,
                                lut=self.lut,
                                font_path=self.font_path)
        ascii_seq_to_gif(seq,
                         output_path,
                         fps=fps,
                         font_size=font_size,
                         font_path=self.font_path)

    def _render_to_movie(self,
                         output_path,
                         fourcc=None,
                         fps=None,
                         font_size=10):
        """

        """
        fps = fps or self.default_fps
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
                ascii_img = AsciiImage(frame,
                                       scalefactor=self.scalefactor,
                                       invert=self.invert,
                                       equalize=self.equalize,
                                       lut=self.lut,
                                       font_path=self.font_path)
                pil_img = ascii_to_pil(ascii_img.data, font_path=self.font_path)
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
                ascii_img = AsciiImage(frame,
                                       scalefactor=self.scalefactor,
                                       invert=self.invert,
                                       equalize=self.equalize,
                                       lut=self.lut,
                                       font_path=self.font_path)
                pil_img = ascii_to_pil(ascii_img.data,
                                       font_size=font_size,
                                       font_path=self.font_path)
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

    def __init__(self,
                 camera_id=0,
                 scalefactor=0.2,
                 invert=False,
                 equalize=True,
                 lut="simple"):
        self.scalefactor = scalefactor
        self.invert = invert
        self.camera_id = camera_id
        self.equalize = equalize
        self.lut = lut

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
                ascii_img = AsciiImage(image,
                                       scalefactor=self.scalefactor,
                                       invert=self.invert,
                                       equalize=self.equalize,
                                       lut=self.lut)
                #set terminal size on the first image?
                if frame == 0:
                    try:
                        console.set_terminal_size(ascii_img.size)
                    except:
                        pass
                console.clear_term()
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

        self.release()

    def release(self):
        self.video.release()


def generate_sequence(imageseq,
                      scalefactor=0.1,
                      invert=False,
                      equalize=True,
                      lut='simple',
                      font_path=None):
    seq = []
    for im in imageseq:
        seq.append(
            AsciiImage(
                im,
                scalefactor,
                invert=invert,
                equalize=equalize,
                lut=lut,
                font_path=font_path
            )
        )
    return seq


def play_sequence(seq, fps=30, repeats=1):
    shape = seq[0].size
    console.set_terminal_size(shape)
    t = time.clock()
    for im in seq:
        console.clear_term()
        print(im)
        interval = time.clock()-t
        t = time.clock()
        remaining = 1.0/fps-interval
        if remaining > 0:
            time.sleep(remaining)


if __name__ == '__main__':
    pass
 
