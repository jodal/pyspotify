from __future__ import unicode_literals

import sys

from spotify import ffi, lib


PY3 = sys.version_info[0] == 3

if PY3:
    text_type = str
    binary_type = bytes
else:
    text_type = unicode
    binary_type = str


def enum(prefix):
    def wrapper(obj):
        for attr in dir(lib):
            if attr.startswith(prefix):
                setattr(obj, attr.replace(prefix, ''), getattr(lib, attr))
        return obj
    return wrapper


def to_bytes(value):
    if isinstance(value, text_type):
        return value.encode('utf-8')
    elif isinstance(value, binary_type):
        return value
    else:
        raise ValueError('Value must be a string')


def to_unicode(chars):
    return ffi.string(chars).decode('utf-8')
