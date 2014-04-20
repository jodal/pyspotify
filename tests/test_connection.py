from __future__ import unicode_literals

import unittest

import spotify

import tests
from tests import mock


@mock.patch('spotify.connection.lib', spec=spotify.lib)
@mock.patch('spotify.session.lib', spec=spotify.lib)
class OfflineTest(unittest.TestCase):

    def tearDown(self):
        spotify._session_instance = None

    def test_set_connection_type(self, session_lib_mock, lib_mock):
        lib_mock.sp_session_set_connection_type.return_value = (
            spotify.ErrorType.OK)
        session = tests.create_real_session(session_lib_mock)

        session.offline.set_connection_type(
            spotify.ConnectionType.MOBILE_ROAMING)

        lib_mock.sp_session_set_connection_type.assert_called_with(
            session._sp_session, spotify.ConnectionType.MOBILE_ROAMING)

    def test_set_connection_type_fail_raises_error(
            self, session_lib_mock, lib_mock):
        lib_mock.sp_session_set_connection_type.return_value = (
            spotify.ErrorType.BAD_API_VERSION)
        session = tests.create_real_session(session_lib_mock)

        with self.assertRaises(spotify.Error):
            session.offline.set_connection_type(
                spotify.ConnectionType.UNKNOWN)

    def test_set_connection_rules(self, session_lib_mock, lib_mock):
        lib_mock.sp_session_set_connection_rules.return_value = (
            spotify.ErrorType.OK)
        session = tests.create_real_session(session_lib_mock)

        session.offline.set_connection_rules(
            spotify.ConnectionRule.NETWORK,
            spotify.ConnectionRule.ALLOW_SYNC_OVER_WIFI)

        lib_mock.sp_session_set_connection_rules.assert_called_with(
            session._sp_session,
            spotify.ConnectionRule.NETWORK |
            spotify.ConnectionRule.ALLOW_SYNC_OVER_WIFI)

    def test_set_connection_rules_without_rules(
            self, session_lib_mock, lib_mock):
        lib_mock.sp_session_set_connection_rules.return_value = (
            spotify.ErrorType.OK)
        session = tests.create_real_session(session_lib_mock)

        session.offline.set_connection_rules()

        lib_mock.sp_session_set_connection_rules.assert_called_with(
            session._sp_session, 0)

    def test_set_connection_rules_fail_raises_error(
            self, session_lib_mock, lib_mock):
        lib_mock.sp_session_set_connection_rules.return_value = (
            spotify.ErrorType.BAD_API_VERSION)
        session = tests.create_real_session(session_lib_mock)

        with self.assertRaises(spotify.Error):
            session.offline.set_connection_rules(
                spotify.ConnectionRule.NETWORK)

    def test_offline_tracks_to_sync(self, session_lib_mock, lib_mock):
        lib_mock.sp_offline_tracks_to_sync.return_value = 17
        session = tests.create_real_session(session_lib_mock)

        result = session.offline.tracks_to_sync

        lib_mock.sp_offline_tracks_to_sync.assert_called_with(
            session._sp_session)
        self.assertEqual(result, 17)

    def test_offline_num_playlists(self, session_lib_mock, lib_mock):
        lib_mock.sp_offline_num_playlists.return_value = 5
        session = tests.create_real_session(session_lib_mock)

        result = session.offline.num_playlists

        lib_mock.sp_offline_num_playlists.assert_called_with(
            session._sp_session)
        self.assertEqual(result, 5)

    def test_offline_sync_status(self, session_lib_mock, lib_mock):
        def func(sp_session_ptr, sp_offline_sync_status):
            sp_offline_sync_status.queued_tracks = 3
            return 1

        lib_mock.sp_offline_sync_get_status.side_effect = func
        session = tests.create_real_session(session_lib_mock)

        result = session.offline.sync_status

        lib_mock.sp_offline_sync_get_status.assert_called_with(
            session._sp_session, mock.ANY)
        self.assertIsInstance(result, spotify.OfflineSyncStatus)
        self.assertEqual(result.queued_tracks, 3)

    def test_offline_sync_status_when_not_syncing(
            self, session_lib_mock, lib_mock):
        lib_mock.sp_offline_sync_get_status.return_value = 0
        session = tests.create_real_session(session_lib_mock)

        result = session.offline.sync_status

        lib_mock.sp_offline_sync_get_status.assert_called_with(
            session._sp_session, mock.ANY)
        self.assertIsNone(result)

    def test_offline_time_left(self, session_lib_mock, lib_mock):
        lib_mock.sp_offline_time_left.return_value = 3600
        session = tests.create_real_session(session_lib_mock)

        result = session.offline.time_left

        lib_mock.sp_offline_time_left.assert_called_with(session._sp_session)
        self.assertEqual(result, 3600)


class ConnectionRuleTest(unittest.TestCase):

    def test_has_constants(self):
        self.assertEqual(spotify.ConnectionRule.NETWORK, 1)
        self.assertEqual(spotify.ConnectionRule.ALLOW_SYNC_OVER_WIFI, 8)


class ConnectionStateTest(unittest.TestCase):

    def test_has_constants(self):
        self.assertEqual(spotify.ConnectionState.LOGGED_OUT, 0)


class ConnectionTypeTest(unittest.TestCase):

    def test_has_constants(self):
        self.assertEqual(spotify.ConnectionType.UNKNOWN, 0)


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
