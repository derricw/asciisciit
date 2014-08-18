#!/usr/bin/env python
"""

ascii.py

@author: derricw

CLI for main functionality of asciisciit library.

Examples
--------

    ascii.py movie.mp4 -s 0.2 -f 30.0

    ascii.py dealwithit.gif -s 0.2 -f 15.0

    ascii.py -w 0 --n

"""

import argparse
import sys
import os
import platform

if "linux" in platform.system().lower():
    from linux_backend import *
else:
    from windows_backend import *

from asciiart import *
from misc import *

MOVIES = [".mp4", '.avi', '.mpg', '.mpeg']
IMAGES = ['.png', '.jpeg', '.jpg', '.tif', '.bmp']
GIFS = ['.gif']

def main():
    parser = argparse.ArgumentParser(
        description='Convert Images, Movies, Gifs, Plots to ASCII')
    parser.add_argument('infile', nargs='?', type=str)
    parser.add_argument('outfile', nargs='?', type=str)
    parser.add_argument('-r', type=int, help='Number of repeats',
                        default=-1)
    parser.add_argument('-s', type=float, help='Scale factor',
                        default=0.2)
    parser.add_argument('-i', type=bool, help='Invert Luminance',
                        default=False)
    parser.add_argument('-w', type=int, help='Webcam ID', default=-1)
    parser.add_argument('-e', type=bool, help='Equalize Histogram',
                        default=True)
    parser.add_argument('-f', type=float, help='Target FPS', default=15.0)
    parser.add_argument('-p', type=int, help='Font render point size', default=10)
    parser.add_argument('--n', help='New terminal', action='store_true')
    args = parser.parse_args()
    args = vars(args)
    print(args)
    #new terminal
    if args['n']:
        sys.argv.remove("--n")
        call_str = " ".join(sys.argv)

        #have to get the size here because we have to set linux terminal size
        #   when we instantiate the terminal because i can't figure out how
        #   to do it after the terminal is created like we do in Winderps
        sf = args['s']
        if args['w'] > -1:
            size = get_movie_size_pix(args['w'])
            
        elif args['infile']:
            infile = args['infile']
            _,ext = os.path.splitext(infile)
            ext = ext.lower()
            if ext in MOVIES:
                size = get_movie_size_pix(infile)
            elif ext in GIFS:
                size = get_gif_size_pix(infile)
            elif ext in IMAGES:
                size = get_img_size_pix(infile)
            else:
                size = None
        else:
            size = None
        if size:
            size = (int(size[0]*sf), int(size[1]*sf*ASPECTCORRECTIONFACTOR))

        new_term(call_str, size)  # call in new terminal without --n argument

    #same terminal
    else:

        #a file to open?
        if args['infile']:
            _,ext = os.path.splitext(args['infile'])
            ext = ext.lower()
            if ext in MOVIES+GIFS:
                task = AsciiMovie(args['infile'],
                                  scalefactor=args['s'],
                                  invert=args['i'])
                if args['outfile']:
                    task.render(args['outfile'],
                                fps=args['f'],
                                font_size=args['p'])
                else:
                    task.play(repeats=args['r'],
                              fps=args['f'])
                    raw_input("")
            elif ext in IMAGES:
                task = AsciiImage(args['infile'],
                                  scalefactor=args['s'],
                                  invert=args['i'],
                                  equalize=args['e'])
                if args['outfile']:
                    task.render(args['outfile'],
                                font_size=args['p'])
                else:
                    task.show()
                    raw_input("")
            else:
                print("Unknown file format.Try:", MOVIES+IMAGES+GIFS)

        #a webcam?
        elif args['w'] > -1:
            task = AsciiCamera(args['w'],
                               scalefactor=args['s'],
                               invert=args['i'])
            task.stream(fps=args['f'])

if __name__ == '__main__':
    main()