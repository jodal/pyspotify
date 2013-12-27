************
Contributing
************

pyspotify 1.x was largely implemented in C as a CPython C extension, working
only with CPython 2.6 and 2.7. It has some tests, but the test suite is far
from complete. It did never provide the full libspotify API.

pyspotify 2.x is based on `CFFI <http://cffi.readthedocs.org/>`__ and
implemented purely in Python. This makes pyspotify 2.x run on both CPython 2.7,
3.2+, as well as on PyPy 2.1+. The library has full test coverage, and the
tests are run on all the targeted Python versions for every commit. pyspotify
2.x will provide Python bindings for the full libspotify API from the very
first release.


Development plans
=================

pyspotify 2.x is a new Python wrapper for `libspotify
<https://developer.spotify.com/technologies/libspotify/>`__. This library is
still under active development. An alpha release to PyPI is planned as soon as
the bindings to libspotify are complete. After the first alpha release, focus
will be on cross-functional aspects such as improved thread safety and drivers
for audio playback.

Alpha 1: 100% complete bindings
-------------------------------

- Complete the playlist subsystem. Mostly need to decide on a pretty way to
  register callbacks, if we should allow multiple callbacks per event, etc.

Alpha 2: More consistent API
----------------------------

- Redo all other callbacks to follow the same pattern as used for playlists.

- Get rid of a lot of properties or getter/setter pairs. The API doesn't feel
  consistent enough as is.

- Update jukebox example to work again.

- Write first draft of the tutorial.

Alpha 3: Threadsafety
---------------------

- Ensure we never call libspotify from another thread while a method is still
  working on the data returned by the previous libspotify call. This will
  require review of all code and the addition of a decorator to the methods
  needing protection against other threads using libspotify while it executes.

- React to ``notify_main_thread`` callbacks and do ``process_events()`` for us
  in a worker thread in the background. This will be a lot easier to implement
  if thread safety is in place first. This functionality should probably be
  possible to opt out of.

- Enforce that the same cache directory isn't used by multiple processes by
  maintaining a lock file or similar.

Beta 1: Seen real usage
-----------------------

- Reimplement Mopidy-Spotify using pyspotify 2. Will surely lead to bug fixes
  and/or API changes.

- Maybe add some more features to the jukebox example.

- Iterate a few times over the docs to improve them as much as possible.

Beta 2: Bundled audio drivers
-----------------------------

- Create GStreamer audio driver.

- Maybe create ALSA audio driver.

- Update jukebox example to play audio.

Final release
-------------

- Consider whether we can get rid of the global session instance now, so we can
  easily support multiple sessions in a single process if libspotify adds
  support for it.

- Fix all remaining TODOs in code and tests.

- Fix all remaining FIXMEs in code and tests.

- Revisit all XXXs in code and tests.


Development setup
=================

1. Make sure you have the following Python versions installed:

   - CPython 2.7
   - CPython 3.2
   - CPython 3.3
   - PyPy 2

2. On Debian/Ubuntu, make sure you have `apt.mopidy.com
   <https://apt.mopidy.com/>`_ in your APT sources. Otherwise, install
   libspotify from source yourself.

3. Install Python, libffi, and libspotify development files. On Debian/Ubuntu::

       sudo apt-get install python-all-dev python3-all-dev libffi-dev libspotify-dev

4. Create and activate a virtualenv::

       virtualenv ve
       source ve/bin/activate

5. Install development dependencies::

       pip install cffi mock nose tox

6. Run tests.

   For a quick test suite run, using the virtualenv's Python version::

       nosetests

   For a complete test suite run, using all the Python implementations::

       tox


Conventions
===========

The following are conventions used in the API or implementation of pyspotify.


Properties vs getters/setters
-----------------------------

In many cases libspotify exposes pairs of related functions, typically a getter
and a setter function. In those cases, pyspotify exposes both the getter and
setter as methods, as well as a more Pythonic property that can both be read
and written to.

For example, the libspotify functions ``sp_playlist_is_in_ram()`` and
``sp_playlist_set_in_ram()`` is available as the methods
:meth:`~spotify.Playlist.is_in_ram` and :meth:`~spotify.Playlist.set_in_ram`,
as well as the property :attr:`~spotify.Playlist.in_ram`. The docstring for all
three is attached to the property.
