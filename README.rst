*********
pyspotify
*********

Python wrapper for libspotify, second edition

This is a new Python wrapper for `libspotify
<https://developer.spotify.com/technologies/libspotify/>`_ based on `CFFI
<http://cffi.readthedocs.org/>`_ instead of a CPython C extension like
pyspotify 1.x was. This makes pyspotify work on CPython 3 as well as PyPy 2.


Development setup
=================

1. Make sure you have the following Python versions installed:

   - CPython 2.7
   - CPython 3.3
   - PyPy 2

2. Install Python, libffi, and libspotify development files. On Ubuntu with
   apt.mopidy.com in your APT sources::

       sudo apt-get install python-all-dev libffi-dev libspotify-dev

3. Create and activate a virtualenv::

       virtualenv ve
       source ve/bin/activate

4. Install cffi and tox::

       pip install cffi tox

5. Optionally, install pyspotify into your virtualenv::

       python setup.py develop

6. Run tests on all the Python implementations::

       tox


Development status
==================

- 2013-05-03: The Python object ``spotify.lib`` is a working CFFI wrapper
  around the entire libspotify 12 API. This will be the foundation for more
  pythonic APIs. The library currently works on CPython 2.7, 3.3 and PyPy 2.
