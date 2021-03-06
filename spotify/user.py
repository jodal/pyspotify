from __future__ import unicode_literals

import spotify
from spotify import ffi, lib, serialized, utils

__all__ = ["User"]


class User(object):

    """A Spotify user.

    You can get users from the session, or you can create a :class:`User`
    yourself from a Spotify URI::

        >>> session = spotify.Session()
        # ...
        >>> user = session.get_user('spotify:user:jodal')
        >>> user.load().display_name
        u'jodal'
    """

    def __init__(self, session, uri=None, sp_user=None, add_ref=True):
        assert uri or sp_user, "uri or sp_user is required"

        self._session = session

        if uri is not None:
            user = spotify.Link(self._session, uri=uri).as_user()
            if user is None:
                raise ValueError("Failed to get user from Spotify URI: %r" % uri)
            sp_user = user._sp_user
            add_ref = True

        if add_ref:
            lib.sp_user_add_ref(sp_user)
        self._sp_user = ffi.gc(sp_user, lib.sp_user_release)

    def __repr__(self):
        return "User(%r)" % self.link.uri

    @property
    @serialized
    def canonical_name(self):
        """The user's canonical username."""
        return utils.to_unicode(lib.sp_user_canonical_name(self._sp_user))

    @property
    @serialized
    def display_name(self):
        """The user's displayable username."""
        return utils.to_unicode(lib.sp_user_display_name(self._sp_user))

    @property
    def is_loaded(self):
        """Whether the user's data is loaded yet."""
        return bool(lib.sp_user_is_loaded(self._sp_user))

    def load(self, timeout=None):
        """Block until the user's data is loaded.

        After ``timeout`` seconds with no results :exc:`~spotify.Timeout` is
        raised. If ``timeout`` is :class:`None` the default timeout is used.

        The method returns ``self`` to allow for chaining of calls.
        """
        return utils.load(self._session, self, timeout=timeout)

    @property
    def link(self):
        """A :class:`Link` to the user."""
        return spotify.Link(
            self._session,
            sp_link=lib.sp_link_create_from_user(self._sp_user),
            add_ref=False,
        )

    @property
    def starred(self):
        """The :class:`Playlist` of tracks starred by the user."""
        return self._session.get_starred(self.canonical_name)

    @property
    def published_playlists(self):
        """The :class:`PlaylistContainer` of playlists published by the
        user."""
        return self._session.get_published_playlists(self.canonical_name)
