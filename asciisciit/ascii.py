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

if __name__ == '__main__':
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
    parser.add_argument('--n', help='New terminal', action='store_true')
    args = parser.parse_args()
    args_dict = vars(args)
    print args_dict
    #new terminal
    if args_dict['n']:
        call = sys.argv.remove("--n")
        call_str = " ".join(sys.argv)

        #have to get the size here because we have to set linux terminal size
        #   when we instantiate the terminal because i can't figure out how
        #   to do it after the terminal is created like we do in Winderps
        sf = args_dict['s']
        if args_dict['w'] > -1:
            size = get_movie_size_pix(args_dict['w'])
            
        elif args_dict['infile']:
            infile = args_dict['infile']
            _,ext = os.path.splitext(infile)
            if ext in [".mp4",'.avi']:
                size = get_movie_size_pix(infile)
            elif ext in ['.gif']:
                size = get_gif_size_pix(infile)
            elif ext in ['.jpeg','.png','.jpg','.tif']:
                size = get_img_size_pix(infile)
            else:
                size = None
        else:
            size = None
        if size:
            size = (int(size[0]*sf), int(size[1]*sf*ASPECTCORRECTIONFACTOR))

        new_term(call_str,size)  # call in new terminal without --n argument
    #same terminal
    else:
        #a file to open?
        if args_dict['infile']:
            _,ext = os.path.splitext(args_dict['infile'])
            if ext in [".gif", ".mp4", '.avi']:
                task = AsciiMovie(args_dict['infile'],
                                  scalefactor=args_dict['s'],
                                  invert=args_dict['i'])
                task.play(repeats=args_dict['r'],
                          fps=args_dict['f'])
            elif ext in ['.png', '.jpeg', '.jpg', '.tif']:
                task = AsciiImage(args_dict['infile'],
                                  scalefactor=args_dict['s'],
                                  invert=args_dict['i'],
                                  equalize=args_dict['e'])
                print(task)
        #a webcam?
        elif args_dict['w'] > -1:
            task = AsciiCamera(args_dict['w'],
                               scalefactor=args_dict['s'],
                               invert=args_dict['i'])
            task.stream(fps=args_dict['f'])
