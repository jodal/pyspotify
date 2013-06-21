from __future__ import unicode_literals

import spotify
from spotify import ffi, lib, utils


__all__ = [
    'Album',
    'AlbumType',
]


class Album(object):
    """A Spotify album.

    You can get an album from a track or an artist, or you can create an
    :class:`Album` yourself from a Spotify URI::

        >>> album = spotify.Album('spotify:album:6wXDbHLesy6zWqQawAa91d')
        >>> album.load().name
        u'Forward / Return'
    """

    def __init__(self, uri=None, sp_album=None):
        assert uri or sp_album, 'uri or sp_album is required'
        if uri is not None:
            link = spotify.Link(uri)
            sp_album = lib.sp_link_as_album(link._sp_link)
            if sp_album is ffi.NULL:
                raise ValueError(
                    'Failed to get album from Spotify URI: %r' % uri)
        lib.sp_album_add_ref(sp_album)
        self._sp_album = ffi.gc(sp_album, lib.sp_album_release)

    @property
    def is_loaded(self):
        """Whether the album's data is loaded."""
        return bool(lib.sp_album_is_loaded(self._sp_album))

    def load(self, timeout=None):
        """Block until the album's data is loaded.

        :param timeout: seconds before giving up and raising an exception
        :type timeout: float
        :returns: self
        """
        # TODO Need to send a browse request for the object to be populated
        # with data
        return utils.load(self, timeout=timeout)

    @property
    def is_available(self):
        """Whether the album is available in the current region.

        Will always return :class:`None` if the album isn't loaded.
        """
        if not self.is_loaded:
            return None
        return bool(lib.sp_album_is_available(self._sp_album))

    @property
    def artist(self):
        """The artist of the album.

        Will always return :class:`None` if the album isn't loaded.
        """
        sp_artist = lib.sp_album_artist(self._sp_album)
        return spotify.Artist(sp_artist=sp_artist) if sp_artist else None

    def cover(self, image_size=None):
        """The album's cover :class:`Image`.

        ``image_size`` is an :class:`ImageSize` value, by default
        :attr:`ImageSize.NORMAL`.

        Will always return :class:`None` if the album isn't loaded or the
        album has no cover.
        """
        if image_size is None:
            image_size = spotify.ImageSize.NORMAL
        cover_id = lib.sp_album_cover(self._sp_album, image_size)
        if cover_id == ffi.NULL:
            return None
        sp_image = lib.sp_image_create(
            spotify.session_instance._sp_session, cover_id)
        return spotify.Image(sp_image=sp_image, add_ref=False)

    @property
    def name(self):
        """The album's name.

        Will always return :class:`None` if the album isn't loaded.
        """
        name = utils.to_unicode(lib.sp_album_name(self._sp_album))
        return name if name else None

    @property
    def year(self):
        """The album's release year.

        Will always return :class:`None` if the album isn't loaded.
        """
        if not self.is_loaded:
            return None
        return lib.sp_album_year(self._sp_album)

    @property
    def type(self):
        """The album's :class:`AlbumType`.

        Will always return :class:`None` if the album isn't loaded.
        """
        if not self.is_loaded:
            return None
        return AlbumType(lib.sp_album_type(self._sp_album))

    @property
    def link(self):
        """A :class:`Link` to the album."""
        return spotify.Link(self)


@utils.make_enum('SP_ALBUMTYPE_')
class AlbumType(utils.IntEnum):
    pass
