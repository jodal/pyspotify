*********
pyspotify
*********

pyspotify provides a Python interface to
`Spotify's <http://www.spotify.com/>`__ online music streaming service.

With pyspotify you can access music metadata, search in Spotify's library of
20+ million tracks, manage your Spotify playlists, and play music from
Spotify. All from your own Python applications.

pyspotify use `CFFI <https://cffi.readthedocs.org/>`_ to make a pure Python
wrapper around the official `libspotify
<https://developer.spotify.com/technologies/libspotify/>`__ library. It works
on CPython 2.7 and 3.3+, as well as PyPy 2.6+ and PyPy3 2.5+.  It is known to
work on Linux and OS X. Windows support should be possible, but is awaiting a
contributor with the interest and knowledge to maintain it.


libspotify's deprecation
========================

Note that as of May 2015 libspotify is officially deprecated by Spotify and is
no longer actively maintained.

Spotify has published newer libraries intended for Android and iOS development,
as well as web APIs to access track metadata and manage playlists. Though, for
making apps with Spotify playback capabilities, on any other platform than
Android and iOS, there is currently no alternative to libspotify.

libspotify has been the main way of integrating with Spotify since 2009, and is
today a part of numerous open source projects and commercial applications,
including many receivers and even cars. There's no guarantees, but one can hope
that the large deployment of libspotify means that the library will continue to
work with the Spotify service for a long time into the future.


Project resources
=================

- `Documentation <http://pyspotify.mopidy.com/>`_
- `Source code <https://github.com/mopidy/pyspotify>`_
- `Issue tracker <https://github.com/mopidy/pyspotify/issues>`_
- `CI server <https://travis-ci.org/mopidy/pyspotify>`_
- `Download development snapshot <https://github.com/mopidy/pyspotify/archive/v2.x/develop.tar.gz#egg=pyspotify-dev>`_
- IRC: ``#mopidy`` at `irc.freenode.net <http://freenode.net/>`_

.. image:: https://img.shields.io/pypi/v/pyspotify.svg?style=flat
    :target: https://pypi.python.org/pypi/pyspotify/
    :alt: Latest PyPI version

.. image:: https://img.shields.io/pypi/dm/pyspotify.svg?style=flat
    :target: https://pypi.python.org/pypi/pyspotify/
    :alt: Number of PyPI downloads

.. image:: https://img.shields.io/travis/mopidy/pyspotify/v2.x/develop.svg?style=flat
    :target: https://travis-ci.org/mopidy/pyspotify
    :alt: Travis CI build status

.. image:: https://img.shields.io/coveralls/mopidy/pyspotify/v2.x/develop.svg?style=flat
   :target: https://coveralls.io/r/mopidy/pyspotify?branch=v2.x/develop
   :alt: Test coverage
