from __future__ import unicode_literals

import spotify
from spotify import ffi, lib, utils


__all__ = [
    'Link',
    'LinkType',
]


class Link(object):
    """A Spotify object link.

    You must create a :class:`Session` before you can create links.

    A link can be created from one of the following:

    ``uri``:
        A string containing a Spotify URI on the form ``spotify:...``.

    ``obj``:
        One of :class:`Track`, :class:`Album`, :class:`Artist`,
        :class:`Search`, :class:`Playlist`, :class:`User`, or :class:`Image`.

    If ``obj`` is a :class:`Track`, ``offset`` will be used as the position
    in milliseconds into the track to link to.

    To get the URI from the link object, use it as a string or look at the
    :attr:`uri` attribute::

        >>> link = spotify.Link('spotify:track:2Foc5Q5nqNiosCNqttzHof')
        >>> str(link)
        'spotify:track:2Foc5Q5nqNiosCNqttzHof'
        >>> track = link.as_track()
        >>> str(track.link)
        'spotify:track:2Foc5Q5nqNiosCNqttzHof'
        >>> track.link.uri
        'spotify:track:2Foc5Q5nqNiosCNqttzHof'
    """

    def __init__(self, uri=None, obj=None, sp_link=None, offset=0):
        assert uri or obj or sp_link, 'uri, obj, or sp_link is required'

        if spotify.session_instance is None:
            raise RuntimeError('Session must be initialized to create links')

        # TODO Add support for creating link from a sp_artistbrowse instance

        if sp_link:
            self._sp_link = ffi.gc(sp_link, lib.sp_link_release)
        elif uri:
            sp_link = lib.sp_link_create_from_string(
                ffi.new('char[]', utils.to_bytes(uri)))
            if sp_link == ffi.NULL:
                raise ValueError(
                    'Failed to get link from Spotify URI: %r' % uri)
            self._sp_link = ffi.gc(sp_link, lib.sp_link_release)
        elif obj:
            if isinstance(obj, spotify.Track):
                sp_link = lib.sp_link_create_from_track(obj._sp_track, offset)
            else:
                self._sp_link = obj.link._sp_link
                return

            self._sp_link = ffi.gc(sp_link, lib.sp_link_release)

    def __repr__(self):
        return 'Link(%r)' % self.uri

    def __str__(self):
        return self.uri

    @property
    def uri(self):
        return utils.get_with_growing_buffer(
            lib.sp_link_as_string, self._sp_link)

    @property
    def type(self):
        """The link's :class:`LinkType`."""
        return LinkType(lib.sp_link_type(self._sp_link))

    def as_track(self):
        """Make a :class:`Track` from the link."""
        sp_track = lib.sp_link_as_track(self._sp_link)
        if sp_track:
            return spotify.Track(sp_track=sp_track)

    def as_track_offset(self):
        """Get the track offset in milliseconds from the link."""
        offset = ffi.new('int *')
        sp_track = lib.sp_link_as_track_and_offset(self._sp_link, offset)
        if sp_track:
            return offset[0]

    def as_album(self):
        """Make an :class:`Album` from the link."""
        sp_album = lib.sp_link_as_album(self._sp_link)
        if sp_album:
            return spotify.Album(sp_album=sp_album)

    def as_artist(self):
        """Make an :class:`Artist` from the link."""
        sp_artist = lib.sp_link_as_artist(self._sp_link)
        if sp_artist:
            return spotify.Artist(sp_artist=sp_artist)

    def as_playlist(self):
        """Make a :class:`Playlist` from the link."""
        if self.type is not LinkType.PLAYLIST:
            return None
        sp_playlist = lib.sp_playlist_create(
            spotify.session_instance._sp_session, self._sp_link)
        if sp_playlist:
            return spotify.Playlist(sp_playlist=sp_playlist, add_ref=False)

    def as_user(self):
        """Make an :class:`User` from the link."""
        sp_user = lib.sp_link_as_user(self._sp_link)
        if sp_user:
            return spotify.User(sp_user=sp_user)

    def as_image(self):
        """Make an :class:`Image` from the link."""
        if self.type is not LinkType.IMAGE:
            return None
        sp_image = lib.sp_image_create_from_link(
            spotify.session_instance._sp_session, self._sp_link)
        if sp_image:
            return spotify.Image(sp_image=sp_image, add_ref=False)


@utils.make_enum('SP_LINKTYPE_')
class LinkType(utils.IntEnum):
    pass
