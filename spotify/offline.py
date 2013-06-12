from __future__ import unicode_literals


__all__ = [
    'OfflineSyncStatus',
]


class OfflineSyncStatus(object):
    """A Spotify offline sync status."""

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
