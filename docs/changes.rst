=======
Changes
=======

.. currentmodule:: spotify

v1.7 (in development)
=====================

**API changes**

- Artist and album browsers are now created directly from the
  :class:`ArtistBrowser` and :class:`AlbumBrowser` class constructors. The
  :meth:`Session.browse_artist` and :meth:`Session.browse_album` methods still
  work but have been deprecated. Also, callbacks are optional for the two
  browsers.

- The audio sink wrappers have been cleaned up and moved to a new
  :mod:`spotify.audiosink` module. The interface is the same, but you'll need
  to update your imports if you previously used either
  :class:`spotify.alsahelper.AlsaController` (renamed to
  :class:`spotify.audiosink.alsa.AlsaSink`) or
  :class:`spotify.osshelper.OssController` (renamed to
  :class:`spotify.audiosink.oss.OssSink`).

**New features**

- A audio sink wrapper for `PortAudio
  <http://www.portaudio.com/>`_ have been contributed by Tommaso Barbugli.
  PortAudio is available on both Linux, Mac OS X, and Windows.

- The audio sink selector code originally written by Tommaso Barbugli for the
  ``jukebox.py`` example app have been generalized and made available for other
  applications as :func:`spotify.audiosink.import_audio_sink`.


v1.6 (2011-11-29)
=================

Updated to work with libspotify 10.1.16.

**API changes**

- ``Session.is_available(track)`` has been moved to
  :meth:`spotify.Track.availability()`, and returns a detailed availability
  status of the track.
- ``Session.is_local(track)`` is now
  :meth:`spotify.Track.is_local()`, and returns a boolean.
- Removed methods: ``Session.get_friends``, ``User.full_name``,
  ``User.picture``, and ``User.relation``, as they was removed from the
  libspotify API.

**New features**

- Add new method: :meth:`spotify.Playlist.track_create_time`. Contributed by
  Benjamin Chapus.


v1.5 (2011-10-30)
=================

Updated to work with libspotify 9.1.32.

**New features**

- Remember me: when setting the ``remember_me`` parameter to ``True`` at
  first login, it is possible to log in again without specifying the
  ``username`` and ``password`` attributes. Don't forget to logout in order to
  store the credentials.
- Add new method: :meth:`spotify.Playlist.subscribers`
- Add new method: :meth:`spotify.Playlist.num_subscribers`
- Add new method: :meth:`spotify.Playlist.update_subscribers`
- Playlist folder boundaries are now recognized. Playlist containers
  contain both :class:`spotify.Playlist` and :class:`spotify.PlaylistFolder`
  objects. Both classes got a ``type()`` method, which returns the string
  ``playlist``, ``folder_start``, ``folder_end``, or ``placeholder``.


v1.4 (2011-09-24)
=================

pyspotify v1.4 only works with libspotify v0.0.8. As libspotify v9.x has been
released, this release of pyspotify will probably be the last release to work
with libspotify v0.0.8.

**API changes**

- All callbacks with optional userdata are now called with the ``userdata``
  parameter set to ``None``, which means they are called with the same number
  of parameters every time.
- Messages from the Spotify service (``log`` and ``user``) have been converted
  to ``unicode`` objects.

**New features**

- Exceptions raised in callbacks are written to ``stderr``
- :meth:`spotify.Session.search` now accepts Unicode queries
- Add user handling: :class:`spotify.User`
- Add toplist browsing: :class:`spotify.ToplistBrowser`
- Add new method: :meth:`spotify.Playlist.rename`
- Add new method: :meth:`spotify.Session.get_friends`. Contributed by Francisco
  Jordano.
- Add new method: :meth:`spotify.Playlist.add_tracks`. Contributed by Andreas
  Franzén.
- Add new method: :meth:`spotify.PlaylistContainer.add_new_playlist`.
  Contributed by Andreas Franzén.

**Bug fixes**

- :meth:`spotify.manager.SpotifySessionManager.log_message` callback used
  ``str`` in place of ``unicode``
- :meth:`spotify.manager.SpotifySessionManager.message_to_user` callback used
  ``str`` in place of ``unicode``
- Argument errors were unchecked in :meth:`spotify.Session.search`
- Fix crash on valid error at image creation. Fixed by Jamie Kirkpatrick.
- Keep compatibility with Python 2.5. Contributed by Jamie Kirkpatrick.
- Callbacks given at artist/album browser creation are now called by pyspotify.
  Fixed by Jamie Kirkpatrick.
- Fix exception when a ``long`` was returned from
  :meth:`spotify.manager.SpotifySessionManager.music_delivery`


v1.3 (2011-06-11)
=================

It has only been four days since the v1.2 release, but we would like to get the
change from bytestrings to unicode objects released before more projects start
using pyspotify, as this change is really backwards incompatible.

- All strings returned by pyspotify has been changed from UTF-8 encoded
  bytestrings to unicode objects.
- Track autolinking enabled for all playlists.
- Add :attr:`spotify.__version__` which exposes the current pyspotify version.
  The API version of the libspotify used is already available as
  :attr:`spotify.api_version`.


v1.2 (2011-06-07)
=================

As of May 2011, Doug Winter transfered the maintenance of pyspotify to the
`Mopidy <http://www.mopidy.com/>`_ project. The Mopidy developers, which
depends upon pyspotify, have during the first half of 2011 been maintaining a
branch of pyspotify and related Debian packages, and done some unofficial
releases. With this change, we hope to get pyspotify up to speed again, and
make it a useful library both for Mopidy and other projects.

Lately, Antoine Pierlot-Garcin aka *bok* have been doing lots of work on
pyspotify, both on catching up with the features of libspotify, fixing and
extending the test suite, writing documentation, and on fixing bugs. A big
thanks to him!

- Upgraded to libspotify 0.0.8
- New managers: *SpotifyPlaylistManager* and *SpotifyContainerManager* \
  giving access to all the Playlist{,Container} callbacks
- Artist and Album browsing available. Contributed by Jamie Kirkpatrick.
- Added a method to stop the playback. Contributed by Jamie Kirkpatrick.
- Better error messages when not logged in and accessing user information
- Added support for a playlist of all starred tracks
- Get/Set starred status for a track
- Better memory management


v1.1+mopidy20110405 (2011-04-05)
================================

Unofficial release by the Mopidy developers.

- Exposed the track_is_local() check function. Contributed by Jamie
  Kirkpatrick.
- Fixed incorrect calls to determine track availability/locality. Contributed
  by Jamie Kirkpatrick.


v1.1+mopidy20110331 (2011-03-31)
================================

Unofficial release by the Mopidy developers.

- Pass error messages instead of error codes to session callbacks. Contributed
  by Antoine Pierlot-Garcin.
- Fixed an issue where all playlists would appar blank when starting up.
  Contributed by Jamie Kirkpatrick.
- Make new config flags default to 0. Thanks to Jamie Kirkpatrick and Antoine
  Pierlot-Garcin.


v1.1+mopidy20110330 (2011-03-30)
================================

Unofficial release by the Mopidy developers.

- Further updates for libspotify 0.0.7 support. Contributed by Antoine
  Pierlot-Garcin.


v1.1+mopidy20110223 (2011-02-23)
================================

Unofficial release by the Mopidy developers.

- Upgraded to libspotify 0.0.7. Contributed by Antoine Pierlot-Garcin.


v1.1+mopidy20110106 (2011-01-06)
================================

Unofficial release by the Mopidy developers.

- Upgraded to libspotify 0.0.6
- Add OSS support for sound output
- Add is_collaborative to playlists
- Add tracks_added playlist callback
- Add removed and moved callbacks for playlists
- Add remove_tracks to playlists
- Add seek support by mapping sp_session_player_seek
- Add support to set preferred bitrate
- Fix a segfault. Thanks to Valentin David.


v1.1 (2010-04-25)
=================

Last release by Doug Winter.

- Upgraded to libspotify 0.0.4
- See the git history for changes up to v1.1.

Contributors to pyspotify up until v1.1 includes:

- Doug Winter
- Stein Magnus Jodal
- Thomas Jost
- Ben Firshman
- Johannes Knutsen
