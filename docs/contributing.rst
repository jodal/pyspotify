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
