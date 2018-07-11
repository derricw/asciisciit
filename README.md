asciisciit
===========

## ASCII Art, Video, and Plotting Toolbox

Ever wanted to convert gifs to text and then back into gifs again?

Ever wanted to convert movies to text and watch them in your terminal?

Ever wanted to stream your webcam into your terminal as text?

Me neither.

But now I can!

![costner](http://i.imgur.com/lncbpBm.gif)

## Installation

Install with pip to make sure you get the dependencies.

    $ pip install asciisciit

## Use

#### Examples to run!

Convert a gif to ascii and render it back to gif in 8 point font:

    $>asciit dealwithit.gif ascii_render.gif -p 8

Display webcam feed from camera 0 in a new terminal, with histogram equalization:

    $>asciit -w 0 --n --e

Play a video file in a new terminal, scale to 0.15 characters per pixel, display at 24 fps:

    $>asciit cats.mp4 -s 0.15 --n -f 24.0

Convert a video to ascii

### Using the module

#### Images

    >>> from asciisciit.asciiart import AsciiImage
    >>> img = AsciiImage("my_img.png")
    >>> print(img)
    >>> img.render("output.png", fontsize=8, bg_color=(20,20,20), fg_color=(255,255,255))

#### Gifs

    >>> from asciisciit.asciiart import AsciiMovie
    >>> gif = AsciiMovie("my_gif.gif", scalefactor=0.2)
    >>> gif.play(fps=15.0)  #play at 15 fps
    >>> gif.render("ouput.gif", fps=15.0, fontsize=8)

#### Movies

    >>> from asciisciit.asciiart import AsciiMovie
    >>> movie = AsciiMovie("my_movie.avi", scalefactor=0.2)
    >>> movie.play(fps=24.0)
    >>> movie.render("output.avi", fps=24.0, fontsize=8)

## TODO:

1. Color
1. gifv and other file types

