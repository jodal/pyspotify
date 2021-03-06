# encoding: utf-8

from __future__ import unicode_literals

import unittest

import spotify
import tests
from tests import mock


@mock.patch("spotify.inbox.lib", spec=spotify.lib)
class InboxPostResultTest(unittest.TestCase):
    def setUp(self):
        self.session = tests.create_session_mock()
        spotify._session_instance = self.session

    def tearDown(self):
        spotify._session_instance = None

    def test_create_without_user_and_tracks_or_sp_inbox_fails(self, lib_mock):
        with self.assertRaises(AssertionError):
            spotify.InboxPostResult(self.session)

    def test_adds_ref_to_sp_inbox_when_created(self, lib_mock):
        sp_inbox = spotify.ffi.cast("sp_inbox *", 42)

        spotify.InboxPostResult(self.session, sp_inbox=sp_inbox)

        lib_mock.sp_inbox_add_ref.assert_called_with(sp_inbox)

    def test_releases_sp_inbox_when_result_dies(self, lib_mock):
        sp_inbox = spotify.ffi.cast("sp_inbox *", 42)

        inbox_post_result = spotify.InboxPostResult(self.session, sp_inbox=sp_inbox)
        inbox_post_result = None  # noqa
        tests.gc_collect()

        lib_mock.sp_inbox_release.assert_called_with(sp_inbox)

    @mock.patch("spotify.track.lib", spec=spotify.lib)
    def test_inbox_post_tracks(self, track_lib_mock, lib_mock):
        sp_track1 = spotify.ffi.cast("sp_track *", 43)
        track1 = spotify.Track(self.session, sp_track=sp_track1)
        sp_track2 = spotify.ffi.cast("sp_track *", 44)
        track2 = spotify.Track(self.session, sp_track=sp_track2)
        sp_inbox = spotify.ffi.cast("sp_inbox *", 42)
        lib_mock.sp_inbox_post_tracks.return_value = sp_inbox

        result = spotify.InboxPostResult(self.session, "alice", [track1, track2], "♥")

        lib_mock.sp_inbox_post_tracks.assert_called_with(
            self.session._sp_session,
            mock.ANY,
            mock.ANY,
            2,
            mock.ANY,
            mock.ANY,
            mock.ANY,
        )
        self.assertEqual(
            spotify.ffi.string(lib_mock.sp_inbox_post_tracks.call_args[0][1]),
            b"alice",
        )
        self.assertIn(sp_track1, lib_mock.sp_inbox_post_tracks.call_args[0][2])
        self.assertIn(sp_track2, lib_mock.sp_inbox_post_tracks.call_args[0][2])
        self.assertEqual(
            spotify.ffi.string(lib_mock.sp_inbox_post_tracks.call_args[0][4]),
            b"\xe2\x99\xa5",
        )
        self.assertIsInstance(result, spotify.InboxPostResult)
        self.assertEqual(result._sp_inbox, sp_inbox)

        self.assertFalse(result.loaded_event.is_set())
        inboxpost_complete_cb = lib_mock.sp_inbox_post_tracks.call_args[0][5]
        userdata = lib_mock.sp_inbox_post_tracks.call_args[0][6]
        inboxpost_complete_cb(sp_inbox, userdata)
        self.assertTrue(result.loaded_event.wait(3))

    @mock.patch("spotify.track.lib", spec=spotify.lib)
    def test_inbox_post_with_single_track(self, track_lib_mock, lib_mock):
        sp_track1 = spotify.ffi.cast("sp_track *", 43)
        track1 = spotify.Track(self.session, sp_track=sp_track1)
        sp_inbox = spotify.ffi.cast("sp_inbox *", 42)
        lib_mock.sp_inbox_post_tracks.return_value = sp_inbox

        result = spotify.InboxPostResult(self.session, "alice", track1, "Enjoy!")

        lib_mock.sp_inbox_post_tracks.assert_called_with(
            self.session._sp_session,
            mock.ANY,
            mock.ANY,
            1,
            mock.ANY,
            mock.ANY,
            mock.ANY,
        )
        self.assertIn(sp_track1, lib_mock.sp_inbox_post_tracks.call_args[0][2])
        self.assertIsInstance(result, spotify.InboxPostResult)
        self.assertEqual(result._sp_inbox, sp_inbox)

    @mock.patch("spotify.track.lib", spec=spotify.lib)
    def test_inbox_post_with_callback(self, track_lib_mock, lib_mock):
        sp_track1 = spotify.ffi.cast("sp_track *", 43)
        track1 = spotify.Track(self.session, sp_track=sp_track1)
        sp_track2 = spotify.ffi.cast("sp_track *", 44)
        track2 = spotify.Track(self.session, sp_track=sp_track2)
        sp_inbox = spotify.ffi.cast("sp_inbox *", 42)
        lib_mock.sp_inbox_post_tracks.return_value = sp_inbox
        callback = mock.Mock()

        result = spotify.InboxPostResult(
            self.session, "alice", [track1, track2], callback=callback
        )

        inboxpost_complete_cb = lib_mock.sp_inbox_post_tracks.call_args[0][5]
        userdata = lib_mock.sp_inbox_post_tracks.call_args[0][6]
        inboxpost_complete_cb(sp_inbox, userdata)

        result.loaded_event.wait(3)
        callback.assert_called_with(result)

    @mock.patch("spotify.track.lib", spec=spotify.lib)
    def test_inbox_post_where_result_is_gone_before_callback_is_called(
        self, track_lib_mock, lib_mock
    ):

        sp_track1 = spotify.ffi.cast("sp_track *", 43)
        track1 = spotify.Track(self.session, sp_track=sp_track1)
        sp_track2 = spotify.ffi.cast("sp_track *", 44)
        track2 = spotify.Track(self.session, sp_track=sp_track2)
        sp_inbox = spotify.ffi.cast("sp_inbox *", 42)
        lib_mock.sp_inbox_post_tracks.return_value = sp_inbox
        callback = mock.Mock()

        result = spotify.InboxPostResult(
            self.session, "alice", [track1, track2], callback=callback
        )
        loaded_event = result.loaded_event
        result = None  # noqa
        tests.gc_collect()

        # The mock keeps the handle/userdata alive, thus this test doesn't
        # really test that session._callback_handles keeps the handle alive.
        inboxpost_complete_cb = lib_mock.sp_inbox_post_tracks.call_args[0][5]
        userdata = lib_mock.sp_inbox_post_tracks.call_args[0][6]
        inboxpost_complete_cb(sp_inbox, userdata)

        loaded_event.wait(3)
        self.assertEqual(callback.call_count, 1)
        self.assertEqual(callback.call_args[0][0]._sp_inbox, sp_inbox)

    @mock.patch("spotify.track.lib", spec=spotify.lib)
    def test_fail_to_init_raises_error(self, track_lib_mock, lib_mock):
        sp_track1 = spotify.ffi.cast("sp_track *", 43)
        track1 = spotify.Track(self.session, sp_track=sp_track1)
        sp_track2 = spotify.ffi.cast("sp_track *", 44)
        track2 = spotify.Track(self.session, sp_track=sp_track2)
        lib_mock.sp_inbox_post_tracks.return_value = spotify.ffi.NULL

        with self.assertRaises(spotify.Error):
            spotify.InboxPostResult(self.session, "alice", [track1, track2], "Enjoy!")

    def test_repr(self, lib_mock):
        sp_inbox = spotify.ffi.cast("sp_inbox *", 42)
        inbox_post_result = spotify.InboxPostResult(self.session, sp_inbox=sp_inbox)

        self.assertEqual(repr(inbox_post_result), "InboxPostResult(<pending>)")

        inbox_post_result.loaded_event.set()
        lib_mock.sp_inbox_error.return_value = int(spotify.ErrorType.INBOX_IS_FULL)

        self.assertEqual(repr(inbox_post_result), "InboxPostResult(INBOX_IS_FULL)")

        lib_mock.sp_inbox_error.return_value = int(spotify.ErrorType.OK)

        self.assertEqual(repr(inbox_post_result), "InboxPostResult(OK)")

    def test_eq(self, lib_mock):
        sp_inbox = spotify.ffi.cast("sp_inbox *", 42)
        inbox1 = spotify.InboxPostResult(self.session, sp_inbox=sp_inbox)
        inbox2 = spotify.InboxPostResult(self.session, sp_inbox=sp_inbox)

        self.assertTrue(inbox1 == inbox2)
        self.assertFalse(inbox1 == "foo")

    def test_ne(self, lib_mock):
        sp_inbox = spotify.ffi.cast("sp_inbox *", 42)
        inbox1 = spotify.InboxPostResult(self.session, sp_inbox=sp_inbox)
        inbox2 = spotify.InboxPostResult(self.session, sp_inbox=sp_inbox)

        self.assertFalse(inbox1 != inbox2)

    def test_hash(self, lib_mock):
        sp_inbox = spotify.ffi.cast("sp_inbox *", 42)
        inbox1 = spotify.InboxPostResult(self.session, sp_inbox=sp_inbox)
        inbox2 = spotify.InboxPostResult(self.session, sp_inbox=sp_inbox)

        self.assertEqual(hash(inbox1), hash(inbox2))

    def test_error(self, lib_mock):
        lib_mock.sp_inbox_error.return_value = int(spotify.ErrorType.INBOX_IS_FULL)
        sp_inbox = spotify.ffi.cast("sp_inbox *", 42)
        inbox_post_result = spotify.InboxPostResult(self.session, sp_inbox=sp_inbox)

        result = inbox_post_result.error

        lib_mock.sp_inbox_error.assert_called_once_with(sp_inbox)
        self.assertIs(result, spotify.ErrorType.INBOX_IS_FULL)
