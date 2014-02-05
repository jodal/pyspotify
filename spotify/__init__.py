from __future__ import unicode_literals

from distutils.version import StrictVersion
import functools
import logging
import os
import threading

import cffi


if StrictVersion(cffi.__version__) < StrictVersion('0.7'):
    raise RuntimeError(
        'pyspotify requires cffi >= 0.7, but found %s' % cffi.__version__)


__version__ = '2.0.0a1'


# Log to nowhere by default. For details, see:
# http://docs.python.org/2/howto/logging.html#library-config
logging.getLogger('spotify').addHandler(logging.NullHandler())


# Global reentrant lock to be held whenever libspotify functions are called or
# libspotify owned data is worked on. This is the heart of pyspotify's thread
# safety.
_lock = threading.RLock()


# Reference to the spotify.Session instance. Used to enforce that one and only
# one session exists in each process.
session_instance = None


def serialized(f):
    """Acquires the global lock while calling the wrapped function.

    Internal function.
    """
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        with _lock:
            return f(*args, **kwargs)
    return wrapper


def serialize_access_to_library(lib):
    """Modify CFFI library to serialize all calls to library functions.

    Internal function.
    """
    for name in dir(lib):
        if name.startswith('sp_') and callable(getattr(lib, name)):
            setattr(lib, name, serialized(getattr(lib, name)))


def build_ffi():
    """Build CFFI instance with knowledge of all libspotify types and a library
    object which wraps libspotify for use from Python.

    Internal function.
    """
    header_file = os.path.join(os.path.dirname(__file__), 'api.processed.h')
    header = open(header_file).read()
    header += '#define SPOTIFY_API_VERSION ...\n'

    ffi = cffi.FFI()
    ffi.cdef(header)
    lib = ffi.verify(
        '#include "libspotify/api.h"',
        libraries=[str('spotify')],
        ext_package='spotify')

    serialize_access_to_library(lib)

    return ffi, lib


ffi, lib = build_ffi()


from spotify.album import *  # noqa
from spotify.artist import *  # noqa
from spotify.audio import *  # noqa
from spotify.config import *  # noqa
from spotify.connection import *  # noqa
from spotify.error import *  # noqa
from spotify.image import *  # noqa
from spotify.inbox import *  # noqa
from spotify.link import *  # noqa
from spotify.offline import *  # noqa
from spotify.playlist import *  # noqa
from spotify.search import *  # noqa
from spotify.session import *  # noqa
from spotify.social import *  # noqa
from spotify.toplist import *  # noqa
from spotify.track import *  # noqa
from spotify.user import *  # noqa
