*********
pyspotify
*********

pyspotify provides a Python interface to
`Spotify's <https://www.spotify.com/>`__ online music streaming service.

With pyspotify you can access music metadata, search in Spotify's library of
20+ million tracks, manage your Spotify playlists, and play music from
Spotify. All from your own Python applications.

pyspotify uses `CFFI <https://cffi.readthedocs.org/>`_ to make a pure Python
wrapper around the official libspotify library. It works on CPython 2.7 and
3.5+, as well as PyPy 2.7 and 3.5+. It is known to work on Linux and
macOS. Windows support should be possible, but is awaiting a contributor with
the interest and knowledge to maintain it.


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

- `Documentation <https://pyspotify.readthedocs.io/>`_
- `Source code <https://github.com/jodal/pyspotify>`_
- `Issue tracker <https://github.com/jodal/pyspotify/issues>`_

.. image:: https://img.shields.io/pypi/v/pyspotify
    :target: https://pypi.org/project/pyspotify/
    :alt: Latest PyPI version

.. image:: https://img.shields.io/circleci/build/gh/jodal/pyspotify
    :target: https://circleci.com/gh/jodal/pyspotify
    :alt: CircleCI build status

.. image:: https://img.shields.io/codecov/c/gh/jodal/pyspotify
   :target: https://codecov.io/gh/jodal/pyspotify
   :alt: Test coverage
