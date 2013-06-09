from __future__ import unicode_literals

from spotify import Artist, ffi, lib
from spotify.utils import load


__all__ = [
    'Album',
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

    @property
    def link(self):
        """A :class:`Link` to the album."""
        from spotify.link import Link
        return Link(self)

    # TODO Add sp_album_* methods
