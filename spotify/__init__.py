from __future__ import unicode_literals

import os

from cffi import FFI


__version__ = '2.0.0a1'


header_file = os.path.join(os.path.dirname(__file__), 'api.processed.h')
header = open(header_file).read()
ffi = FFI()
ffi.cdef(header)
lib = ffi.verify('#include "libspotify/api.h"', libraries=[str('spotify')])
