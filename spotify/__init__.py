from __future__ import unicode_literals

import logging
import os
import weakref

import cffi


__version__ = '2.0.0a1'


# Log to nowhere by default. For details, see:
# http://docs.python.org/2/howto/logging.html#library-config
logging.getLogger('spotify').addHandler(logging.NullHandler())


_header_file = os.path.join(os.path.dirname(__file__), 'api.processed.h')
_header = open(_header_file).read()
_header += '#define SPOTIFY_API_VERSION ...\n'
ffi = cffi.FFI()
ffi.cdef(_header)
lib = ffi.verify('#include "libspotify/api.h"', libraries=[str('spotify')])


# Mapping between keys and objects that should be kept alive as long as the key
# is alive. May be used to keep objects alive when there isn't a more
# convenient place to keep a reference to it. The keys are weakrefs, so entries
# disappear from the dict when the key is garbage collected, potentially
# causing objects associated to the key to be garbage collected as well. For
# further details, refer to the CFFI docs.
global_weakrefs = weakref.WeakKeyDictionary()


from spotify.error import *  # noqa
from spotify.session import *  # noqa
