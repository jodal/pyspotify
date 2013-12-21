*********
pyspotify
*********

.. image:: https://pypip.in/v/pyspotify/badge.png
    :target: https://pypi.python.org/pypi/pyspotify/
    :alt: Latest PyPI version

.. image:: https://pypip.in/d/pyspotify/badge.png
    :target: https://pypi.python.org/pypi/pyspotify/
    :alt: Number of PyPI downloads

.. image:: https://travis-ci.org/mopidy/pyspotify.png?branch=v2.x/develop
    :target: https://travis-ci.org/mopidy/pyspotify
    :alt: Travis CI build status

.. image:: https://coveralls.io/repos/mopidy/pyspotify/badge.png?branch=v2.x/develop
   :target: https://coveralls.io/r/mopidy/pyspotify?branch=v2.x/develop
   :alt: Test coverage

pyspotify 2.x is a new Python wrapper for `libspotify
<https://developer.spotify.com/technologies/libspotify/>`__.

pyspotify 1.x was largely implemented in C as a CPython C extension, working
only with CPython 2.6 and 2.7. It has some tests, but the test suite is far
from complete. It did never provide the full libspotify API.

pyspotify 2.x is based on `CFFI <http://cffi.readthedocs.org/>`__ and
implemented purely in Python. This makes pyspotify 2.x run on both CPython 2.7,
3.2, 3.3, as well as on PyPy. The library has full test coverage, and the tests
are run on all the targeted Python versions for every commit. pyspotify 2.x
will provide Python bindings for the full libspotify API from the very first
release.


Development
===========

This library is still under active development. See ``docs/contributing.rst``
for how to setup the development environment and run tests.


Development plans
=================

An alpha release to PyPI is planned as soon as the bindings to libspotify are
complete. After the first alpha release, focus will be on cross-functional
aspects such as improved thread safety and drivers for audio playback.

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


Development milestones
======================

- 2013-12-16: Ensure we never call libspotify from two different threads at the
  same time. We can't assume that the CPython GIL will ensure this for us, as
  we target non-CPython interpreters like PyPy.

- 2013-12-13: Artist browsing complete.

- 2013-12-13: Album browsing complete.

- 2013-11-29: Toplist subsystem complete.

- 2013-11-27: Inbox subsystem complete.

- 2013-10-14: Playlist subsystem *almost* complete.

- 2013-06-21: Search subsystem complete.

- 2013-06-10: Album subsystem complete.

- 2013-06-09: Track and artist subsystem complete.

- 2013-06-02: Session subsystem complete, with all methods.

- 2013-06-01: Session callbacks complete.

- 2013-05-25: Session config complete.

- 2013-05-16: Link subsystem complete.

- 2013-05-09: User subsystem complete.

- 2013-05-08: Session configuration and creation, with login and logout works.

- 2013-05-03: The Python object ``spotify.lib`` is a working CFFI wrapper
  around the entire libspotify 12 API. This will be the foundation for more
  pythonic APIs. The library currently works on CPython 2.7, 3.3 and PyPy 2.
