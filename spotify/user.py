from __future__ import unicode_literals

import spotify
from spotify import ffi, lib, utils


__all__ = [
    'User',
]


class User(object):
    """A Spotify user."""

    def __init__(self, sp_user):
        lib.sp_user_add_ref(sp_user)
        self.sp_user = ffi.gc(sp_user, lib.sp_user_release)

    @property
    def canonical_name(self):
        """The user's canonical username."""
        return utils.to_unicode(lib.sp_user_canonical_name(self.sp_user))

    @property
    def display_name(self):
        """The user's displayable username."""
        return utils.to_unicode(lib.sp_user_display_name(self.sp_user))

    @property
    def is_loaded(self):
        """Whether the user's data is loaded yet."""
        return bool(lib.sp_user_is_loaded(self.sp_user))

    def load(self, timeout=None):
        """Block until the user's data is loaded.

        :param timeout: seconds before giving up and raising an exception
        :type timeout: float
        :returns: self
        """
        return utils.load(self, timeout=timeout)

    @property
    def link(self):
        """A :class:`Link` to the user."""
        from spotify.link import Link
        return Link(self)

    @property
    def starred(self):
        """The :class:`Playlist` of tracks starred by the user."""
        if spotify.session_instance is None:
            return None
        return spotify.session_instance.starred_for_user(self.canonical_name)

    @property
    def published_container(self):
        """The :class:`PlaylistContainer` of playlists published by the
        user."""
        if spotify.session_instance is None:
            return None
        return spotify.session_instance.published_container_for_user(
            self.canonical_name)
