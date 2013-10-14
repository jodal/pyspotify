*********
pyspotify
*********

.. image:: https://pypip.in/v/pyspotify/badge.png
    :target: https://crate.io/packages/pyspotify/
    :alt: Latest PyPI version

.. image:: https://pypip.in/d/pyspotify/badge.png
    :target: https://crate.io/packages/pyspotify/
    :alt: Number of PyPI downloads

.. image:: https://travis-ci.org/jodal/pyspotify.png?branch=pyspotify2
    :target: https://travis-ci.org/jodal/pyspotify
    :alt: Travis CI build status

.. image:: https://coveralls.io/repos/jodal/pyspotify/badge.png?branch=pyspotify2
   :target: https://coveralls.io/r/jodal/pyspotify?branch=pyspotify2
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


Development plans
=================

This library is still under development. An alpha release to PyPI is planned as
soon as the the bindings to libspotify are complete. After the first alpha
release, focus will be on cross-functional aspects such as improved thread
safety and helpers for audio playback.

See ``docs/contributing.rst`` for how to setup the development environment and
run tests.


Development milestones
======================

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
