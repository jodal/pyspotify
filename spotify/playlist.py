from __future__ import unicode_literals

import spotify
from spotify import ffi, lib, utils


__all__ = [
    'Playlist',
    'PlaylistContainer',
]


class Playlist(object):
    """A Spotify playlist.

    You can get playlists from the :attr:`~Session.playlist_container`,
    :attr:`~Session.inbox`, :attr:`~Session.starred`,
    :meth:`~Session.starred_for_user`, :meth:`~Session.search`, etc., or you
    can create a playlist yourself from a Spotify URI::

        >>> playlist = spotify.Playlist(
        ...     'spotify:user:fiat500c:playlist:54k50VZdvtnIPt4d8RBCmZ')
        >>> playlist.load().name
        u'500C feelgood playlist'
    """

    def __init__(self, uri=None, sp_playlist=None, add_ref=True):
        assert uri or sp_playlist, 'uri or sp_playlist is required'
        if uri is not None:
            link = spotify.Link(uri)
            sp_playlist = lib.sp_playlist_create(
                spotify.session_instance._sp_session, link._sp_link)
            if sp_playlist is ffi.NULL:
                raise ValueError(
                    'Failed to get playlist from Spotify URI: %r' % uri)
            add_ref = False
        if add_ref:
            lib.sp_playlist_add_ref(sp_playlist)
        self._sp_playlist = ffi.gc(sp_playlist, lib.sp_playlist_release)

    @property
    def is_loaded(self):
        """Whether the playlist's data is loaded."""
        return bool(lib.sp_playlist_is_loaded(self._sp_playlist))

    def load(self, timeout=None):
        """Block until the playlist's data is loaded.

        :param timeout: seconds before giving up and raising an exception
        :type timeout: float
        :returns: self
        """
        return utils.load(self, timeout=timeout)

    @property
    def link(self):
        """A :class:`Link` to the playlist."""
        return spotify.Link(self)

    # TODO Add sp_playlist_* methods


class PlaylistContainer(object):
    """A Spotify playlist container."""

    def __init__(self, sp_playlistcontainer, add_ref=True):
        if add_ref:
            lib.sp_playlistcontainer_add_ref(sp_playlistcontainer)
        self._sp_playlistcontainer = ffi.gc(
            sp_playlistcontainer, lib.sp_playlistcontainer_release)

    # TODO Add sp_playlistcontainer_* methods
