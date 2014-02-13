from __future__ import unicode_literals

import collections
import functools
import pprint
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


class EventEmitter(object):
    """Mixin for adding event emitter functionality to a class."""

    def __init__(self):
        self._listeners = collections.defaultdict(list)

    def on(self, event, listener, *user_args):
        """Register a ``listener`` to be called on ``event``.

        The listener will be called with any extra arguments passed to
        :meth:`emit` first, and then the extra arguments passed to :meth:`on`
        last.

        If the listener function returns :class:`False`, it is removed and will
        not be called the next time the ``event`` is emitted.
        """
        self._listeners[event].append(
            _Listener(callback=listener, user_args=user_args))

    def off(self, event=None, listener=None):
        """Remove a ``listener`` that was to be called on ``event``.

        If ``listener`` is :class:`None`, all listeners for the given ``event``
        will be removed.

        If ``event`` is :class:`None`, all listeners for all events on this
        object will be removed.
        """
        if event is None:
            events = self._listeners.keys()
        else:
            events = [event]
        for event in events:
            if listener is None:
                self._listeners[event] = []
            else:
                self._listeners[event] = [
                    l for l in self._listeners[event]
                    if l.callback is not listener]

    def emit(self, event, *event_args):
        """Call the registered listeners for ``event``.

        The listeners will be called with any extra arguments passed to
        :meth:`emit` first, and then the extra arguments passed to :meth:`on`
        """
        for listener in self._listeners[event]:
            args = list(event_args) + list(listener.user_args)
            result = listener.callback(*args)
            if result is False:
                self.off(event, listener.callback)

    def num_listeners(self, event=None):
        """Return the number of listeners for ``event``.

        Return the total number of listeners for all events on this object if
        ``event`` is :class:`None`.
        """
        if event is not None:
            return len(self._listeners[event])
        else:
            return sum([len(l) for l in self._listeners.values()])

    def call(self, event, *event_args):
        """Call the single registered listener for ``event``.

        The listener will be called with any extra arguments passed to
        :meth:`call` first, and then the extra arguments passed to :meth:`on`

        Raises :exc:`AssertionError` if there is none or multiple listeners for
        ``event``. Returns the listener's return value on success.
        """
        assert self.num_listeners(event) == 1, (
            'Expected exactly 1 event listener, found %d listeners' %
            self.num_listeners(event))
        listener = self._listeners[event][0]
        args = list(event_args) + list(listener.user_args)
        return listener.callback(*args)


class _Listener(collections.namedtuple(
        'Listener', ['callback', 'user_args'])):
    """An listener of events from an :class:`EventEmitter`"""


class IntEnum(int):
    """An enum type for values mapping to integers.

    Tries to stay as close as possible to the enum type specified in
    :pep:`435` and introduced in Python 3.4.
    """

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
    """Class decorator for automatically adding enum values.

    The values are read directly from the :attr:`spotify.lib` CFFI wrapper
    around libspotify. All values starting with ``lib_prefix`` are added. The
    ``lib_prefix`` is stripped from the name. Optionally, ``enum_prefix`` can
    be specified to add a prefix to all the names.
    """

    def wrapper(cls):
        for attr in dir(lib):
            if attr.startswith(lib_prefix):
                name = attr.replace(lib_prefix, enum_prefix)
                cls.add(name, getattr(lib, attr))
        return cls
    return wrapper


def get_with_fixed_buffer(buffer_length, func, *args):
    """Get a unicode string from a C function that takes a fixed-size buffer.

    The C function ``func`` is called with any arguments given in ``args``, a
    buffer of the given ``buffer_length``, and ``buffer_length``.

    Returns the buffer's value decoded from UTF-8 to a unicode string.
    """
    func = functools.partial(func, *args)
    buffer_ = ffi.new('char[]', buffer_length)
    func(buffer_, buffer_length)
    return to_unicode(buffer_)


def get_with_growing_buffer(func, *args):
    """Get a unicode string from a C function that returns the buffer size
    needed to return the full string.

    The C function ``func`` is called with any arguments given in ``args``, a
    buffer of fixed size, and the buffer size. If the C function returns a
    size that is larger than the buffer already filled, the C function is
    called again with a buffer large enough to get the full string from the C
    function.

    Returns the buffer's value decoded from UTF-8 to a unicode string.
    """
    func = functools.partial(func, *args)
    actual_length = 10
    buffer_length = actual_length
    while actual_length >= buffer_length:
        buffer_length = actual_length + 1
        buffer_ = ffi.new('char[]', buffer_length)
        actual_length = func(buffer_, buffer_length)
    if actual_length == -1:
        return None
    return to_unicode(buffer_)


def load(obj, timeout=None):
    """Block until the object's data is loaded.

    The ``obj`` must at least have the :attr:`is_loaded` attribute. If it also
    has an :meth:`error` method, it will be checked for errors to raise.

    After ``timeout`` seconds with no results :exc:`~spotify.Timeout` is
    raised.

    If unspecified, the ``timeout`` defaults to 10s. Any timeout is better than
    no timeout, since no timeout would cause programs to potentially hang
    forever without any information to help debug the issue.

    The method returns ``self`` to allow for chaining of calls.
    """
    if spotify.session_instance is None:
        raise RuntimeError('Session must be initialized to load objects')
    if spotify.session_instance.user is None:
        raise RuntimeError('Session must be logged in to load objects')
    if timeout is None:
        timeout = 10
    deadline = time.time() + timeout
    while not obj.is_loaded:
        # TODO Consider sleeping for the time returned by process_events()
        # instead of making a tight loop.
        spotify.session_instance.process_events()
        spotify.Error.maybe_raise(
            getattr(obj, 'error', 0), ignores=[spotify.ErrorType.IS_LOADING])
        if time.time() > deadline:
            raise spotify.Timeout(timeout)
        time.sleep(0.001)
    spotify.Error.maybe_raise(
        getattr(obj, 'error', 0), ignores=[spotify.ErrorType.IS_LOADING])
    return obj


class Sequence(collections.Sequence):
    """Helper class for making sequences from a length and getitem function.

    The ``sp_obj`` is assumed to already have gotten an extra reference through
    ``sp_*_add_ref`` and to be automatically released through ``sp_*_release``
    when the ``sp_obj`` object is GC-ed.
    """

    def __init__(
            self, sp_obj, add_ref_func, release_func, len_func, getitem_func):

        add_ref_func(sp_obj)
        self._sp_obj = ffi.gc(sp_obj, release_func)
        self._len_func = len_func
        self._getitem_func = getitem_func

    def __len__(self):
        return self._len_func(self._sp_obj)

    def __getitem__(self, key):
        if isinstance(key, slice):
            return list(self).__getitem__(key)
        if not isinstance(key, int):
            raise TypeError(
                'list indices must be int or slice, not %s' %
                key.__class__.__name__)
        if not 0 <= key < self.__len__():
            raise IndexError('list index out of range')
        return self._getitem_func(self._sp_obj, key)

    def __repr__(self):
        return pprint.pformat(list(self))


def to_bytes(value):
    """Converts bytes, unicode, and C char arrays to bytes.

    Unicode strings are encoded to UTF-8.
    """
    if isinstance(value, text_type):
        return value.encode('utf-8')
    elif isinstance(value, ffi.CData):
        return ffi.string(value)
    elif isinstance(value, binary_type):
        return value
    else:
        raise ValueError('Value must be text, bytes, or char[]')


def to_bytes_or_none(value):
    """Converts C char arrays to bytes and C NULL values to None."""
    if value == ffi.NULL:
        return None
    elif isinstance(value, ffi.CData):
        return ffi.string(value)
    else:
        raise ValueError('Value must be char[] or NULL')


def to_unicode(value):
    """Converts bytes, unicode, and C char arrays to unicode strings.

    Bytes and C char arrays are decoded from UTF-8.
    """
    if isinstance(value, ffi.CData):
        return ffi.string(value).decode('utf-8')
    elif isinstance(value, binary_type):
        return value.decode('utf-8')
    elif isinstance(value, text_type):
        return value
    else:
        raise ValueError('Value must be text, bytes, or char[]')


def to_unicode_or_none(value):
    """Converts C char arrays to unicode and C NULL values to None.

    C char arrays are decoded from UTF-8.
    """
    if value == ffi.NULL:
        return None
    elif isinstance(value, ffi.CData):
        return ffi.string(value).decode('utf-8')
    else:
        raise ValueError('Value must be char[] or NULL')


def to_char_or_null(value):
    """Converts bytes, unicode, and C char arrays to C char arrays, and
    :class:`None` to C NULL values.
    """
    if value is None:
        return ffi.NULL
    else:
        return ffi.new('char[]', to_bytes(value))


def to_country(code):
    """Converts libspotify country codes to unicode strings."""
    return to_unicode(chr(code >> 8) + chr(code & 0xff))


def to_country_code(country):
    """Converts unicode strings to libspotify country codes."""
    country = to_unicode(country)
    if len(country) != 2:
        raise ValueError('Must be exactly two chars')
    first, second = (ord(char) for char in country)
    if (not (ord('A') <= first <= ord('Z')) or
            not (ord('A') <= second <= ord('Z'))):
        raise ValueError('Chars must be in range A-Z')
    return first << 8 | second
