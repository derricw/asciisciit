asciisciit
===========

## ASCII Art, Video, and Plotting Toolbox

Ever wanted to convert gifs to text and then back into gifs again?

Ever wanted to convert movies to text and watch them in your terminal?

Ever wanted to stream your webcam into your terminal as text?

Me neither.

But now I can!

![costner](http://i.imgur.com/lncbpBm.gif)
![wrunner](http://i.imgur.com/LrGqxRg.png =500x)

## Installation

### Requirements

[Pillow](https://pillow.readthedocs.org/en/latest/)

Get the latest version of Pillow.  <=2.0.0 has issues writing gifs.

[Numpy](http://www.numpy.org/)

[OpenCV](http://opencv.org/)

### Setup

Install with:

    python setup.py install

## Use

### CLI

#### Windows

##### Manual

Add ".py" to the PATHEXT environment variable.

Add the package directory to PATH.

##### Automatic

#### Linux

##### Manual

Link ascii.py like so:

    $>ln -s 'python /path/to/ascii.py' asciit

##### Automatic


#### Examples to run!



### Using the module

#### Images

    >>> from asciisciit.asciiart import AsciiImage
    >>> img = AsciiImage("my_img.png")
    >>> print img
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

## Known Issues

1. Sometimes gifs look really wonkey.  Especially ones with superimposed text.  I blame PIL.

![traincat](http://i.imgur.com/TIFHP.gif)