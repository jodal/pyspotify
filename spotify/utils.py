from __future__ import unicode_literals

from spotify import ffi, lib


def enum(prefix):
    def wrapper(obj):
        for attr in dir(lib):
            if attr.startswith(prefix):
                setattr(obj, attr.replace(prefix, ''), getattr(lib, attr))
        return obj
    return wrapper


def to_bytes(text):
    if isinstance(text, unicode):
        return text.encode('utf-8')
    else:
        return text


def to_unicode(chars):
    return ffi.string(chars).decode('utf-8')
