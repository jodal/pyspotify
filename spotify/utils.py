from __future__ import unicode_literals

import sys

from spotify import ffi, lib


PY2 = sys.version_info[0] == 2

if PY2:
    text_type = unicode
    binary_type = str
else:
    text_type = str
    binary_type = bytes


def enum(prefix):
    def wrapper(obj):
        for attr in dir(lib):
            if attr.startswith(prefix):
                setattr(obj, attr.replace(prefix, ''), getattr(lib, attr))
        return obj
    return wrapper


def get_with_growing_buffer(func, obj):
    actual_length = 10
    buffer_length = actual_length
    while actual_length >= buffer_length:
        buffer_length = actual_length + 1
        buffer_ = ffi.new('char[%d]' % buffer_length)
        actual_length = func(obj, buffer_, buffer_length)
    if actual_length == -1:
        return None
    return to_unicode(buffer_)


def to_bytes(value):
    if isinstance(value, text_type):
        return value.encode('utf-8')
    elif isinstance(value, binary_type):
        return value
    else:
        raise ValueError('Value must be a string')


def to_unicode(chars):
    return ffi.string(chars).decode('utf-8')
