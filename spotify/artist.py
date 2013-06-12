from __future__ import unicode_literals

import spotify
from spotify import ffi, lib, utils


__all__ = [
    'Artist',
]


class Artist(object):
    """A Spotify artist."""

    def __init__(self, sp_artist):
        lib.sp_artist_add_ref(sp_artist)
        self.sp_artist = ffi.gc(sp_artist, lib.sp_artist_release)

    @property
    def name(self):
        """The artist's name.

        Will always return :class:`None` if the artist isn't loaded.
        """
        name = utils.to_unicode(lib.sp_artist_name(self.sp_artist))
        return name if name else None

    @property
    def is_loaded(self):
        """Whether the artist's data is loaded."""
        return bool(lib.sp_artist_is_loaded(self.sp_artist))

    def load(self, timeout=None):
        """Block until the artist's data is loaded.

        :param timeout: seconds before giving up and raising an exception
        :type timeout: float
        :returns: self
        """
        return utils.load(self, timeout=timeout)

    def portrait(self, image_size=None):
        """The artist's portrait :class:`Image`.

        ``image_size`` is an :class:`ImageSize` value, by default
        :attr:`ImageSize.NORMAL`.

        Will always return :class:`None` if the artist isn't loaded or the
        artist has no portrait.
        """
        if image_size is None:
            image_size = spotify.ImageSize.NORMAL
        portrait_id = lib.sp_artist_portrait(self.sp_artist, image_size)
        if portrait_id == ffi.NULL:
            return None
        sp_image = lib.sp_image_create(
            spotify.session_instance.sp_session, portrait_id)
        return spotify.Image(sp_image, add_ref=False)

    @property
    def link(self):
        """A :class:`Link` to the artist."""
        from spotify.link import Link
        return Link(self)
