from __future__ import unicode_literals

import spotify
from spotify import ffi, lib

__all__ = ["OfflineSyncStatus"]


class Offline(object):

    """Offline sync controller.

    You'll never need to create an instance of this class yourself. You'll find
    it ready to use as the :attr:`~Session.offline` attribute on the
    :class:`Session` instance.
    """

    def __init__(self, session):
        self._session = session

    @property
    def tracks_to_sync(self):
        """Total number of tracks that needs download before everything from
        all playlists that are marked for offline is fully synchronized.
        """
        return lib.sp_offline_tracks_to_sync(self._session._sp_session)

    @property
    def num_playlists(self):
        """Number of playlists that are marked for offline synchronization."""
        return lib.sp_offline_num_playlists(self._session._sp_session)

    @property
    def sync_status(self):
        """The :class:`OfflineSyncStatus` or :class:`None` if not syncing.

        The :attr:`~SessionEvent.OFFLINE_STATUS_UPDATED` event is emitted on
        the session object when this is updated.
        """
        sp_offline_sync_status = ffi.new("sp_offline_sync_status *")
        syncing = lib.sp_offline_sync_get_status(
            self._session._sp_session, sp_offline_sync_status
        )
        if syncing:
            return spotify.OfflineSyncStatus(sp_offline_sync_status)

    @property
    def time_left(self):
        """The number of seconds until the user has to get online and
        relogin."""
        return lib.sp_offline_time_left(self._session._sp_session)


class OfflineSyncStatus(object):

    """A Spotify offline sync status object.

    You'll never need to create an instance of this class yourself. You'll find
    it ready for use as the :attr:`~spotify.Offline.sync_status` attribute on
    the :attr:`~spotify.Session.offline` attribute on the
    :class:`~spotify.Session` instance.
    """

    def __init__(self, sp_offline_sync_status):
        self._sp_offline_sync_status = sp_offline_sync_status

    @property
    def queued_tracks(self):
        """Number of tracks left to sync in current sync operation."""
        return self._sp_offline_sync_status.queued_tracks

    @property
    def done_tracks(self):
        """Number of tracks marked for sync that existed on the device before
        the current sync operation."""
        return self._sp_offline_sync_status.done_tracks

    @property
    def copied_tracks(self):
        """Number of tracks copied during the current sync operation."""
        return self._sp_offline_sync_status.copied_tracks

    @property
    def willnotcopy_tracks(self):
        """Number of tracks marked for sync that will not be copied."""
        return self._sp_offline_sync_status.willnotcopy_tracks

    @property
    def error_tracks(self):
        """Number of tracks that failed syncing during the current sync
        operation."""
        return self._sp_offline_sync_status.error_tracks

    @property
    def syncing(self):
        """If sync operation is in progress."""
        return bool(self._sp_offline_sync_status.syncing)
