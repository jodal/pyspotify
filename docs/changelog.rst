*********
Changelog
*********

v2.0.0a1 (2014-01-14)
=====================

pyspotify 2.x is a full rewrite of pyspotify. While pyspotify 1.x is a
CPython C extension, pyspotify 2.x uses `CFFI <http://cffi.readthedocs.org/>`__
to wrap the libspotify C library. It works on CPython 2.7 and 3.2+, as well as
PyPy 2.1+.

This first alpha release of pyspotify 2.0.0 makes 100% of the libspotify
12.1.51 API available from Python, going far beyond the API coverage of
pyspotify 1.x.

pyspotify 2.0.0a1 has an extensive test suite with 98% line coverage. All tests
pass on all combinations of CPython 2.7, 3.2, 3.3, PyPy 2.2 running on Linux on
i386, amd64, armel, and armhf. Mac OS X should work, but has not been tested
recently.

This release *does not* provide:

- thread safety,

- an event loop for regularly processing libspotify events, or

- audio playback drivers.

These features are planned for the upcoming prereleases, as outlined in
:doc:`plans`.

**Development milestones**

- 2014-02-13: Playlist callbacks complete. pyspotify 2.x now covers 100% of
  the libspotify 12 API. Docs reviewed, quickstart guide extended. Redundant
  getters/setters removed.

- 2014-02-08: Playlist container callbacks complete.

- 2014-01-31: Redesign session event listening to a model supporting multiple
  listeners per event, with a nicer API for registering listeners.

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


v1.x series
===========

See the `pyspotify 1.x changelog
<http://pyspotify.mopidy.com/en/v1.x-develop/changes/>`__.
