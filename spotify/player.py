from __future__ import unicode_literals

import spotify
from spotify import lib


class Player(object):
    """Playback controller.

    You'll never need to create an instance of this class yourself. You'll find
    it ready to use as the :attr:`~Session.player` attribute on the
    :class:`Session` instance.
    """

    def __init__(self, session):
        self._session = session

    def load(self, track):
        """Load :class:`Track` for playback."""
        spotify.Error.maybe_raise(lib.sp_session_player_load(
            self._session._sp_session, track._sp_track))

    def seek(self, offset):
        """Seek to the offset in ms in the currently loaded track."""
        spotify.Error.maybe_raise(
            lib.sp_session_player_seek(self._session._sp_session, offset))

    def play(self, play=True):
        """Play the currently loaded track.

        This will cause audio data to be passed to the
        :attr:`~SessionCallbacks.music_delivery` callback.

        If ``play`` is set to :class:`False`, playback will be paused.
        """
        spotify.Error.maybe_raise(lib.sp_session_player_play(
            self._session._sp_session, play))

    def pause(self):
        """Pause the currently loaded track.

        This is the same as calling :meth:`play` with :class:`False`.
        """
        self.play(False)

    def unload(self):
        """Stops the currently playing track."""
        spotify.Error.maybe_raise(
            lib.sp_session_player_unload(self._session._sp_session))

    def prefetch(self, track):
        """Prefetch a :class:`Track` for playback.

        This can be used to make libspotify download and cache a track before
        playing it.
        """
        spotify.Error.maybe_raise(lib.sp_session_player_prefetch(
            self._session._sp_session, track._sp_track))
