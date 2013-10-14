************
Contributing
************

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
