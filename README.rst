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

Python wrapper for libspotify, second edition

This is a new Python wrapper for `libspotify
<https://developer.spotify.com/technologies/libspotify/>`__ based on `CFFI
<http://cffi.readthedocs.org/>`__ instead of a CPython C extension like
pyspotify 1.x was. This makes pyspotify work on CPython 3 as well as PyPy 2.


Development setup
=================

1. Make sure you have the following Python versions installed:

   - CPython 2.7
   - CPython 3.2
   - CPython 3.3
   - PyPy 2

2. Install Python, libffi, and libspotify development files. On Ubuntu with
   apt.mopidy.com in your APT sources::

       sudo apt-get install python-all-dev python3-all-dev libffi-dev libspotify-dev

3. Create and activate a virtualenv::

       virtualenv ve
       source ve/bin/activate

4. Install development dependencies::

       pip install cffi mock nose tox

5. Quick test suite run, using the virtualenv's Python version::

       nosetests

6. Slower test suite run, using all the Python implementations::

       tox


Development status
==================

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
