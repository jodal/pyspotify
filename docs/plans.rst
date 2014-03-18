*****************
Development plans
*****************

pyspotify 2.x is a new Python wrapper for `libspotify
<https://developer.spotify.com/technologies/libspotify/>`__. This library is
still under active development.


v2.0.0a2: Thread safety
=======================

- Revisit all TODOs and FIXMEs in code and tests.


v2.0.0b1: Seen real usage
=========================

- Reimplement Mopidy-Spotify using pyspotify 2. Will surely lead to bug fixes
  and/or API changes.

- Look into how asyncio support could work.

- Maybe add some more features to the jukebox example.

- Iterate a few times over the docs to improve them as much as possible.


v2.0.0: Final release
=====================

- Enforce that the same cache and settings directories are not used by multiple
  processes by maintaining a lock file.

- Fix all remaining TODOs in code and tests.

- Fix all remaining FIXMEs in code and tests.

- Revisit all XXXs in code and tests.
