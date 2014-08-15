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
        size_str = "mode %s,%s" % (height+1, width+1)
        os.system(size_str)
    except Exception as e:
        print("Failed to scale window: %s" % e)


def new_term(command, size=None):
    os.system("start %s" % command)

if __name__ == '__main__':
    pass