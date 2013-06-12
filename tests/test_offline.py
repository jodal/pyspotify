from __future__ import unicode_literals

import unittest

import spotify


class OfflineSyncStatusTest(unittest.TestCase):

    def setUp(self):
        self._sp_offline_sync_status = spotify.ffi.new(
            'sp_offline_sync_status *')
        self._sp_offline_sync_status.queued_tracks = 5
        self._sp_offline_sync_status.done_tracks = 16
        self._sp_offline_sync_status.copied_tracks = 27
        self._sp_offline_sync_status.willnotcopy_tracks = 2
        self._sp_offline_sync_status.error_tracks = 3
        self._sp_offline_sync_status.syncing = True

        self.offline_sync_status = spotify.OfflineSyncStatus(
            self._sp_offline_sync_status)

    def test_queued_tracks(self):
        self.assertEqual(self.offline_sync_status.queued_tracks, 5)

    def test_done_tracks(self):
        self.assertEqual(self.offline_sync_status.done_tracks, 16)

    def test_copied_tracks(self):
        self.assertEqual(self.offline_sync_status.copied_tracks, 27)

    def test_willnotcopy_tracks(self):
        self.assertEqual(self.offline_sync_status.willnotcopy_tracks, 2)

    def test_error_tracks(self):
        self.assertEqual(self.offline_sync_status.error_tracks, 3)

    def test_syncing(self):
        self.assertTrue(self.offline_sync_status.syncing)
