from __future__ import unicode_literals

import spotify
from spotify import ffi, lib, serialized, utils

__all__ = ["Track", "TrackAvailability", "TrackOfflineStatus"]


class Track(object):

    """A Spotify track.

    You can get tracks from playlists or albums, or you can create a
    :class:`Track` yourself from a Spotify URI::

        >>> session = spotify.Session()
        # ...
        >>> track = session.get_track('spotify:track:2Foc5Q5nqNiosCNqttzHof')
        >>> track.load().name
        u'Get Lucky'
    """

    def __init__(self, session, uri=None, sp_track=None, add_ref=True):
        assert uri or sp_track, "uri or sp_track is required"

        self._session = session

        if uri is not None:
            track = spotify.Link(self._session, uri=uri).as_track()
            if track is None:
                raise ValueError("Failed to get track from Spotify URI: %r" % uri)
            sp_track = track._sp_track
            add_ref = True

        if add_ref:
            lib.sp_track_add_ref(sp_track)
        self._sp_track = ffi.gc(sp_track, lib.sp_track_release)

    def __repr__(self):
        return "Track(%r)" % self.link.uri

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._sp_track == other._sp_track
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self._sp_track)

    @property
    def is_loaded(self):
        """Whether the track's data is loaded."""
        return bool(lib.sp_track_is_loaded(self._sp_track))

    @property
    def error(self):
        """An :class:`ErrorType` associated with the track.

        Check to see if there was problems loading the track.
        """
        return spotify.ErrorType(lib.sp_track_error(self._sp_track))

    def load(self, timeout=None):
        """Block until the track's data is loaded.

        After ``timeout`` seconds with no results :exc:`~spotify.Timeout` is
        raised. If ``timeout`` is :class:`None` the default timeout is used.

        The method returns ``self`` to allow for chaining of calls.
        """
        return utils.load(self._session, self, timeout=timeout)

    @property
    def offline_status(self):
        """The :class:`TrackOfflineStatus` of the track.

        The :attr:`~SessionCallbacks.metadata_updated` callback is called when
        the offline status changes.

        Will always return :class:`None` if the track isn't loaded.
        """
        spotify.Error.maybe_raise(self.error, ignores=[spotify.ErrorType.IS_LOADING])
        if not self.is_loaded:
            return None
        return TrackOfflineStatus(lib.sp_track_offline_get_status(self._sp_track))

    @property
    def availability(self):
        """The :class:`TrackAvailability` of the track.

        Will always return :class:`None` if the track isn't loaded.
        """
        spotify.Error.maybe_raise(self.error, ignores=[spotify.ErrorType.IS_LOADING])
        if not self.is_loaded:
            return None
        return TrackAvailability(
            lib.sp_track_get_availability(self._session._sp_session, self._sp_track)
        )

    @property
    def is_local(self):
        """Whether the track is a local track.

        Will always return :class:`None` if the track isn't loaded.
        """
        spotify.Error.maybe_raise(self.error, ignores=[spotify.ErrorType.IS_LOADING])
        if not self.is_loaded:
            return None
        return bool(lib.sp_track_is_local(self._session._sp_session, self._sp_track))

    @property
    def is_autolinked(self):
        """Whether the track is a autolinked to another track.

        Will always return :class:`None` if the track isn't loaded.

        See :attr:`playable`.
        """
        spotify.Error.maybe_raise(self.error, ignores=[spotify.ErrorType.IS_LOADING])
        if not self.is_loaded:
            return None
        return bool(
            lib.sp_track_is_autolinked(self._session._sp_session, self._sp_track)
        )

    @property
    @serialized
    def playable(self):
        """The actual track that will be played when this track is played.

        Will always return :class:`None` if the track isn't loaded.

        See :attr:`is_autolinked`.
        """
        spotify.Error.maybe_raise(self.error, ignores=[spotify.ErrorType.IS_LOADING])
        if not self.is_loaded:
            return None
        return Track(
            self._session,
            sp_track=lib.sp_track_get_playable(
                self._session._sp_session, self._sp_track
            ),
            add_ref=True,
        )

    @property
    def is_placeholder(self):
        """Whether the track is a placeholder for a non-track object in the
        playlist.

        To convert to the real object::

            >>> session = spotify.Session()
            # ...
            >>> track = session.get_track(
            ...     'spotify:track:2Foc5Q5nqNiosCNqttzHof')
            >>> track.load()
            >>> track.is_placeholder
            True
            >>> track.link.type
            <LinkType.ARTIST: ...>
            >>> artist = track.link.as_artist()

        Will always return :class:`None` if the track isn't loaded.
        """
        spotify.Error.maybe_raise(self.error, ignores=[spotify.ErrorType.IS_LOADING])
        if not self.is_loaded:
            return None
        return bool(lib.sp_track_is_placeholder(self._sp_track))

    @property
    def starred(self):
        """Whether the track is starred by the current user.

        Set to :class:`True` or :class:`False` to change.

        Will always be :class:`None` if the track isn't loaded.
        """
        spotify.Error.maybe_raise(self.error, ignores=[spotify.ErrorType.IS_LOADING])
        if not self.is_loaded:
            return None
        return bool(lib.sp_track_is_starred(self._session._sp_session, self._sp_track))

    @starred.setter
    def starred(self, value):
        tracks = ffi.new("sp_track *[]", 1)
        tracks[0] = self._sp_track
        spotify.Error.maybe_raise(
            lib.sp_track_set_starred(
                self._session._sp_session, tracks, len(tracks), bool(value)
            )
        )

    @property
    @serialized
    def artists(self):
        """The artists performing on the track.

        Will always return an empty list if the track isn't loaded.
        """
        spotify.Error.maybe_raise(self.error, ignores=[spotify.ErrorType.IS_LOADING])
        if not self.is_loaded:
            return []

        @serialized
        def get_artist(sp_track, key):
            return spotify.Artist(
                self._session,
                sp_artist=lib.sp_track_artist(sp_track, key),
                add_ref=True,
            )

        return utils.Sequence(
            sp_obj=self._sp_track,
            add_ref_func=lib.sp_track_add_ref,
            release_func=lib.sp_track_release,
            len_func=lib.sp_track_num_artists,
            getitem_func=get_artist,
        )

    @property
    @serialized
    def album(self):
        """The album of the track.

        Will always return :class:`None` if the track isn't loaded.
        """
        spotify.Error.maybe_raise(self.error, ignores=[spotify.ErrorType.IS_LOADING])
        if not self.is_loaded:
            return None
        sp_album = lib.sp_track_album(self._sp_track)
        return spotify.Album(self._session, sp_album=sp_album, add_ref=True)

    @property
    @serialized
    def name(self):
        """The track's name.

        Will always return :class:`None` if the track isn't loaded.
        """
        spotify.Error.maybe_raise(self.error, ignores=[spotify.ErrorType.IS_LOADING])
        if not self.is_loaded:
            return None
        return utils.to_unicode(lib.sp_track_name(self._sp_track))

    @property
    def duration(self):
        """The track's duration in milliseconds.

        Will always return :class:`None` if the track isn't loaded.
        """
        spotify.Error.maybe_raise(self.error, ignores=[spotify.ErrorType.IS_LOADING])
        if not self.is_loaded:
            return None
        return lib.sp_track_duration(self._sp_track)

    @property
    def popularity(self):
        """The track's popularity in the range 0-100, 0 if undefined.

        Will always return :class:`None` if the track isn't loaded.
        """
        spotify.Error.maybe_raise(self.error, ignores=[spotify.ErrorType.IS_LOADING])
        if not self.is_loaded:
            return None
        return lib.sp_track_popularity(self._sp_track)

    @property
    def disc(self):
        """The track's disc number. 1 or higher.

        Will always return :class:`None` if the track isn't part of an album or
        artist browser.
        """
        spotify.Error.maybe_raise(self.error, ignores=[spotify.ErrorType.IS_LOADING])
        if not self.is_loaded:
            return None
        return lib.sp_track_disc(self._sp_track)

    @property
    def index(self):
        """The track's index number. 1 or higher.

        Will always return :class:`None` if the track isn't part of an album or
        artist browser.
        """
        spotify.Error.maybe_raise(self.error, ignores=[spotify.ErrorType.IS_LOADING])
        if not self.is_loaded:
            return None
        return lib.sp_track_index(self._sp_track)

    @property
    def link(self):
        """A :class:`Link` to the track."""
        return self.link_with_offset(0)

    def link_with_offset(self, offset):
        """A :class:`Link` to the track with an ``offset`` in milliseconds into
        the track."""
        return spotify.Link(
            self._session,
            sp_link=lib.sp_link_create_from_track(self._sp_track, offset),
            add_ref=False,
        )


@utils.make_enum("SP_TRACK_AVAILABILITY_")
class TrackAvailability(utils.IntEnum):
    pass


@utils.make_enum("SP_TRACK_OFFLINE_")
class TrackOfflineStatus(utils.IntEnum):
    pass
