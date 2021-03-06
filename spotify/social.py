from __future__ import unicode_literals

import spotify
from spotify import ffi, lib, utils

__all__ = ["ScrobblingState", "SocialProvider"]


class Social(object):

    """Social sharing controller.

    You'll never need to create an instance of this class yourself. You'll find
    it ready to use as the :attr:`~Session.social` attribute on the
    :class:`Session` instance.
    """

    def __init__(self, session):
        self._session = session

    @property
    def private_session(self):
        """Whether the session is private.

        Set to :class:`True` or :class:`False` to change.
        """
        return bool(lib.sp_session_is_private_session(self._session._sp_session))

    @private_session.setter
    def private_session(self, value):
        # XXX sp_session_set_private_session() segfaults unless we login and
        # call process_events() at least once before calling it. If we log out
        # again, calling the function still works without segfaults. This bug
        # has been reported to Spotify on IRC.
        if self._session.connection.state != spotify.ConnectionState.LOGGED_IN:
            raise RuntimeError(
                "private_session can only be set when the session is logged "
                "in. This is temporary workaround of a libspotify bug, "
                "causing the application to segfault otherwise."
            )
        spotify.Error.maybe_raise(
            lib.sp_session_set_private_session(self._session._sp_session, bool(value))
        )

    def is_scrobbling(self, social_provider):
        """Get the :class:`ScrobblingState` for the given
        ``social_provider``."""
        scrobbling_state = ffi.new("sp_scrobbling_state *")
        spotify.Error.maybe_raise(
            lib.sp_session_is_scrobbling(
                self._session._sp_session, social_provider, scrobbling_state
            )
        )
        return spotify.ScrobblingState(scrobbling_state[0])

    def is_scrobbling_possible(self, social_provider):
        """Check if the scrobbling settings should be shown to the user."""
        out = ffi.new("bool *")
        spotify.Error.maybe_raise(
            lib.sp_session_is_scrobbling_possible(
                self._session._sp_session, social_provider, out
            )
        )
        return bool(out[0])

    def set_scrobbling(self, social_provider, scrobbling_state):
        """Set the ``scrobbling_state`` for the given ``social_provider``."""
        spotify.Error.maybe_raise(
            lib.sp_session_set_scrobbling(
                self._session._sp_session, social_provider, scrobbling_state
            )
        )

    def set_social_credentials(self, social_provider, username, password):
        """Set the user's credentials with a social provider.

        Currently this is only relevant for Last.fm. Call
        :meth:`set_scrobbling` to force an authentication attempt with the
        provider. If authentication fails a
        :attr:`~SessionEvent.SCROBBLE_ERROR` event will be emitted on the
        :class:`Session` object.
        """
        spotify.Error.maybe_raise(
            lib.sp_session_set_social_credentials(
                self._session._sp_session,
                social_provider,
                utils.to_char(username),
                utils.to_char(password),
            )
        )


@utils.make_enum("SP_SCROBBLING_STATE_")
class ScrobblingState(utils.IntEnum):
    pass


@utils.make_enum("SP_SOCIAL_PROVIDER_")
class SocialProvider(utils.IntEnum):
    pass
