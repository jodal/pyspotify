=======
Changes
=======

v1.4 (in development)
=====================

- New Playlist method: rename.

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
- Artist and Album browsing available
- Added a method to stop the playback
- Better error messages when not logged in and accessing user information
- Added support for a playlist of all starred tracks
- Get/Set starred status for a track
- Better memory management

v1.1+mopidy20110405 (2011-04-05)
================================

Unofficial release by the Mopidy developers.

- Exposed the track_is_local() check function
- Fixed incorrect calls to determine track availability/locality

v1.1+mopidy20110331 (2011-03-31)
================================

Unofficial release by the Mopidy developers.

- Pass error messages instead of error codes to session callbacks
- Fixed an issue where all playlists would appar blank when starting up
- Make new config flags default to 0

v1.1+mopidy20110330 (2011-03-30)
================================

Unofficial release by the Mopidy developers.

- Further updates for libspotify 0.0.7 support

v1.1+mopidy20110223 (2011-02-23)
================================

Unofficial release by the Mopidy developers.

- Upgraded to libspotify 0.0.7

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
- Fix a segfault (Thanks to Valentin David)

v1.1 (2010-04-25)
=================

Last release by Doug Winter. See the git history for changes up to v1.1.

- Upgraded to libspotify 0.0.4
- ...
