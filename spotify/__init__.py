from __future__ import unicode_literals

import os
import re

from cffi import FFI


__version__ = '2.0.0a1'


def parse_header():
    header_file = os.path.join(os.path.dirname(__file__), 'api.h')
    header = open(header_file).read()

    api = []
    includes = ['#include "libspotify/api.h"']

    # Flags to keep state while iterating header file lines
    cpp = False
    win32 = False

    # Remove multiline comments
    header = re.sub('\/\*.*?\*\/', '', header, flags=re.DOTALL)

    for line in header.splitlines():

        # Remove blank lines
        if len(line.strip()) == 0:
            continue

        # Remove C++ blocks
        if line.startswith('#ifdef __cplusplus'):
            cpp = True
            continue
        if cpp:
            if line.startswith('#endif') or line.startswith('#else'):
                cpp = False
            continue
        if line.startswith('#if !defined(__cplusplus)'):
            continue

        # Remove Windows blocks
        if line.startswith('#ifdef _WIN32'):
            win32 = True
            continue
        if win32:
            if line.startswith('#endif') or line.startswith('#else'):
                win32 = False
            continue

        # Build separate list of #include lines
        if line.startswith('#include'):
            includes.append(line)
            continue

        # Ignore PUBLIC_API_H definition
        if line.startswith('#ifndef PUBLIC_API_H'):
            continue
        if line.startswith('#define PUBLIC_API_H'):
            continue

        # Search and replace SP_CALLCONV
        if line.startswith('#ifndef SP_CALLCONV'):
            continue
        if line.startswith('#define SP_CALLCONV'):
            continue
        line = line.replace('SP_CALLCONV ', '')

        # Search and replace SP_LIBEXPORT
        if line.startswith('#ifndef SP_LIBEXPORT'):
            continue
        if line.startswith('#define SP_LIBEXPORT(x) x'):
            continue
        line = re.sub('SP_LIBEXPORT\(([^)]*)\)', lambda x: x.groups()[0], line)

        # Remove unmatched #endif lines
        if line.startswith('#endif'):
            continue

        # Remove macro which can be reimplemented in Python
        if line.startswith('#define SP_TOPLIST_REGION(a, b)'):
            continue

        # Make the API version macro available
        line = re.sub(
            '#define SPOTIFY_API_VERSION \d+',
            '#define SPOTIFY_API_VERSION ...',
            line)

        # Remove inline comments
        line = re.sub('\s*\/\/\/\< .*', '', line)

        # Remove trailing whitespace
        line = re.sub('\s*$', '', line)

        api.append(line)

    api = '\n'.join(api)
    includes = '\n'.join(includes)

    return dict(api=api, includes=includes)


header = parse_header()
ffi = FFI()
ffi.cdef(header['api'])
lib = ffi.verify(header['includes'], libraries=[str('spotify')])
