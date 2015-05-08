from __future__ import unicode_literals

import binascii
import sys
import threading


__version__ = '2.0.0b5'


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


class _SerializedLib(object):
    """CFFI library wrapper to serialize all calls to library functions.

    Internal class.
    """

    def __init__(self, lib):
        for name in dir(lib):
            attr = getattr(lib, name)
            if name.startswith('sp_') and callable(attr):
                attr = serialized(attr)
            setattr(self, name, attr)


def _get_cffi_modulename(header, source, sys_version):
    """Create CFFI module name that does not depend on CFFI version."""
    key = '\x00'.join([sys.version[:3], source, header])
    key = key.encode('utf-8')
    k1 = hex(binascii.crc32(key[0::2]) & 0xffffffff)
    k1 = k1.lstrip('0x').rstrip('L')
    k2 = hex(binascii.crc32(key[1::2]) & 0xffffffff)
    k2 = k2.lstrip('0').rstrip('L')
    return str('_spotify_cffi_%s%s' % (k1, k2))  # Native string type on Py2/3


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

    source = '#include "libspotify/api.h"'

    ffi = cffi.FFI()
    ffi.cdef(header)
    lib = ffi.verify(
        source,
        modulename=_get_cffi_modulename(header, source, sys.version),
        libraries=[str('spotify')],
        ext_package='spotify')

    lib = _SerializedLib(lib)

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
from spotify.offline import *  # noqa
from spotify.player import *  # noqa
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
