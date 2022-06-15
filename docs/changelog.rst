*********
Changelog
*********

v2.1.4 (2022-06-15)
===================

Maintenance release.

- Declare the pyspotify project as dead.

- Add support for Python 3.9 and 3.10. No changes was required, but the test
  suite now runs on these versions too. (PR: :issue:`203`)

- Switch from CircleCI to GitHub Actions.


v2.1.3 (2019-12-29)
===================

Maintenance release.

- Document that the playlists API is broken. If it is used, emit a warning to notify
  the user of the playlist functionality.

- Update project links.


v2.1.2 (2019-12-10)
===================

Maintenance release.

- Silently abort libspotify ``sp_*_release()`` function calls that happen
  during process shutdown, after pyspotify's global lock is freed. (Fixes:
  :issue:`202`)


v2.1.1 (2019-11-17)
===================

Maintenance release.

- Add support for Python 3.8. No changes was required, but the test suite now
  runs on this version too.

- Switch from Travis CI to CircleCI.


v2.1.0 (2019-07-08)
===================

Maintenance release.

- Drop support for Python 3.3 and 3.4, as both has reached end of life.

- Add support for Python 3.6 and 3.7. No changes was required, but the test
  suite now runs on these versions too.

- On Python 3, import :class:`Iterable`, :class:`MutableSequence`, and
  :class:`Sequence` from :mod:`collections.abc` instead of :mod:`collections`.
  This fixes a deprecation warning on Python 3.7 and prepares for Python 3.8.

- Document that the search API is broken. If it is used, raise an exception
  instead of sending the search to Spotify, as that seems to disconnect your
  session. (Fixes: :issue:`183`)

- Format source code with Black.


v2.0.5 (2015-09-22)
===================

Bug fix release.

- To follow up on the previous release, the getters for the proxy configs now
  convert empty strings in the ``sp_session_config`` struct back to
  :class:`None`. Thus, the need to set these configs to empty strings in the
  struct to make sure the cached settings are cleared from disk are now an
  internal detail, hidden from the user of pyspotify.

- Make :attr:`~spotify.Config.tracefile` default to :class:`None` and set to
  ``NULL`` in the libspotify config struct. If it is set to an empty string by
  default, libspotify will try to use a file with an empty filename for cache
  and fail with "LibError: Unable to open trace file". Now empty strings are
  set as ``NULL`` in the ``sp_session_config`` struct. (Fixes: :ms-issue:`70`)

- libspotify segfaults if the ``device_id`` config is set to an empty string.
  We now avoid this segfault if :attr:`~spotify.Config.device_id` is set to an
  empty string by setting the ``device_id`` field in libspotify's
  ``sp_session_config`` struct to ``NULL`` instead.

- As some test tools (like coverage.py 4.0) no longer support Python 3.2, we no
  longer test pyspotify on Python 3.2. Though, we have not done anything to
  intentionally break support for Python 3.2 ourselves.


v2.0.4 (2015-09-15)
===================

Bug fix release.

- It has been observed that libspotify will reuse cached proxy settings from
  previous sessions if the proxy fields on the ``sp_session_config`` struct are
  set to ``NULL``. When the ``sp_session_config`` fields are set to an empty
  string, the cached settings are updated. When attributes on
  :class:`spotify.Config` are set to :class:`None`, we now set the fields on
  ``sp_session_config`` to empty strings instead of ``NULL``.


v2.0.3 (2015-09-05)
===================

Bug fix release.

- Make moving a playlist to its own location a no-op instead of causing an
  error like libspotify does. (Fixes: :issue:`175`)

- New better installation instructions. (Fixes: :issue:`174`)


v2.0.2 (2015-08-06)
===================

Bug fix release.

- Use ``sp_session_starred_for_user_create(session, username)`` instead of
  ``sp_playlist_create(session, link)`` to get starred playlists by URI. The
  previous approach caused segfaults under some circumstances. (Fixes:
  :ms-issue:`60`)


v2.0.1 (2015-07-20)
===================

Bug fix release.

- Make :meth:`spotify.Session.get_playlist` acquire the global lock before
  modifying the global playlist cache.

- Make :class:`~spotify.Playlist` and :class:`~spotify.PlaylistContainer`
  register callbacks with libspotify if and only if a Python event handler is
  added to the object. Previously, we always registered the callbacks with
  libspotify. Hopefully, this will remove the preconditions for the crashes in
  :issue:`122`, :issue:`153`, and :issue:`165`.


v2.0.0 (2015-06-01)
===================

pyspotify 2.x is a full rewrite of pyspotify. While pyspotify 1.x is a
CPython C extension, pyspotify 2.x uses `CFFI
<https://cffi.readthedocs.io/>`__ to wrap the libspotify C library. It works
on CPython 2.7 and 3.2+, as well as PyPy 2.6+. pyspotify 2.0 makes 100% of the
libspotify 12.1.51 API available from Python, going far beyond the API coverage
of pyspotify 1.x.

The following are the changes since pyspotify 2.0.0b5.

Dependency changes
------------------

- Require cffi >= 1.0. (Fixes: :issue:`133`, :issue:`160`)

- If you're using pyspotify with PyPy you need version 2.6 or newer as older
  versions of PyPy come with a too old cffi version. For PyPy3, you'll probably
  need the yet to be released PyPy3 2.5.

ALSA sink
---------

- Changed the :class:`spotify.AlsaSink` keyword argument ``card`` to ``device``
  to align with pyalsaaudio 0.8.

- Updated to work with pyalsaaudio 0.8 which changed the signature of
  :class:`alsaaudio.PCM`. :class:`spotify.AlsaSink` still works with
  pyalsaaudio 0.7, but 0.8 is recommended at least for Python 3 users, as it
  fixes a memory leak present on Python 3 (see :issue:`127`). (Fixes:
  :issue:`162`)


v2.0.0b5 (2015-05-09)
=====================

A fifth beta with a couple of bug fixes.

Minor changes
-------------

- Changed :meth:`spotify.Link.as_playlist()` to also support creating playlists
  from links with type :attr:`spotify.LinkType.STARRED`.

- Changed all ``load()`` methods to raise :exc:`spotify.Error` instead of
  :exc:`RuntimeError` if the session isn't logged in.

- Changed from nose to py.test as test runner.

Bug fixes
---------

- Work around segfault in libspotify when :attr:`spotify.Config.cache_location`
  is set to :class:`None` and then used to create a session. (Fixes:
  :issue:`151`)

- Return a :class:`spotify.PlaylistPlaceholder` object instead of raising an
  exception if the playlist container contains an element of type
  :attr:`~spotify.PlaylistType.PLACEHOLDER`. (Fixes: :issue:`159`)


v2.0.0b4 (2015-01-13)
=====================

The fourth beta includes a single API change, a couple of API additions, and
otherwise minor tweaks to logging.

pyspotify 2.x has been verified to work on PyPy3, and PyPy3 is now part of the
test matrix.

Minor changes
-------------

- Added :attr:`spotify.Link.url` which returns an
  ``https://open.spotify.com/...`` URL for the link object.

- Adjusted ``info``, ``warning``, and ``error`` level log messages to include
  the word "Spotify" or "pyspotify" for context in applications not including
  the logger name in the log. ``debug`` level messages have not been changed,
  as it is assumed that more details, including the logger name, is included in
  debug logs.

- Added :attr:`spotify.player.Player.state` which is maintained by calls to
  the various :class:`~spotify.player.Player` methods.

Bug fixes
---------

- Fix :meth:`spotify.Playlist.reorder_tracks`. It now accepts a list of
  track indexes instead of a list of tracks. This makes it possible to
  reorder any of multiple identical tracks in a playlist and is consistent with
  :meth:`spotify.Playlist.remove_tracks`. (Fixes: :issue:`134`)

- Fix pause/resume/stop in the ``examples/shell.py`` example. (PR:
  :issue:`140`)

- Errors passed to session callbacks are now logged with the full error type
  representation, instead of just the integer value. E.g. where previously
  only "8" was logged, we now log "<ErrorType.UNABLE_TO_CONTACT_SERVER: 8>".


v2.0.0b3 (2014-05-04)
=====================

The third beta includes a couple of changes to the API in the name of
consistency, as well as three minor improvements.

Also worth noticing is that with this release, pyspotify 2.x has been in
development for a year and a day. Happy birthday, pyspotify 2!

Refactoring: Connection cleanup
-------------------------------

Parts of :class:`spotify.Session` and :attr:`spotify.Session.offline` has been
moved to :attr:`spotify.Session.connection`:

- :meth:`~spotify.offline.Offline.set_connection_type` has been replaced by
  :attr:`session.connection.type <spotify.connection.Connection.type>`,
  which now also allows reading the current connection type.

- :meth:`~spotify.offline.Offline.set_connection_rules` has been replaced by:

  - :attr:`~spotify.connection.Connection.allow_network`
  - :attr:`~spotify.connection.Connection.allow_network_if_roaming`
  - :attr:`~spotify.connection.Connection.allow_sync_over_wifi`
  - :attr:`~spotify.connection.Connection.allow_sync_over_mobile`

  The new attributes allow reading the current connection rules, so your
  application don't have to keep track of what rules it has set.

- :attr:`session.connection_state <spotify.Session.connection_state>`
  has been replaced by :attr:`session.connection.state
  <spotify.connection.Connection.state>`

Refactoring: position vs index
------------------------------

Originally, pyspotify named everything identically with libspotify and have
thus ended up with a mix of the terms "position" and "index" for the same
concept. Now, we use "index" all over the place, as that's also the name used
in the Python world at large. This changes the signature of three methods,
which may affect you if you use keyword arguments to call the methods. There's
also a number of affected events, but these changes shouldn't stop your code
from working.

Affected functions include:

- :meth:`spotify.Playlist.add_tracks` now takes ``index`` instead of
  ``position``.
- :meth:`spotify.Playlist.remove_tracks` now takes ``indexes`` instead of
  ``positions``.
- :meth:`spotify.Playlist.reorder_tracks` now takes ``new_index`` instead of
  ``new_position``.

Affected events include:

- :attr:`spotify.PlaylistContainerEvent.PLAYLIST_ADDED`
- :attr:`spotify.PlaylistContainerEvent.PLAYLIST_REMOVED`
- :attr:`spotify.PlaylistContainerEvent.PLAYLIST_MOVED`
- :attr:`spotify.PlaylistEvent.TRACKS_ADDED`
- :attr:`spotify.PlaylistEvent.TRACKS_REMOVED`
- :attr:`spotify.PlaylistEvent.TRACKS_MOVED`
- :attr:`spotify.PlaylistEvent.TRACK_CREATED_CHANGED`
- :attr:`spotify.PlaylistEvent.TRACK_SEEN_CHANGED`
- :attr:`spotify.PlaylistEvent.TRACK_MESSAGE_CHANGED`

Minor changes
-------------

- ``load()`` methods now return the object if it is already loaded, even if
  :attr:`~spotify.connection.Connection.state` isn't
  :attr:`~spotify.ConnectionState.LOGGED_IN`. Previously, a
  :exc:`RuntimeError` was raised requiring the session to be logged in and
  online before loading already loaded objects.

- :attr:`spotify.Playlist.tracks` now implements the
  :attr:`collections.MutableSequence` contract, supporting deleting items with
  ``del playlist.tracks[i]``, adding items with ``playlist.tracks[i] =
  track``, etc.

- :meth:`spotify.Session.get_link` and all other methods accepting Spotify
  URIs now also understand open.spotify.com and play.spotify.com URLs.


v2.0.0b2 (2014-04-29)
=====================

The second beta is a minor bug fix release.

Bug fixes
---------

- Fix :class:`spotify.Playlist.remove_tracks`. It now accepts a list of
  track positions instead of a list of tracks. This makes it possible to
  remove any of multiple identical tracks in a playlist. (Fixes: :issue:`128`)

Minor changes
-------------

- Make all objects compare as equal and have the same hash if they wrap the
  same libspotify object. This makes it possible to find the index of a track
  in a playlist by doing ``playlist.tracks.index(track)``, where
  ``playlist.tracks`` is a custom collection always returning new
  :class:`~spotify.Track` instances. (Related to: :issue:`128`)

- :attr:`spotify.Config.ca_certs_filename` now works on systems where
  libspotify has this field. On systems where this field isn't present in
  libspotify, assigning to it will have no effect. Previously, assignment to
  this field was a noop on all platforms because the field is missing from
  libspotify on OS X.


v2.0.0b1 (2014-04-24)
=====================

pyspotify 2.x is a full rewrite of pyspotify. While pyspotify 1.x is a
CPython C extension, pyspotify 2.x uses `CFFI <http://cffi.readthedocs.io/>`__
to make 100% of the libspotify C library available from Python. It works on
CPython 2.7 and 3.2+, as well as PyPy 2.1+.

Since the previous release, pyspotify has become thread safe. That is,
pyspotify can safely be used from multiple threads. The added thread safety
made an integrated event loop possible, which greatly simplifies the usage of
pyspotify, as can be seen from the updated example in ``examples/shell.py``.
Audio sink helpers for ALSA and PortAudio have been added, together with
updated examples that can play music. A number of bugs have been fixed, and at
the time of the release, there are no known issues.

The pyspotify 2.0.0b1 release marks the completion of all planned features for
pyspotify 2.x. The plans for the next releases are focused on fixing bugs as
they surface, incrementally improving the documentation, and integrating
feedback from increased usage of the library in the wild.

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
  playlist when it is initially loaded. Combined with having registered a
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
CPython C extension, pyspotify 2.x uses `CFFI <http://cffi.readthedocs.io/>`__
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

These features are planned for the upcoming prereleases.


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
<http://pyspotify.readthedocs.io/en/v1.x-develop/changes/>`__.
