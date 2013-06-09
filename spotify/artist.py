from __future__ import unicode_literals

from spotify import ffi, lib
from spotify.utils import to_unicode


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
        name = to_unicode(lib.sp_artist_name(self.sp_artist))
        return name if name else None

    @property
    def link(self):
        """A :class:`Link` to the artist."""
        from spotify.link import Link
        return Link(self)

    # TODO Add sp_artist_* methods
