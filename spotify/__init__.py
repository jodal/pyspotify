from __future__ import unicode_literals

import threading


__version__ = '2.0.0b2'


# Global reentrant lock to be held whenever libspotify functions are called or
# libspotify owned data is worked on. This is the heart of pyspotify's thread
# safety.
_lock = threading.RLock()


# Reference to the spotify.Session instance. Used to enforce that one and only
# one session exists in each process.
_session_instance = None


def _setup_logging():
    """Setup logging to log to nowhere by default.

    For details, see:
    http://docs.python.org/3/howto/logging.html#library-config

    Internal function.
    """
    import logging

    logger = logging.getLogger('spotify')
    handler = logging.NullHandler()
    logger.addHandler(handler)


def serialized(f):
    """Decorator that serializes access to all decorated functions.

    The decorator acquires pyspotify's single global lock while calling any
    wrapped function. It is used to serialize access to:

    - All calls to functions on :attr:`spotify.lib`.

    - All code blocks working on pointers returned from functions on
      :attr:`spotify.lib`.

    - All code blocks working on other internal data structures in pyspotify.

    Together this is what makes pyspotify safe to use from multiple threads and
    enables convenient features like the :class:`~spotify.EventLoop`.

    Internal function.
    """
    import functools

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        with _lock:
            return f(*args, **kwargs)
    if not hasattr(wrapper, '__wrapped__'):
        # Workaround for Python < 3.2
        wrapper.__wrapped__ = f
    return wrapper


def _serialize_access_to_library(lib):
    """Modify CFFI library to serialize all calls to library functions.

    Internal function.
    """
    for name in dir(lib):
        if name.startswith('sp_') and callable(getattr(lib, name)):
            setattr(lib, name, serialized(getattr(lib, name)))


def _build_ffi():
    """Build CFFI instance with knowledge of all libspotify types and a library
    object which wraps libspotify for use from Python.

    Internal function.
    """
    from distutils.version import StrictVersion
    import os

    import cffi

    if StrictVersion(cffi.__version__) < StrictVersion('0.7'):
        raise RuntimeError(
            'pyspotify requires cffi >= 0.7, but found %s' % cffi.__version__)

    header_file = os.path.join(os.path.dirname(__file__), 'api.processed.h')
    with open(header_file) as fh:
        header = fh.read()
        header += '#define SPOTIFY_API_VERSION ...\n'

    ffi = cffi.FFI()
    ffi.cdef(header)
    lib = ffi.verify(
        '#include "libspotify/api.h"',
        libraries=[str('spotify')],
        ext_package='spotify')

    _serialize_access_to_library(lib)

    return ffi, lib


_setup_logging()
ffi, lib = _build_ffi()


from spotify.album import *  # noqa
from spotify.artist import *  # noqa
from spotify.audio import *  # noqa
from spotify.config import *  # noqa
from spotify.connection import *  # noqa
from spotify.error import *  # noqa
from spotify.eventloop import *  # noqa
from spotify.image import *  # noqa
from spotify.inbox import *  # noqa
from spotify.link import *  # noqa
from spotify.playlist import *  # noqa
from spotify.playlist_container import *  # noqa
from spotify.playlist_track import *  # noqa
from spotify.playlist_unseen_tracks import *  # noqa
from spotify.search import *  # noqa
from spotify.session import *  # noqa
from spotify.sink import *  # noqa
from spotify.social import *  # noqa
from spotify.toplist import *  # noqa
from spotify.track import *  # noqa
from spotify.user import *  # noqa
from spotify.version import *  # noqa
