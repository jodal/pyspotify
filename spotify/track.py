from __future__ import unicode_literals

import spotify
from spotify import Error, ErrorType, ffi, lib, Loadable
from spotify.utils import IntEnum, make_enum, to_bytes, to_unicode


__all__ = [
    'LocalTrack',
    'Track',
    'TrackAvailability',
    'TrackOfflineStatus',
]


class Track(Loadable):
    """A Spotify track."""

    def __init__(self, sp_track, add_ref=True):
        if add_ref:
            lib.sp_track_add_ref(sp_track)
        self.sp_track = ffi.gc(sp_track, lib.sp_track_release)

    @property
    def is_loaded(self):
        """Whether the track's data is loaded yet."""
        return bool(lib.sp_track_is_loaded(self.sp_track))

    @property
    def error(self):
        """An :class:`ErrorType` associated with the track.

        Check to see if there was problems loading the track.
        """
        return ErrorType(lib.sp_track_error(self.sp_track))

    @property
    def offline_status(self):
        """The :class:`TrackOfflineStatus` of the track.

        The :attr:`~SessionCallbacks.metadata_updated` callback is called when
        the offline status changes.
        """
        Error.maybe_raise(self.error)
        return TrackOfflineStatus(
            lib.sp_track_offline_get_status(self.sp_track))

    @property
    def availability(self):
        """The :class:`TrackAvailability` of the track."""
        if spotify.session_instance is None:
            raise RuntimeError('Session must be initialized')
        Error.maybe_raise(self.error)
        return TrackAvailability(lib.sp_track_get_availability(
            spotify.session_instance.sp_session, self.sp_track))

    @property
    def is_local(self):
        """Whether the track is a local track.

        Will always return :class:`False` if the track isn't loaded.
        """
        if spotify.session_instance is None:
            raise RuntimeError('Session must be initialized')
        Error.maybe_raise(self.error)
        return bool(lib.sp_track_is_local(
            spotify.session_instance.sp_session, self.sp_track))

    @property
    def is_autolinked(self):
        """Whether the track is a autolinked to another track.

        Will always return :class:`False` if the track isn't loaded.

        See :meth:`playable`.
        """
        if spotify.session_instance is None:
            raise RuntimeError('Session must be initialized')
        Error.maybe_raise(self.error)
        return bool(lib.sp_track_is_autolinked(
            spotify.session_instance.sp_session, self.sp_track))

    @property
    def playable(self):
        """The actual track that will be played when this track is played.

        See :meth:`is_autolinked`.
        """
        if spotify.session_instance is None:
            raise RuntimeError('Session must be initialized')
        Error.maybe_raise(self.error)
        return Track(lib.sp_track_get_playable(
            spotify.session_instance.sp_session, self.sp_track))

    @property
    def is_placeholder(self):
        """Whether the track is a placeholder for a non-track object in the
        playlist.

        To convert to the real object::

            >>> track.is_placeholder
            True
            >>> link = track.as_link()
            >>> link.type
            <LinkType.ARTIST: ...>
            >>> artist = link.as_artist()
        """
        Error.maybe_raise(self.error)
        return bool(lib.sp_track_is_placeholder(self.sp_track))

    @property
    def name(self):
        """The track's name. Empty if the track is not loaded yet."""
        if spotify.session_instance is None:
            raise RuntimeError('Session must be initialized')
        Error.maybe_raise(self.error)
        return to_unicode(lib.sp_track_name(self.sp_track))

    def as_link(self, offset=0):
        """Make a :class:`Link` to the track.

        ``offset`` is the number of milliseconds into the track the link should
        point.
        """
        from spotify.link import Link
        return Link(self, offset=offset)

    # TODO Add sp_track_* methods


class LocalTrack(Track):
    """A Spotify local track.

    TODO: Explain what a local track is. libspotify docs doesn't say much, but
    there are more details in Hallon's docs.
    """

    def __init__(self, artist=None, title=None, album=None, length=None):
        convert = lambda value: ffi.NULL if value is None else ffi.new(
            'char[]', to_bytes(value))

        artist = convert(artist)
        title = convert(title)
        album = convert(album)
        if length is None:
            length = -1

        sp_track = lib.sp_localtrack_create(artist, title, album, length)

        super(LocalTrack, self).__init__(sp_track, add_ref=False)


@make_enum('SP_TRACK_AVAILABILITY_')
class TrackAvailability(IntEnum):
    pass


@make_enum('SP_TRACK_OFFLINE_')
class TrackOfflineStatus(IntEnum):
    pass
