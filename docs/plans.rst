*****************
Development plans
*****************

pyspotify 2.x is a new Python wrapper for `libspotify
<https://developer.spotify.com/technologies/libspotify/>`__. This library is
still under active development.


v2.0.0a2: Thread safety
=======================

- Ensure we never call libspotify from another thread while a method is still
  working on the data returned by the previous libspotify call. This will
  require review of all code and the addition of a decorator to the methods
  needing protection against other threads using libspotify while it executes.

- React to ``notify_main_thread`` callbacks and do ``process_events()`` for us
  in a worker thread in the background. This will be a lot easier to implement
  if thread safety is in place first. This functionality should probably be
  possible to opt out of.

- Enforce that the same cache directory isn't used by multiple processes by
  maintaining a lock file or similar.

- Consider whether we can get rid of the global session instance now, so we can
  easily support multiple sessions in a single process if libspotify adds
  support for it.


v2.0.0b1: Seen real usage
=========================

- Reimplement Mopidy-Spotify using pyspotify 2. Will surely lead to bug fixes
  and/or API changes.

- Maybe add some more features to the jukebox example.

- Iterate a few times over the docs to improve them as much as possible.


v2.0.0b2: Bundled audio drivers
===============================

- Create GStreamer audio driver.

- Maybe create ALSA audio driver.

- Update jukebox example to play audio.


v2.0.0: Final release
=====================

- Fix all remaining TODOs in code and tests.

- Fix all remaining FIXMEs in code and tests.

- Revisit all XXXs in code and tests.
