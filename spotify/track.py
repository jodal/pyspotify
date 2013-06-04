from __future__ import unicode_literals

from spotify import ErrorType, ffi, lib, Loadable
from spotify.utils import to_bytes, to_unicode


__all__ = [
    'LocalTrack',
    'Track',
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
    def name(self):
        """The track's name. Empty if the track is not loaded yet."""
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
