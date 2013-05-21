*********
pyspotify
*********

Python wrapper for libspotify, second edition

This is a new Python wrapper for `libspotify
<https://developer.spotify.com/technologies/libspotify/>`__ based on `CFFI
<http://cffi.readthedocs.org/>`__ instead of a CPython C extension like
pyspotify 1.x was. This makes pyspotify work on CPython 3 as well as PyPy 2.


Development setup
=================

1. Make sure you have the following Python versions installed:

   - CPython 2.7
   - CPython 3.3
   - PyPy 2

2. Install Python, libffi, and libspotify development files. On Ubuntu with
   apt.mopidy.com in your APT sources::

       sudo apt-get install python-all-dev python3-all-dev libffi-dev libspotify-dev

3. Create and activate a virtualenv::

       virtualenv ve
       source ve/bin/activate

4. Install development dependencies::

       pip install cffi mock nose six tox

5. Quick test suite run, using the virtualenv's Python version::

       nosetests

6. Slower test suite run, using all the Python implementations::

       tox


Development status
==================

.. image:: https://secure.travis-ci.org/jodal/pyspotify.png?branch=pyspotify2
    :target: https://travis-ci.org/jodal/pyspotify

- 2013-05-16: Link subsystem complete.

- 2013-05-09: User subsystem complete.

- 2013-05-08: Session configuration and creation, with login and logout works.

- 2013-05-03: The Python object ``spotify.lib`` is a working CFFI wrapper
  around the entire libspotify 12 API. This will be the foundation for more
  pythonic APIs. The library currently works on CPython 2.7, 3.3 and PyPy 2.
