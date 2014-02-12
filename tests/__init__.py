from __future__ import unicode_literals

import gc
import mock
import platform
import weakref

import cffi

# Import the module so that ffi.verify() is run before cffi.verifier is used
import spotify  # noqa

cffi.verifier.cleanup_tmpdir()


# TODO Review all use of ffi.cast() in the tests. Lots of `ffi.cast('sp_foo *',
# ffi.new('int *'))` should probably be replaced by `ffi.cast('sp_foo *', 42)`.


def buffer_writer(string):
    """Creates a function that takes a ``buffer`` and ``buffer_size`` as the
    two last arguments and writes the given ``string`` to ``buffer``.
    """

    def func(*args):
        assert len(args) >= 2
        buffer_, buffer_size = args[-2:]

        # -1 to keep a char free for \0 terminating the string
        length = min(len(string), buffer_size - 1)

        # Due to Python 3 treating bytes as an array of ints, we have to
        # encode and copy chars one by one.
        for i in range(length):
            buffer_[i] = string[i].encode('utf-8')

        return len(string)

    return func


def create_session():
    """Creates a :class:`spotify.Session` mock for testing."""
    session = mock.Mock()
    session._cache = weakref.WeakValueDictionary()
    session._emitters = []
    spotify.session_instance = session
    return session


def gc_collect():
    """Run enough GC collections to make object finalizers run."""
    if platform.python_implementation() == 'PyPy':
        # Since PyPy use garbage collection instead of reference counting
        # objects are not finalized before the next major GC collection.
        # Currently, the best way we have to ensure a major GC collection has
        # run is to call gc.collect() a number of times.
        [gc.collect() for _ in range(10)]
    else:
        gc.collect()
