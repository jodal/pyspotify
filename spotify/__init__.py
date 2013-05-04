from __future__ import unicode_literals

import os

import cffi


__version__ = '2.0.0a1'


_header_file = os.path.join(os.path.dirname(__file__), 'api.processed.h')
_header = open(_header_file).read()
_header += '#define SPOTIFY_API_VERSION ...\n'
ffi = cffi.FFI()
ffi.cdef(_header)
lib = ffi.verify('#include "libspotify/api.h"', libraries=[str('spotify')])



from spotify.error import *  # noqa
