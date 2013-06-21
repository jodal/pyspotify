from __future__ import unicode_literals

import spotify
from spotify import ffi, lib, utils


__all__ = [
    'User',
]


class User(object):
    """A Spotify user.

    You can get users from the session, or you can create a :class:`User`
    yourself from a Spotify URI::

        >>> user = spotify.User('spotify:user:jodal')
        >>> user.load().display_name
        u'jodal'
    """

    def __init__(self, uri=None, sp_user=None):
        assert uri or sp_user, 'uri or sp_user is required'
        if uri is not None:
            link = spotify.Link(uri)
            sp_user = lib.sp_link_as_user(link._sp_link)
            if sp_user is ffi.NULL:
                raise ValueError(
                    'Failed to get user from Spotify URI: %r' % uri)
        lib.sp_user_add_ref(sp_user)
        self._sp_user = ffi.gc(sp_user, lib.sp_user_release)

    @property
    def canonical_name(self):
        """The user's canonical username."""
        return utils.to_unicode(lib.sp_user_canonical_name(self._sp_user))

    @property
    def display_name(self):
        """The user's displayable username."""
        return utils.to_unicode(lib.sp_user_display_name(self._sp_user))

    @property
    def is_loaded(self):
        """Whether the user's data is loaded yet."""
        return bool(lib.sp_user_is_loaded(self._sp_user))

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
        return spotify.Link(self)

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
