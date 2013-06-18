from __future__ import unicode_literals

from spotify import ffi, lib


__all__ = [
    'Playlist',
    'PlaylistContainer',
]


class Playlist(object):
    """A Spotify playlist."""

    def __init__(self, sp_playlist, add_ref=True):
        if add_ref:
            lib.sp_playlist_add_ref(sp_playlist)
        self._sp_playlist = ffi.gc(sp_playlist, lib.sp_playlist_release)

    @property
    def link(self):
        """A :class:`Link` to the playlist."""
        from spotify.link import Link
        return Link(self)

    # TODO Add sp_playlist_* methods


class PlaylistContainer(object):
    """A Spotify playlist container."""

    def __init__(self, sp_playlistcontainer, add_ref=True):
        if add_ref:
            lib.sp_playlistcontainer_add_ref(sp_playlistcontainer)
        self._sp_playlistcontainer = ffi.gc(
            sp_playlistcontainer, lib.sp_playlistcontainer_release)

    # TODO Add sp_playlistcontainer_* methods