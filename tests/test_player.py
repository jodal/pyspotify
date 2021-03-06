from __future__ import unicode_literals

import unittest

import spotify
import tests
from tests import mock


@mock.patch("spotify.player.lib", spec=spotify.lib)
@mock.patch("spotify.session.lib", spec=spotify.lib)
class PlayerTest(unittest.TestCase):
    def tearDown(self):
        spotify._session_instance = None

    def test_player_state_is_unloaded_initially(self, session_lib_mock, lib_mock):
        session = tests.create_real_session(session_lib_mock)

        self.assertEqual(session.player.state, spotify.PlayerState.UNLOADED)

    @mock.patch("spotify.track.lib", spec=spotify.lib)
    def test_player_load(self, track_lib_mock, session_lib_mock, lib_mock):
        lib_mock.sp_session_player_load.return_value = spotify.ErrorType.OK
        session = tests.create_real_session(session_lib_mock)
        sp_track = spotify.ffi.cast("sp_track *", 42)
        track = spotify.Track(session, sp_track=sp_track)

        session.player.load(track)

        lib_mock.sp_session_player_load.assert_called_once_with(
            session._sp_session, sp_track
        )
        self.assertEqual(session.player.state, spotify.PlayerState.LOADED)

    @mock.patch("spotify.track.lib", spec=spotify.lib)
    def test_player_load_fail_raises_error(
        self, track_lib_mock, session_lib_mock, lib_mock
    ):
        lib_mock.sp_session_player_load.return_value = (
            spotify.ErrorType.TRACK_NOT_PLAYABLE
        )
        session = tests.create_real_session(session_lib_mock)
        player_state = session.player.state
        sp_track = spotify.ffi.cast("sp_track *", 42)
        track = spotify.Track(session, sp_track=sp_track)

        with self.assertRaises(spotify.Error):
            session.player.load(track)
        self.assertEqual(session.player.state, player_state)

    def test_player_seek(self, session_lib_mock, lib_mock):
        lib_mock.sp_session_player_seek.return_value = spotify.ErrorType.OK
        session = tests.create_real_session(session_lib_mock)
        player_state = session.player.state

        session.player.seek(45000)

        lib_mock.sp_session_player_seek.assert_called_once_with(
            session._sp_session, 45000
        )
        self.assertEqual(session.player.state, player_state)

    def test_player_seek_fail_raises_error(self, session_lib_mock, lib_mock):
        lib_mock.sp_session_player_seek.return_value = spotify.ErrorType.BAD_API_VERSION
        session = tests.create_real_session(session_lib_mock)
        player_state = session.player.state

        with self.assertRaises(spotify.Error):
            session.player.seek(45000)
        self.assertEqual(session.player.state, player_state)

    def test_player_play(self, session_lib_mock, lib_mock):
        lib_mock.sp_session_player_play.return_value = spotify.ErrorType.OK
        session = tests.create_real_session(session_lib_mock)

        session.player.play(True)

        lib_mock.sp_session_player_play.assert_called_once_with(session._sp_session, 1)
        self.assertEqual(session.player.state, spotify.PlayerState.PLAYING)

    def test_player_play_with_false_to_pause(self, session_lib_mock, lib_mock):
        lib_mock.sp_session_player_play.return_value = spotify.ErrorType.OK
        session = tests.create_real_session(session_lib_mock)

        session.player.play(False)

        lib_mock.sp_session_player_play.assert_called_once_with(session._sp_session, 0)
        self.assertEqual(session.player.state, spotify.PlayerState.PAUSED)

    def test_player_play_fail_raises_error(self, session_lib_mock, lib_mock):
        lib_mock.sp_session_player_play.return_value = spotify.ErrorType.BAD_API_VERSION
        session = tests.create_real_session(session_lib_mock)
        player_state = session.player.state

        with self.assertRaises(spotify.Error):
            session.player.play(True)
        self.assertEqual(session.player.state, player_state)

    def test_player_pause(self, session_lib_mock, lib_mock):
        lib_mock.sp_session_player_play.return_value = spotify.ErrorType.OK
        session = tests.create_real_session(session_lib_mock)

        session.player.pause()

        lib_mock.sp_session_player_play.assert_called_once_with(session._sp_session, 0)
        self.assertEqual(session.player.state, spotify.PlayerState.PAUSED)

    def test_player_unload(self, session_lib_mock, lib_mock):
        lib_mock.sp_session_player_unload.return_value = spotify.ErrorType.OK
        session = tests.create_real_session(session_lib_mock)

        session.player.unload()

        lib_mock.sp_session_player_unload.assert_called_once_with(session._sp_session)
        self.assertEqual(session.player.state, spotify.PlayerState.UNLOADED)

    def test_player_unload_fail_raises_error(self, session_lib_mock, lib_mock):
        lib_mock.sp_session_player_unload.return_value = (
            spotify.ErrorType.BAD_API_VERSION
        )
        session = tests.create_real_session(session_lib_mock)
        player_state = session.player.state

        with self.assertRaises(spotify.Error):
            session.player.unload()
        self.assertEqual(session.player.state, player_state)

    @mock.patch("spotify.track.lib", spec=spotify.lib)
    def test_player_prefetch(self, track_lib_mock, session_lib_mock, lib_mock):
        lib_mock.sp_session_player_prefetch.return_value = spotify.ErrorType.OK
        session = tests.create_real_session(session_lib_mock)
        sp_track = spotify.ffi.cast("sp_track *", 42)
        track = spotify.Track(session, sp_track=sp_track)

        session.player.prefetch(track)

        lib_mock.sp_session_player_prefetch.assert_called_once_with(
            session._sp_session, sp_track
        )

    @mock.patch("spotify.track.lib", spec=spotify.lib)
    def test_player_prefetch_fail_raises_error(
        self, track_lib_mock, session_lib_mock, lib_mock
    ):
        lib_mock.sp_session_player_prefetch.return_value = spotify.ErrorType.NO_CACHE
        session = tests.create_real_session(session_lib_mock)
        sp_track = spotify.ffi.cast("sp_track *", 42)
        track = spotify.Track(session, sp_track=sp_track)

        with self.assertRaises(spotify.Error):
            session.player.prefetch(track)
