from __future__ import unicode_literals

import functools
import logging
import os
import threading
import weakref

import cffi


__version__ = '2.0.0a1'


# Log to nowhere by default. For details, see:
# http://docs.python.org/2/howto/logging.html#library-config
logging.getLogger('spotify').addHandler(logging.NullHandler())


# Global reentrant lock to be held whenever libspotify functions are called or
# libspotify owned data is worked on. This is the heart of pyspotify's thread
# safety.
_lock = threading.RLock()


def serialized(f):
    """Acquires the global lock while calling the wrapped function.

    Internal function.
    """
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        with _lock:
            return f(*args, **kwargs)
    return wrapper


_header_file = os.path.join(os.path.dirname(__file__), 'api.processed.h')
_header = open(_header_file).read()
_header += '#define SPOTIFY_API_VERSION ...\n'

ffi = cffi.FFI()
ffi.cdef(_header)
lib = ffi.verify(
    '#include "libspotify/api.h"',
    libraries=[str('spotify')],
    ext_package='spotify')

for name in dir(lib):
    attr = getattr(lib, name)
    if callable(attr):
        setattr(lib, name, serialized(attr))


# Mapping between keys and objects that should be kept alive as long as the key
# is alive. May be used to keep objects alive when there isn't a more
# convenient place to keep a reference to it. The keys are weakrefs, so entries
# disappear from the dict when the key is garbage collected, potentially
# causing objects associated to the key to be garbage collected as well. For
# further details, refer to the CFFI docs.
weak_key_dict = weakref.WeakKeyDictionary()


# Reference to the spotify.Session instance. Used to enforce that one and only
# one session exists in each process.
session_instance = None


from spotify.album import *  # noqa
from spotify.artist import *  # noqa
from spotify.audio import *  # noqa
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
