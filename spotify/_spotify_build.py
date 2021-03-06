import os
from distutils.version import StrictVersion

import cffi

if StrictVersion(cffi.__version__) < StrictVersion("1.0.0"):
    raise RuntimeError(
        "pyspotify requires cffi >= 1.0, but found %s" % cffi.__version__
    )


header_file = os.path.join(os.path.dirname(__file__), "api.processed.h")

with open(header_file) as fh:
    header = fh.read()
    header += "#define SPOTIFY_API_VERSION ...\n"

ffi = cffi.FFI()
ffi.cdef(header)
ffi.set_source("spotify._spotify", '#include "libspotify/api.h"', libraries=["spotify"])


if __name__ == "__main__":
    ffi.compile()
