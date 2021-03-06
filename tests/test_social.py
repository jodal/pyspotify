from __future__ import unicode_literals

import unittest

import spotify
import tests
from tests import mock


@mock.patch("spotify.social.lib", spec=spotify.lib)
@mock.patch("spotify.session.lib", spec=spotify.lib)
class SocialTest(unittest.TestCase):
    def tearDown(self):
        spotify._session_instance = None

    def test_is_private_session(self, session_lib_mock, lib_mock):
        lib_mock.sp_session_is_private_session.return_value = 0
        session = tests.create_real_session(session_lib_mock)

        result = session.social.private_session

        lib_mock.sp_session_is_private_session.assert_called_with(session._sp_session)
        self.assertFalse(result)

    @mock.patch("spotify.connection.lib", spec=spotify.lib)
    def test_set_private_session(self, conn_lib_mock, session_lib_mock, lib_mock):
        lib_mock.sp_session_set_private_session.return_value = spotify.ErrorType.OK
        session = tests.create_real_session(session_lib_mock)

        session.social.private_session = True

        lib_mock.sp_session_set_private_session.assert_called_with(
            session._sp_session, 1
        )

    @mock.patch("spotify.connection.lib", spec=spotify.lib)
    def test_set_private_session_fail_raises_error(
        self, conn_lib_mock, session_lib_mock, lib_mock
    ):
        lib_mock.sp_session_set_private_session.return_value = (
            spotify.ErrorType.BAD_API_VERSION
        )
        session = tests.create_real_session(session_lib_mock)

        with self.assertRaises(spotify.Error):
            session.social.private_session = True

    def test_is_scrobbling(self, session_lib_mock, lib_mock):
        def func(sp_session_ptr, sp_social_provider, sp_scrobbling_state_ptr):
            sp_scrobbling_state_ptr[0] = spotify.ScrobblingState.USE_GLOBAL_SETTING
            return spotify.ErrorType.OK

        lib_mock.sp_session_is_scrobbling.side_effect = func
        session = tests.create_real_session(session_lib_mock)

        result = session.social.is_scrobbling(spotify.SocialProvider.SPOTIFY)

        lib_mock.sp_session_is_scrobbling.assert_called_with(
            session._sp_session, spotify.SocialProvider.SPOTIFY, mock.ANY
        )
        self.assertIs(result, spotify.ScrobblingState.USE_GLOBAL_SETTING)

    def test_is_scrobbling_fail_raises_error(self, session_lib_mock, lib_mock):
        lib_mock.sp_session_is_scrobbling.return_value = (
            spotify.ErrorType.BAD_API_VERSION
        )
        session = tests.create_real_session(session_lib_mock)

        with self.assertRaises(spotify.Error):
            session.social.is_scrobbling(spotify.SocialProvider.SPOTIFY)

    def test_set_scrobbling(self, session_lib_mock, lib_mock):
        lib_mock.sp_session_set_scrobbling.return_value = spotify.ErrorType.OK
        session = tests.create_real_session(session_lib_mock)

        session.social.set_scrobbling(
            spotify.SocialProvider.SPOTIFY,
            spotify.ScrobblingState.USE_GLOBAL_SETTING,
        )

        lib_mock.sp_session_set_scrobbling.assert_called_with(
            session._sp_session,
            spotify.SocialProvider.SPOTIFY,
            spotify.ScrobblingState.USE_GLOBAL_SETTING,
        )

    def test_set_scrobbling_fail_raises_error(self, session_lib_mock, lib_mock):
        lib_mock.sp_session_set_scrobbling.return_value = (
            spotify.ErrorType.BAD_API_VERSION
        )
        session = tests.create_real_session(session_lib_mock)

        with self.assertRaises(spotify.Error):
            session.social.set_scrobbling(
                spotify.SocialProvider.SPOTIFY,
                spotify.ScrobblingState.USE_GLOBAL_SETTING,
            )

    def test_is_scrobbling_possible(self, session_lib_mock, lib_mock):
        def func(sp_session_ptr, sp_social_provider, out_ptr):
            out_ptr[0] = 1
            return spotify.ErrorType.OK

        lib_mock.sp_session_is_scrobbling_possible.side_effect = func
        session = tests.create_real_session(session_lib_mock)

        result = session.social.is_scrobbling_possible(spotify.SocialProvider.FACEBOOK)

        lib_mock.sp_session_is_scrobbling_possible.assert_called_with(
            session._sp_session, spotify.SocialProvider.FACEBOOK, mock.ANY
        )
        self.assertTrue(result)

    def test_is_scrobbling_possible_fail_raises_error(self, session_lib_mock, lib_mock):
        lib_mock.sp_session_is_scrobbling_possible.return_value = (
            spotify.ErrorType.BAD_API_VERSION
        )
        session = tests.create_real_session(session_lib_mock)

        with self.assertRaises(spotify.Error):
            session.social.is_scrobbling_possible(spotify.SocialProvider.FACEBOOK)

    def test_set_social_credentials(self, session_lib_mock, lib_mock):
        lib_mock.sp_session_set_social_credentials.return_value = spotify.ErrorType.OK
        session = tests.create_real_session(session_lib_mock)

        session.social.set_social_credentials(
            spotify.SocialProvider.LASTFM, "alice", "secret"
        )

        lib_mock.sp_session_set_social_credentials.assert_called_once_with(
            session._sp_session,
            spotify.SocialProvider.LASTFM,
            mock.ANY,
            mock.ANY,
        )
        self.assertEqual(
            spotify.ffi.string(
                lib_mock.sp_session_set_social_credentials.call_args[0][2]
            ),
            b"alice",
        )
        self.assertEqual(
            spotify.ffi.string(
                lib_mock.sp_session_set_social_credentials.call_args[0][3]
            ),
            b"secret",
        )

    def test_set_social_credentials_fail_raises_error(self, session_lib_mock, lib_mock):
        lib_mock.sp_session_login.return_value = spotify.ErrorType.BAD_API_VERSION
        session = tests.create_real_session(session_lib_mock)

        with self.assertRaises(spotify.Error):
            session.social.set_social_credentials(
                spotify.SocialProvider.LASTFM, "alice", "secret"
            )


class ScrobblingStateTest(unittest.TestCase):
    def test_has_constants(self):
        self.assertEqual(spotify.ScrobblingState.USE_GLOBAL_SETTING, 0)
        self.assertEqual(spotify.ScrobblingState.LOCAL_ENABLED, 1)


class SocialProviderTest(unittest.TestCase):
    def test_has_constants(self):
        self.assertEqual(spotify.SocialProvider.SPOTIFY, 0)
        self.assertEqual(spotify.SocialProvider.FACEBOOK, 1)
