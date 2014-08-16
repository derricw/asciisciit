"""

misc.py

@author: derricw

Random crap that doesn't belong anywhere else.

"""

import cv2
from PIL import Image


def get_movie_size_pix(movie_path):
    video = cv2.VideoCapture(movie_path)
    _,frame = video.read()
    shape = frame.shape
    video.release()
    return (shape[1],shape[0])

def get_gif_size_pix(gif_path):
    gif = Image.open(gif_path)
    shape = gif.size
    return (shape[0],shape[1])

def get_img_size_pix(img_path):
    img = Image.open(img_path)
    shape = img.size
    return (shape[0],shape[1])


if __name__ == '__main__':
    pass
