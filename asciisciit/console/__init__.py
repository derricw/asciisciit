import platform

if "linux" in platform.system().lower():
    from .linux import *
else:
    from .windows import *
