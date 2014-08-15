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
from asciiart import *
from windows_backend import new_term

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Convert Images, Movies, Gifs, Plots to ASCII')
    parser.add_argument('infile', nargs='?', type=str)
    parser.add_argument('outfile', nargs='?', type=str)
    parser.add_argument('-r', type=int, help='Number of repeats',
                        default=1)
    parser.add_argument('-s', type=float, help='Scale factor',
                        default=0.2)
    parser.add_argument('-i', type=bool, help='Invert Luminance',
                        default=False)
    parser.add_argument('-w', type=int, help='Webcam ID')
    parser.add_argument('-e', type=bool, help='Equalize Histogram',
                        default=True)
    parser.add_argument('-f', type=float, help='Target FPS', default=15.0)
    parser.add_argument('--n', help='New terminal', action='store_true')
    args = parser.parse_args()
    args_dict = vars(args)
    #new window?
    if args_dict['n']:
        call = sys.argv.remove("--n")
        call_str = " ".join(sys.argv)
        new_term(call_str)  # call in new terminal without --n
    else:
        #a file to open?
        if args_dict['infile']:
            _,ext = os.path.splitext(args_dict['infile'])
            if ext in [".gif", ".mp4"]:
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
        elif type(args_dict['w']) == int:
            task = AsciiCamera(args_dict['w'],
                               scalefactor=args_dict['s'],
                               invert=args_dict['i'])
            task.stream(fps=args_dict['f'])
