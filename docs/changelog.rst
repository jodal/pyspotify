*********
Changelog
*********

v2.0.0b1 (UNRELEASED)
=====================

Feature: Thread safety
----------------------

- Hold the global lock while we are working with pointers returned by
  libspotify. This ensures that we never call libspotify from another thread
  while we are still working on the data returned by the previous libspotify
  call, which could make the data garbage.

- Ensure we never edit shared data structures without holding the global lock.

Feature: Event loop
-------------------

- Add :class:`spotify.EventLoop` helper thread that reacts to
  :class:`~spotify.SessionEvent.NOTIFY_MAIN_THREAD` events and calls
  :meth:`~spotify.Session.process_events` for you when appropriate.

- Update ``examples/shell.py`` to be a lot simpler with the help of the new
  event loop.

Feature: Audio playback
-----------------------

- Add :class:`spotify.AlsaSink`, an audio sink for playback through ALSA on
  Linux systems.

- Add :class:`spotify.PortAudioSink`, an audio sink for playback through
  PortAudio on most platforms, including Linux, OS X, and Windows.

- Update ``examples/shell.py`` to use the ALSA sink to play music.

- Add ``examples/play_track.py`` as a simpler example of audio playback.

Refactoring: Remove global state
--------------------------------

To prepare for removing all global state, the use of the module attribute
:attr:`spotify.session_instance` has been replaced with explicit passing of the
session object to all objects that needs it. To allow for this, the following
new methods have been added, and should be used instead of their old
equivalents:

- :meth:`spotify.Session.get_link` replaces :class:`spotify.Link`.
- :meth:`spotify.Session.get_track` replaces :class:`spotify.Track`.
- :meth:`spotify.Session.get_local_track` replaces
  :class:`spotify.LocalTrack`.
- :meth:`spotify.Session.get_album` replaces :class:`spotify.Album`.
- :meth:`spotify.Session.get_artist` replaces :class:`spotify.Artist`.
- :meth:`spotify.Session.get_playlist` replaces :class:`spotify.Playlist`.
- :meth:`spotify.Session.get_user` replaces :class:`spotify.User`.
- :meth:`spotify.Session.get_image` replaces :class:`spotify.Image`.
- :meth:`spotify.Session.get_toplist` replaces :class:`spotify.Toplist`.

Refactoring: Consistent naming of ``Session`` members
-----------------------------------------------------

With all the above getters added to the :class:`spotify.Session` object, it
made sense to rename some existing methods of :class:`~spotify.Session` for
consistency:

- :meth:`spotify.Session.starred_for_user`
  is replaced by :meth:`~spotify.Session.get_starred`.

- :attr:`spotify.Session.starred` to get the currently logged in user's starred
  playlist is replaced by :meth:`~spotify.Session.get_starred` without any
  arguments.

- :meth:`spotify.Session.get_published_playlists` replaces
  :meth:`~spotify.Session.published_playlists_for_user`. As previously, it
  returns the published playlists for the currently logged in user if no
  username is provided.

Refactoring: Consistent naming of ``threading.Event`` objects
-------------------------------------------------------------

All :class:`threading.Event` objects have been renamed to be consistently
named across classes.

- :attr:`spotify.AlbumBrowser.loaded_event` replaces
  :attr:`spotify.AlbumBrowser.complete_event`.
- :attr:`spotify.ArtistBrowser.loaded_event` replaces
  :attr:`spotify.ArtistBrowser.complete_event`.
- :attr:`spotify.Image.loaded_event` replaces :attr:`spotify.Image.load_event`.
- :attr:`spotify.InboxPostResult.loaded_event` replaces
  :attr:`spotify.InboxPostResult.complete_event`.
- :attr:`spotify.Search.loaded_event` replaces
  :attr:`spotify.Search.complete_event`.
- :attr:`spotify.Toplist.loaded_event` replaces
  :attr:`spotify.Toplist.complete_event`.

Refactoring: Change how to register image load listeners
--------------------------------------------------------

pyspotify has two main schemes for registering listener functions:

- Objects that only emit an event when it is done loading, like
  :class:`~spotify.AlbumBrowser`, :class:`~spotify.ArtistBrowser`,
  :class:`~spotify.InboxPostResult`, :class:`~spotify.Search`, and
  :class:`~spotify.Toplist`, accept a single callback as a ``callback``
  argument to its constructor or constructor methods.

- Objects that have multiple callback events, like :class:`~spotify.Session`,
  :class:`~spotify.PlaylistContainer`, and :class:`~spotify.Playlist`, accept
  the registration and unregistration of one or more listener functions for
  each event it emits. This can happen any time during the object's life cycle.

Due to pyspotify's close mapping to libspotify's organization, :class:`Image`
objects used to use a third variant with two methods,
:meth:`~spotify.Image.add_load_callback` and
:meth:`~spotify.Image.remove_load_callback`, for adding and removing load
callbacks. These methods have now been removed, and :class:`~spotify.Image`
accepts a ``callback`` argument to its constructor and constructor methods:

- :meth:`spotify.Album.cover` accepts a ``callback`` argument.
- :meth:`spotify.Artist.portrait` accepts a ``callback`` argument.
- :meth:`spotify.ArtistBrowser.portraits` is now a method and accepts a
  ``callback`` argument.
- :meth:`spotify.Link.as_image` accepts a ``callback`` argument.
- :meth:`spotify.Playlist.image` is now a method and accepts a ``callback``
  argument.
- :meth:`spotify.Session.get_image` accepts a ``callback`` argument.

Bug fixes
---------

- Remove multiple extra ``sp_link_add_ref()`` calls, potentially causing
  memory leaks in libspotify.

- Add missing error check to :meth:`spotify.Playlist.add_tracks`.

- Keep album, artist, image, inbox, search, and toplist objects alive until
  their complete/load callbacks have been called, even if the library user
  doesn't keep any references to the objects. (Fixes: :issue:`121`)

- Fix flipped logic causing crash in :meth:`spotify.Album.cover_link`. (Fixes:
  :issue:`126`)

- Work around segfault in libspotify if
  :attr:`~spotify.social.Social.private_session` is set before the session is
  logged in and the first events are processed. This is a bug in libspotify
  which has been reported to Spotify through their IRC channel.

- Multiple attributes on :class:`~spotify.Track` raised an exception if
  accessed before the track was loaded. They now return :class:`None` or
  similar as documented.

- Fix segfault when creating local tracks without all arguments specified.
  ``NULL`` was used as the placeholder instead of the empty string.

- Support negative indexes on all custom sequence types. For example,
  ``collection[-1]`` returns the last element in the collection.

- We now cache playlists when created from URIs. Previously, only playlists
  created from ``sp_playlist`` objects were cached. This avoids a potentially
  large number of wrapper object recreations due to a flood of updates to the
  playlist when it is intially loaded. Combined with having registered a
  callback for the libspotify ``playlist_update_in_progress`` callback, this
  could cause deep call stacks reaching the maximum recursion depth. (Fixes:
  :issue:`122`)

Minor changes
-------------

- Add :func:`spotify.get_libspotify_api_version` and
  :func:`spotify.get_libspotify_build_id`.

- Running ``python setup.py test`` now runs the test suite.

- The tests are now compatible with CPython 3.4. No changes to the
  implementation was required.

- The test suite now runs on Mac OS X, using CPython 2.7, 3.2, 3.3, 3.4, and
  PyPy 2.2, on every push to GitHub.


v2.0.0a1 (2014-02-14)
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


Development milestones
----------------------

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
