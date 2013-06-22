from __future__ import unicode_literals

import spotify
from spotify import ffi, lib, utils


__all__ = [
    'LocalTrack',
    'Track',
    'TrackAvailability',
    'TrackOfflineStatus',
]


class Track(object):
    """A Spotify track.

    You can get tracks from playlists or albums, or you can create a
    :class:`Track` yourself from a Spotify URI::

        >>> track = spotify.Track('spotify:track:2Foc5Q5nqNiosCNqttzHof')
        >>> track.load().name
        u'Get Lucky'
    """

    def __init__(self, uri=None, sp_track=None, add_ref=True):
        assert uri or sp_track, 'uri or sp_track is required'
        if uri is not None:
            track = spotify.Link(uri).as_track()
            if track is None:
                raise ValueError(
                    'Failed to get track from Spotify URI: %r' % uri)
            sp_track = track._sp_track
            add_ref = True
        if add_ref:
            lib.sp_track_add_ref(sp_track)
        self._sp_track = ffi.gc(sp_track, lib.sp_track_release)

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

        :param timeout: seconds before giving up and raising an exception
        :type timeout: float
        :returns: self
        """
        return utils.load(self, timeout=timeout)

    @property
    def offline_status(self):
        """The :class:`TrackOfflineStatus` of the track.

        The :attr:`~SessionCallbacks.metadata_updated` callback is called when
        the offline status changes.
        """
        spotify.Error.maybe_raise(self.error)
        # TODO What happens here if the track is unloaded?
        return TrackOfflineStatus(
            lib.sp_track_offline_get_status(self._sp_track))

    @property
    def availability(self):
        """The :class:`TrackAvailability` of the track."""
        if spotify.session_instance is None:
            raise RuntimeError('Session must be initialized')
        spotify.Error.maybe_raise(self.error)
        # TODO What happens here if the track is unloaded?
        return TrackAvailability(lib.sp_track_get_availability(
            spotify.session_instance._sp_session, self._sp_track))

    @property
    def is_local(self):
        """Whether the track is a local track.

        Will always return :class:`None` if the track isn't loaded.
        """
        if spotify.session_instance is None:
            raise RuntimeError('Session must be initialized')
        spotify.Error.maybe_raise(self.error)
        if not self.is_loaded:
            return None
        return bool(lib.sp_track_is_local(
            spotify.session_instance._sp_session, self._sp_track))

    @property
    def is_autolinked(self):
        """Whether the track is a autolinked to another track.

        Will always return :class:`None` if the track isn't loaded.

        See :meth:`playable`.
        """
        if spotify.session_instance is None:
            raise RuntimeError('Session must be initialized')
        spotify.Error.maybe_raise(self.error)
        if not self.is_loaded:
            return None
        return bool(lib.sp_track_is_autolinked(
            spotify.session_instance._sp_session, self._sp_track))

    @property
    def playable(self):
        """The actual track that will be played when this track is played.

        See :meth:`is_autolinked`.
        """
        if spotify.session_instance is None:
            raise RuntimeError('Session must be initialized')
        spotify.Error.maybe_raise(self.error)
        # TODO What happens here if the track is unloaded?
        return Track(sp_track=lib.sp_track_get_playable(
            spotify.session_instance._sp_session, self._sp_track))

    @property
    def is_placeholder(self):
        """Whether the track is a placeholder for a non-track object in the
        playlist.

        To convert to the real object::

            >>> track = spotify.Track('spotify:track:2Foc5Q5nqNiosCNqttzHof')
            >>> track.load()
            >>> track.is_placeholder
            True
            >>> track.link.type
            <LinkType.ARTIST: ...>
            >>> artist = track.link.as_artist()
        """
        spotify.Error.maybe_raise(self.error)
        # TODO What happens here if the track is unloaded?
        return bool(lib.sp_track_is_placeholder(self._sp_track))

    def is_starred(self):
        if spotify.session_instance is None:
            raise RuntimeError('Session must be initialized')
        spotify.Error.maybe_raise(self.error)
        if not self.is_loaded:
            return None
        return bool(lib.sp_track_is_starred(
            spotify.session_instance._sp_session, self._sp_track))

    def set_starred(self, star=True):
        if spotify.session_instance is None:
            raise RuntimeError('Session must be initialized')
        tracks = ffi.new('sp_track *[]', 1)
        tracks[0] = self._sp_track
        spotify.Error.maybe_raise(lib.sp_track_set_starred(
            spotify.session_instance._sp_session, tracks, len(tracks), star))

    starred = property(is_starred, set_starred)
    """Whether the track is starred by the current user.

    Set to :class:`True` or :class:`False` to change.

    Will always return :class:`None` if the track isn't loaded.
    """

    @property
    def artists(self):
        """The artists performing on the track.

        Will always return :class:`None` if the track isn't loaded.
        """
        # TODO Replace with collections.Sequence subclass
        # TODO Return empty list if not loaded
        spotify.Error.maybe_raise(self.error)
        if not self.is_loaded:
            return None
        num_artists = lib.sp_track_num_artists(self._sp_track)
        artists = []
        for i in range(num_artists):
            artists.append(spotify.Artist(
                sp_artist=lib.sp_track_artist(self._sp_track, i)))
        return artists

    @property
    def album(self):
        """The album of the track.

        Will always return :class:`None` if the track isn't loaded.
        """
        spotify.Error.maybe_raise(self.error)
        sp_album = lib.sp_track_album(self._sp_track)
        return spotify.Album(sp_album=sp_album) if sp_album else None

    @property
    def name(self):
        """The track's name.

        Will always return :class:`None` if the track isn't loaded.
        """
        spotify.Error.maybe_raise(self.error)
        name = utils.to_unicode(lib.sp_track_name(self._sp_track))
        return name if name else None

    @property
    def duration(self):
        """The track's duration in milliseconds.

        Will always return :class:`None` if the track isn't loaded.
        """
        spotify.Error.maybe_raise(self.error)
        duration = lib.sp_track_duration(self._sp_track)
        return duration if duration else None

    @property
    def popularity(self):
        """The track's popularity in the range 0-100, 0 if undefined.

        Will always return :class:`None` if the track isn't loaded.
        """
        spotify.Error.maybe_raise(self.error)
        if not self.is_loaded:
            return None
        return lib.sp_track_popularity(self._sp_track)

    @property
    def disc(self):
        """The track's disc number. 1 or higher.

        Will always return :class:`None` if the track isn't part of an album or
        artist browser.
        """
        spotify.Error.maybe_raise(self.error)
        disc = lib.sp_track_disc(self._sp_track)
        return disc if disc else None

    @property
    def index(self):
        """The track's index number. 1 or higher.

        Will always return :class:`None` if the track isn't part of an album or
        artist browser.
        """
        spotify.Error.maybe_raise(self.error)
        index = lib.sp_track_index(self._sp_track)
        return index if index else None

    @property
    def link(self):
        """A :class:`Link` to the track."""
        return spotify.Link(self, offset=0)

    def link_with_offset(self, offset):
        """A :class:`Link` to the track with an ``offset`` in milliseconds into
        the track."""
        return spotify.Link(self, offset=offset)


class LocalTrack(Track):
    """A Spotify local track.

    TODO: Explain what a local track is. libspotify docs doesn't say much, but
    there are more details in Hallon's docs.
    """

    def __init__(self, artist=None, title=None, album=None, length=None):
        convert = lambda value: ffi.NULL if value is None else ffi.new(
            'char[]', utils.to_bytes(value))

        artist = convert(artist)
        title = convert(title)
        album = convert(album)
        if length is None:
            length = -1

        sp_track = lib.sp_localtrack_create(artist, title, album, length)

        super(LocalTrack, self).__init__(sp_track=sp_track, add_ref=False)


@utils.make_enum('SP_TRACK_AVAILABILITY_')
class TrackAvailability(utils.IntEnum):
    pass


@utils.make_enum('SP_TRACK_OFFLINE_')
class TrackOfflineStatus(utils.IntEnum):
    pass
