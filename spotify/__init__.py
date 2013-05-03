from __future__ import unicode_literals

import os

from cffi import FFI


__version__ = '2.0.0a1'


header_file = os.path.join(os.path.dirname(__file__), 'api.processed.h')
header = open(header_file).read()
header += '#define SPOTIFY_API_VERSION ...\n'

ffi = FFI()
ffi.cdef(header)
lib = ffi.verify('#include "libspotify/api.h"', libraries=[str('spotify')])


def _to_text(chars):
    return ffi.string(chars).decode('utf-8')


def _add_enum(obj, prefix):
    for attr in dir(lib):
        if attr.startswith(prefix):
            setattr(obj, attr.replace(prefix, ''), getattr(lib, attr))


class Error(Exception):
    def __init__(self, error_code):
        self.error_code = error_code
        message = _to_text(lib.sp_error_message(error_code))
        super(Error, self).__init__(message)

_add_enum(Error, 'SP_ERROR_')
