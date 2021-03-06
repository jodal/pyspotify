from __future__ import unicode_literals

import unittest

import spotify
import tests
from tests import mock


@mock.patch("spotify.connection.lib", spec=spotify.lib)
@mock.patch("spotify.session.lib", spec=spotify.lib)
class ConnectionTest(unittest.TestCase):
    def tearDown(self):
        spotify._session_instance = None

    def test_connection_state(self, session_lib_mock, lib_mock):
        lib_mock.sp_session_connectionstate.return_value = int(
            spotify.ConnectionState.LOGGED_OUT
        )
        session = tests.create_real_session(session_lib_mock)

        self.assertIs(session.connection.state, spotify.ConnectionState.LOGGED_OUT)

        lib_mock.sp_session_connectionstate.assert_called_once_with(session._sp_session)

    def test_connection_type_defaults_to_unknown(self, session_lib_mock, lib_mock):
        lib_mock.sp_session_set_connection_type.return_value = spotify.ErrorType.OK
        session = tests.create_real_session(session_lib_mock)

        result = session.connection.type

        self.assertIs(result, spotify.ConnectionType.UNKNOWN)
        self.assertEqual(lib_mock.sp_session_set_connection_type.call_count, 0)

    def test_set_connection_type(self, session_lib_mock, lib_mock):
        lib_mock.sp_session_set_connection_type.return_value = spotify.ErrorType.OK
        session = tests.create_real_session(session_lib_mock)

        session.connection.type = spotify.ConnectionType.MOBILE_ROAMING

        lib_mock.sp_session_set_connection_type.assert_called_with(
            session._sp_session, spotify.ConnectionType.MOBILE_ROAMING
        )

        result = session.connection.type

        self.assertIs(result, spotify.ConnectionType.MOBILE_ROAMING)

    def test_set_connection_type_fail_raises_error(self, session_lib_mock, lib_mock):
        lib_mock.sp_session_set_connection_type.return_value = (
            spotify.ErrorType.BAD_API_VERSION
        )
        session = tests.create_real_session(session_lib_mock)

        with self.assertRaises(spotify.Error):
            session.connection.type = spotify.ConnectionType.MOBILE_ROAMING

        result = session.connection.type

        self.assertIs(result, spotify.ConnectionType.UNKNOWN)

    def test_allow_network_defaults_to_true(self, session_lib_mock, lib_mock):
        session = tests.create_real_session(session_lib_mock)

        self.assertTrue(session.connection.allow_network)

    def test_set_allow_network(self, session_lib_mock, lib_mock):
        lib_mock.sp_session_set_connection_rules.return_value = spotify.ErrorType.OK
        session = tests.create_real_session(session_lib_mock)

        session.connection.allow_network = False

        self.assertFalse(session.connection.allow_network)
        lib_mock.sp_session_set_connection_rules.assert_called_with(
            session._sp_session,
            int(spotify.ConnectionRule.ALLOW_SYNC_OVER_WIFI),
        )

    def test_allow_network_if_roaming_defaults_to_false(
        self, session_lib_mock, lib_mock
    ):
        session = tests.create_real_session(session_lib_mock)

        self.assertFalse(session.connection.allow_network_if_roaming)

    def test_set_allow_network_if_roaming(self, session_lib_mock, lib_mock):
        lib_mock.sp_session_set_connection_rules.return_value = spotify.ErrorType.OK
        session = tests.create_real_session(session_lib_mock)

        session.connection.allow_network_if_roaming = True

        self.assertTrue(session.connection.allow_network_if_roaming)
        lib_mock.sp_session_set_connection_rules.assert_called_with(
            session._sp_session,
            spotify.ConnectionRule.NETWORK
            | spotify.ConnectionRule.NETWORK_IF_ROAMING
            | spotify.ConnectionRule.ALLOW_SYNC_OVER_WIFI,
        )

    def test_allow_sync_over_wifi_defaults_to_true(self, session_lib_mock, lib_mock):
        session = tests.create_real_session(session_lib_mock)

        self.assertTrue(session.connection.allow_sync_over_wifi)

    def test_set_allow_sync_over_wifi(self, session_lib_mock, lib_mock):
        lib_mock.sp_session_set_connection_rules.return_value = spotify.ErrorType.OK
        session = tests.create_real_session(session_lib_mock)

        session.connection.allow_sync_over_wifi = False

        self.assertFalse(session.connection.allow_sync_over_wifi)
        lib_mock.sp_session_set_connection_rules.assert_called_with(
            session._sp_session, int(spotify.ConnectionRule.NETWORK)
        )

    def test_allow_sync_over_mobile_defaults_to_false(self, session_lib_mock, lib_mock):
        session = tests.create_real_session(session_lib_mock)

        self.assertFalse(session.connection.allow_sync_over_mobile)

    def test_set_allow_sync_over_mobile(self, session_lib_mock, lib_mock):
        lib_mock.sp_session_set_connection_rules.return_value = spotify.ErrorType.OK
        session = tests.create_real_session(session_lib_mock)

        session.connection.allow_sync_over_mobile = True

        self.assertTrue(session.connection.allow_sync_over_mobile)
        lib_mock.sp_session_set_connection_rules.assert_called_with(
            session._sp_session,
            spotify.ConnectionRule.NETWORK
            | spotify.ConnectionRule.ALLOW_SYNC_OVER_WIFI
            | spotify.ConnectionRule.ALLOW_SYNC_OVER_MOBILE,
        )

    def test_set_connection_rules_without_rules(self, session_lib_mock, lib_mock):
        lib_mock.sp_session_set_connection_rules.return_value = spotify.ErrorType.OK
        session = tests.create_real_session(session_lib_mock)

        session.connection.allow_network = False
        session.connection.allow_sync_over_wifi = False

        lib_mock.sp_session_set_connection_rules.assert_called_with(
            session._sp_session, 0
        )

    def test_set_connection_rules_fail_raises_error(self, session_lib_mock, lib_mock):
        lib_mock.sp_session_set_connection_rules.return_value = (
            spotify.ErrorType.BAD_API_VERSION
        )
        session = tests.create_real_session(session_lib_mock)

        with self.assertRaises(spotify.Error):
            session.connection.allow_network = False


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
