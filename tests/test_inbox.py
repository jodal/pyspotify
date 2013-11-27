# encoding: utf-8

from __future__ import unicode_literals

import mock
import unittest

import spotify
import tests


@mock.patch('spotify.inbox.lib', spec=spotify.lib)
class InboxPostResultTest(unittest.TestCase):

    def create_session(self, lib_mock):
        session = mock.sentinel.session
        session._sp_session = mock.sentinel.sp_session
        spotify.session_instance = session
        return session

    def test_create_without_user_and_tracks_or_sp_inbox_fails(self, lib_mock):
        self.assertRaises(AssertionError, spotify.InboxPostResult)

    def test_adds_ref_to_sp_inbox_when_created(self, lib_mock):
        sp_inbox = spotify.ffi.new('int *')

        spotify.InboxPostResult(sp_inbox=sp_inbox)

        lib_mock.sp_inbox_add_ref.assert_called_with(sp_inbox)

    def test_releases_sp_inbox_when_result_dies(self, lib_mock):
        sp_inbox = spotify.ffi.new('int *')

        inbox_post_result = spotify.InboxPostResult(sp_inbox=sp_inbox)
        inbox_post_result = None  # noqa
        tests.gc_collect()

        lib_mock.sp_inbox_release.assert_called_with(sp_inbox)

    @mock.patch('spotify.track.lib', spec=spotify.lib)
    def test_inbox_post_tracks(self, track_lib_mock, lib_mock):
        session = self.create_session(lib_mock)
        sp_track1 = spotify.ffi.new('int *')
        track1 = spotify.Track(sp_track=sp_track1)
        sp_track2 = spotify.ffi.new('int *')
        track2 = spotify.Track(sp_track=sp_track2)
        sp_inbox = spotify.ffi.new('int *')
        lib_mock.sp_inbox_post_tracks.return_value = sp_inbox

        result = spotify.InboxPostResult('alice', [track1, track2], '♥')

        lib_mock.sp_inbox_post_tracks.assert_called_with(
            session._sp_session, b'alice', mock.ANY, 2, b'\xe2\x99\xa5',
            spotify.ffi.NULL, spotify.ffi.NULL)
        self.assertIn(
            sp_track1, lib_mock.sp_inbox_post_tracks.call_args[0][2])
        self.assertIn(
            sp_track2, lib_mock.sp_inbox_post_tracks.call_args[0][2])
        self.assertIsInstance(result, spotify.InboxPostResult)
        self.assertEqual(result._sp_inbox, sp_inbox)

    @mock.patch('spotify.track.lib', spec=spotify.lib)
    def test_create_with_single_track(self, track_lib_mock, lib_mock):
        session = self.create_session(lib_mock)
        sp_track1 = spotify.ffi.new('int *')
        track1 = spotify.Track(sp_track=sp_track1)
        sp_inbox = spotify.ffi.new('int *')
        lib_mock.sp_inbox_post_tracks.return_value = sp_inbox

        result = spotify.InboxPostResult('alice', track1, '♥')

        lib_mock.sp_inbox_post_tracks.assert_called_with(
            session._sp_session, b'alice', mock.ANY, 1, b'\xe2\x99\xa5',
            spotify.ffi.NULL, spotify.ffi.NULL)
        self.assertIn(
            sp_track1, lib_mock.sp_inbox_post_tracks.call_args[0][2])
        self.assertIsInstance(result, spotify.InboxPostResult)
        self.assertEqual(result._sp_inbox, sp_inbox)

    @mock.patch('spotify.track.lib', spec=spotify.lib)
    def test_fail_to_init_raises_error(self, track_lib_mock, lib_mock):
        sp_track1 = spotify.ffi.new('int *')
        track1 = spotify.Track(sp_track=sp_track1)
        sp_track2 = spotify.ffi.new('int *')
        track2 = spotify.Track(sp_track=sp_track2)
        lib_mock.sp_inbox_post_tracks.return_value = spotify.ffi.NULL

        with self.assertRaises(spotify.Error):
            spotify.InboxPostResult('alice', [track1, track2], 'Enjoy!')

    def test_error(self, lib_mock):
        lib_mock.sp_inbox_error.return_value = int(
            spotify.ErrorType.INBOX_IS_FULL)
        sp_inbox = spotify.ffi.new('int *')
        inbox_post_result = spotify.InboxPostResult(sp_inbox=sp_inbox)

        result = inbox_post_result.error

        lib_mock.sp_inbox_error.assert_called_once_with(sp_inbox)
        self.assertIs(result, spotify.ErrorType.INBOX_IS_FULL)
