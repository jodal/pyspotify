*********
pyspotify
*********

WARNING: This library no longer works
=====================================

pyspotify is a Python wrapper around the libspotify C library, and thus depends
on libspotify for everything it does.

In May 2015, libspotify was deprecated by Spotify and active maintenance
stopped. At this point, libspotify had been the main way to integrate with
Spotify for six years, and was part of numerous open source projects and
commercial applications, including many receivers and even cars.  It remained
the only API for playback outside Android and iOS.

In February 2016, server side changes to the Spotify API caused the search
functionality to stop working, without Spotify ever acknowledging it. Users of
pyspotify could work around this by using the Spotify web API for searches and
pyspotify for playback.

In April 2022, `Spotify announced
<https://developer.spotify.com/community/news/2022/04/12/libspotify-sunset/>`_
that they would sunset the libspotify API one month later.

In May 2022, new libspotify connections to Spotify started failing. With
libspotify dead, pyspotify was dead too.

After two years in development from May 2013 to May 2015, and seven years of
loyal service this project has reached its end.

**There will be no further updates to pyspotify.**

Hopefully, the pyspotify source code can still serve as a complete example of
how to successfully wrap a large C library in Python using CFFI.


Introduction
============

pyspotify provides a Python interface to
`Spotify's <https://www.spotify.com/>`__ online music streaming service.

With pyspotify you can access music metadata, search in Spotify's library of
20+ million tracks, manage your Spotify playlists, and play music from
Spotify. All from your own Python applications.

pyspotify uses `CFFI <https://cffi.readthedocs.io/>`_ to make a pure Python
wrapper around the official libspotify library. It works on CPython 2.7 and
3.5+, as well as PyPy 2.7 and 3.5+. It is known to work on Linux and
macOS. Windows support should be possible, but is awaiting a contributor with
the interest and knowledge to maintain it.


Project resources
=================

- `Documentation <https://pyspotify.readthedocs.io/>`_
- `Source code <https://github.com/jodal/pyspotify>`_
- `Issue tracker <https://github.com/jodal/pyspotify/issues>`_

.. image:: https://img.shields.io/pypi/v/pyspotify
    :target: https://pypi.org/project/pyspotify/
    :alt: Latest PyPI version

.. image:: https://img.shields.io/github/workflow/status/jodal/pyspotify/CI
    :target: https://github.com/jodal/pyspotify/actions?workflow=CI
    :alt: CI build status

.. image:: https://img.shields.io/readthedocs/pyspotify.svg
    :target: https://pyspotify.readthedocs.io/
    :alt: Read the Docs build status

.. image:: https://img.shields.io/codecov/c/gh/jodal/pyspotify
   :target: https://codecov.io/gh/jodal/pyspotify
   :alt: Test coverage
