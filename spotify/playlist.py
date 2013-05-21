from __future__ import unicode_literals

from spotify import ffi, lib


__all__ = [
    'Playlist',
    'PlaylistContainer',
]


class Playlist(object):
    """A Spotify playlist."""

    def __init__(self, sp_playlist):
        lib.sp_playlist_add_ref(sp_playlist)
        self.sp_playlist = ffi.gc(sp_playlist, lib.sp_playlist_release)

    def as_link(self):
        """Make a :class:`Link` to the playlist."""
        from spotify.link import Link
        return Link(self)

    # TODO Add sp_playlist_* methods


class PlaylistContainer(object):
    """A Spotify playlist container."""

    pass

    # TODO Add sp_playlistcontainer_* methods
