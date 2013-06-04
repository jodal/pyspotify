from __future__ import unicode_literals

import spotify
from spotify import ffi, lib
from spotify.utils import get_with_growing_buffer, IntEnum, make_enum, to_bytes


__all__ = [
    'Link',
    'LinkType',
]


class Link(object):
    """A Spotify object link.

    You must create a :class:`Session` before you can create links.

    ``value`` can either be a string containing a Spotify URI on the form
    ``spotify:...``, or a :class:`Track`, :class:`Album`, :class:`Artist`,
    :class:`Search`, :class:`Playlist`, :class:`User`, or :class:`Image`.

    If ``value`` is a :class:`Track`, ``offset`` will be used as the position
    in milliseconds into the track to link to.

    If ``value`` is an :class:`Album` or an :class:`Artist` and ``image_size``
    is an :class:`ImageSize`, then the link will point to an album cover or
    artist portrait.

    To get the URI from the link object, use it as a string::

        >>> link = spotify.Link('spotify:track:2Foc5Q5nqNiosCNqttzHof')
        >>> str(link)
        'spotify:track:2Foc5Q5nqNiosCNqttzHof'
        >>> track = link.as_track()
        >>> str(track.as_link())
        'spotify:track:2Foc5Q5nqNiosCNqttzHof'
    """

    def __init__(self, value, offset=0, image_size=None):
        if spotify.session_instance is None:
            raise RuntimeError('Session must be initialized to create links')

        # TODO Add support for creating link from a sp_artistbrowse instance

        if isinstance(value, spotify.Track):
            sp_link = lib.sp_link_create_from_track(value.sp_track, offset)
        elif isinstance(value, spotify.Album):
            if image_size is not None:
                sp_link = lib.sp_link_create_from_album_cover(
                    value.sp_album, image_size)
            else:
                sp_link = lib.sp_link_create_from_album(value.sp_album)
        elif isinstance(value, spotify.Artist):
            if image_size is not None:
                sp_link = lib.sp_link_create_from_artist_portrait(
                    value.sp_artist, image_size)
            else:
                sp_link = lib.sp_link_create_from_artist(value.sp_artist)
        elif isinstance(value, spotify.Search):
            sp_link = lib.sp_link_create_from_search(value.sp_search)
        elif isinstance(value, spotify.Playlist):
            sp_link = lib.sp_link_create_from_playlist(value.sp_playlist)
        elif isinstance(value, spotify.User):
            sp_link = lib.sp_link_create_from_user(value.sp_user)
        elif isinstance(value, spotify.Image):
            sp_link = lib.sp_link_create_from_image(value.sp_image)
        else:
            sp_link = lib.sp_link_create_from_string(
                ffi.new('char[]', to_bytes(value)))
            if sp_link == ffi.NULL:
                raise ValueError(
                    'Failed to get link from Spotify URI: %r' % value)

        self.sp_link = ffi.gc(sp_link, lib.sp_link_release)

    def __str__(self):
        return get_with_growing_buffer(lib.sp_link_as_string, self.sp_link)

    @property
    def type(self):
        """The link's :class:`LinkType`."""
        return lib.sp_link_type(self.sp_link)

    def as_track(self):
        """Make a :class:`Track` from the link."""
        sp_track = lib.sp_link_as_track(self.sp_link)
        if sp_track:
            return spotify.Track(sp_track)

    def as_track_offset(self):
        """Get the track offset in milliseconds from the link."""
        offset = ffi.new('int *')
        sp_track = lib.sp_link_as_track_and_offset(self.sp_link, offset)
        if sp_track:
            return offset[0]

    def as_album(self):
        """Make an :class:`Album` from the link."""
        sp_album = lib.sp_link_as_album(self.sp_link)
        if sp_album:
            return spotify.Album(sp_album)

    def as_artist(self):
        """Make an :class:`Artist` from the link."""
        sp_artist = lib.sp_link_as_artist(self.sp_link)
        if sp_artist:
            return spotify.Artist(sp_artist)

    def as_user(self):
        """Make a :class:`User` from the link."""
        sp_user = lib.sp_link_as_user(self.sp_link)
        if sp_user:
            return spotify.User(sp_user)


@make_enum('SP_LINKTYPE_')
class LinkType(IntEnum):
    pass
