'''Wrapper for D:\projects\dvr\src\mediacodec\ffmpeg

Generated with:
wrap.py D:\projects\dvr\src\mediacodec\ffmpeg.h

Do not modify this file.
'''

__docformat__ =  'restructuredtext'
__version__ = '$Id$'

import ctypes
from ctypes import *

import pyglet.lib

_lib = pyglet.lib.load_library('D:\\projects\\dvr\\src\\mediacodec\\ffmpeg')

_int_types = (c_int16, c_int32)
if hasattr(ctypes, 'c_int64'):
    # Some builds of ctypes apparently do not have c_int64
    # defined; it's a pretty good bet that these builds do not
    # have 64-bit pointers.
    _int_types += (ctypes.c_int64,)
for t in _int_types:
    if sizeof(t) == sizeof(c_size_t):
        c_ptrdiff_t = t

class c_void(Structure):
    # c_void_p is a buggy return type, converting to int, so
    # POINTER(None) == c_void_p is actually written as
    # POINTER(c_void), so it can be treated as a real pointer.
    _fields_ = [('dummy', c_int)]



StreamByte_t = c_ubyte 	# D:\projects\dvr\src\mediacodec\ffmpeg.h:18
# D:\projects\dvr\src\mediacodec\ffmpeg.h:98
InitLib = _lib.InitLib
InitLib.restype = c_int
InitLib.argtypes = []

# D:\projects\dvr\src\mediacodec\ffmpeg.h:99
Cleanup = _lib.Cleanup
Cleanup.restype = None
Cleanup.argtypes = []

# D:\projects\dvr\src\mediacodec\ffmpeg.h:117
SeekToTime = _lib.SeekToTime
SeekToTime.restype = c_int
SeekToTime.argtypes = [c_int]


__all__ = ['StreamByte_t', 'InitLib', 'Cleanup', 'SeekToTime']
