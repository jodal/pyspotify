from __future__ import unicode_literals

from spotify import ffi, lib


__all__ = [
    'Artist',
]


class Artist(object):
    """A Spotify artist."""

    def __init__(self, sp_artist):
        lib.sp_artist_add_ref(sp_artist)
        self.sp_artist = ffi.gc(sp_artist, lib.sp_artist_release)

    def as_link(self):
        """Make a :class:`Link` to the artist."""
        from spotify.link import Link
        return Link(self)

    # TODO Add sp_artist_* methods
