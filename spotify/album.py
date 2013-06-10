from __future__ import unicode_literals

import spotify
from spotify import Artist, ffi, Image, ImageSize, lib
from spotify.utils import IntEnum, load, make_enum, to_unicode


__all__ = [
    'Album',
    'AlbumType',
]


class Album(object):
    """A Spotify album."""

    def __init__(self, sp_album):
        lib.sp_album_add_ref(sp_album)
        self.sp_album = ffi.gc(sp_album, lib.sp_album_release)

    @property
    def is_loaded(self):
        """Whether the album's data is loaded."""
        return bool(lib.sp_album_is_loaded(self.sp_album))

    def load(self, timeout=None):
        """Block until the album's data is loaded.

        :param timeout: seconds before giving up and raising an exception
        :type timeout: float
        :returns: self
        """
        return load(self, timeout=timeout)

    @property
    def is_available(self):
        """Whether the album is available in the current region.

        Will always return :class:`None` if the album isn't loaded.
        """
        if not self.is_loaded:
            return None
        return bool(lib.sp_album_is_available(self.sp_album))

    @property
    def artist(self):
        """The artist of the album.

        Will always return :class:`None` if the album isn't loaded.
        """
        sp_artist = lib.sp_album_artist(self.sp_album)
        return Artist(sp_artist) if sp_artist else None

    def cover(self, image_size=ImageSize.NORMAL):
        """The album's cover :class:`Image`.

        ``image_size`` is an :class:`ImageSize` value, by default
        :attr:`ImageSize.NORMAL`.

        Will always return :class:`None` if the album isn't loaded or the
        album has no cover.
        """
        cover_id = lib.sp_album_cover(self.sp_album, image_size)
        if cover_id == ffi.NULL:
            return None
        sp_image = lib.sp_image_create(
            spotify.session_instance.sp_session, cover_id)
        return Image(sp_image, add_ref=False)

    @property
    def name(self):
        """The album's name.

        Will always return :class:`None` if the album isn't loaded.
        """
        name = to_unicode(lib.sp_album_name(self.sp_album))
        return name if name else None

    @property
    def year(self):
        """The album's release year.

        Will always return :class:`None` if the album isn't loaded.
        """
        if not self.is_loaded:
            return None
        return lib.sp_album_year(self.sp_album)

    @property
    def type(self):
        """The album's :class:`AlbumType`.

        Will always return :class:`None` if the album isn't loaded.
        """
        if not self.is_loaded:
            return None
        return AlbumType(lib.sp_album_type(self.sp_album))

    @property
    def link(self):
        """A :class:`Link` to the album."""
        from spotify.link import Link
        return Link(self)


@make_enum('SP_ALBUMTYPE_')
class AlbumType(IntEnum):
    pass
