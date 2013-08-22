from __future__ import unicode_literals

import sys
import time

import spotify
from spotify import ffi, lib


PY2 = sys.version_info[0] == 2

if PY2:  # pragma: no branch
    string_types = (basestring,)
    text_type = unicode
    binary_type = str
else:
    string_types = (str,)
    text_type = str
    binary_type = bytes


class IntEnum(int):
    def __new__(cls, value):
        if not hasattr(cls, '_values'):
            cls._values = {}
        if value not in cls._values:
            cls._values[value] = int.__new__(cls, value)
        return cls._values[value]

    def __repr__(self):
        if hasattr(self, '_name'):
            return '<%s.%s: %d>' % (self.__class__.__name__, self._name, self)
        else:
            return '<Unknown %s: %d>' % (self.__class__.__name__, self)

    @classmethod
    def add(cls, name, value):
        attr = cls(value)
        attr._name = name
        setattr(cls, name, attr)


def make_enum(lib_prefix, enum_prefix=''):
    def wrapper(cls):
        for attr in dir(lib):
            if attr.startswith(lib_prefix):
                name = attr.replace(lib_prefix, enum_prefix)
                cls.add(name, getattr(lib, attr))
        return cls
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


def load(obj, timeout=None):
    """Block until the object's data is loaded.

    The ``obj`` must at least have the :attr:`is_loaded` attribute. If it also
    has an :meth:`error` method, it will be checked for errors to raise.

    :param timeout: seconds before giving up and raising an exception
    :type timeout: float
    :returns: self
    """
    if spotify.session_instance is None:
        raise RuntimeError('Session must be initialized to load objects')
    if spotify.session_instance.user is None:
        raise RuntimeError('Session must be logged in to load objects')
    # TODO Timeout if this takes too long
    while not obj.is_loaded:
        spotify.session_instance.process_events()
        if hasattr(obj, 'error'):
            spotify.Error.maybe_raise(
                obj.error, ignores=[spotify.ErrorType.IS_LOADING])
        time.sleep(0.001)
    return obj


def to_bytes(value):
    if isinstance(value, text_type):
        return value.encode('utf-8')
    elif isinstance(value, ffi.CData):
        return ffi.string(value)
    elif isinstance(value, binary_type):
        return value
    else:
        raise ValueError('Value must be text, bytes, or char[]')


def to_unicode(value):
    if isinstance(value, ffi.CData):
        return ffi.string(value).decode('utf-8')
    elif isinstance(value, binary_type):
        return value.decode('utf-8')
    elif isinstance(value, text_type):
        return value
    else:
        raise ValueError('Value must be text, bytes, or char[]')


def to_country(code):
    return to_unicode(chr(code >> 8) + chr(code & 0xff))


def to_country_code(country):
    country = to_unicode(country)
    if len(country) != 2:
        raise ValueError('Must be exactly two chars')
    first, second = (ord(char) for char in country)
    if (not (ord('A') <= first <= ord('Z')) or
            not (ord('A') <= second <= ord('Z'))):
        raise ValueError('Chars must be in range A-Z')
    return first << 8 | second
