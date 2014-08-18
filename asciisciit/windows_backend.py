"""

windows_backend.py

@author: derricw

Windows support functions.

"""

import os


def clear_term():
    os.system("cls")


def set_terminal_size(size):
    try:
        width, height = size
        #size_str = "mode %s,%s" % (height+1, width+1)
        cols_str = "mode con: cols=%s" % (height+1)
        rows_str = "mode con: lines=%s" % (width+1)
        os.system(cols_str)
        os.system(rows_str)
    except Exception as e:
        print("Failed to scale window: %s" % e)


def new_term(command, size=None):
    """
    the window set_terminal_size works so we don't 
        have to do anything with the size
    """
    os.system("start %s" % command)

if __name__ == '__main__':
    pass