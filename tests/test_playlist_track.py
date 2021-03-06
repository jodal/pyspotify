from __future__ import unicode_literals

import unittest

import spotify
import tests
from tests import mock


@mock.patch("spotify.playlist_track.lib", spec=spotify.lib)
class PlaylistTrackTest(unittest.TestCase):
    def setUp(self):
        self.session = tests.create_session_mock()

    @mock.patch("spotify.track.lib", spec=spotify.lib)
    def test_track(self, track_lib_mock, lib_mock):
        sp_track = spotify.ffi.cast("sp_track *", 43)
        lib_mock.sp_playlist_track.return_value = sp_track
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist_track = spotify.PlaylistTrack(self.session, sp_playlist, 0)

        result = playlist_track.track

        lib_mock.sp_playlist_track.assert_called_with(sp_playlist, 0)
        track_lib_mock.sp_track_add_ref.assert_called_with(sp_track)
        self.assertIsInstance(result, spotify.Track)
        self.assertEqual(result._sp_track, sp_track)

    @mock.patch("spotify.Track", spec=spotify.Track)
    @mock.patch("spotify.User", spec=spotify.User)
    def test_repr(self, user_mock, track_mock, lib_mock):
        sp_track = spotify.ffi.cast("sp_track *", 43)
        lib_mock.sp_playlist_track.return_value = sp_track
        track_instance_mock = track_mock.return_value
        track_instance_mock.link.uri = "foo"

        lib_mock.sp_playlist_track_create_time.return_value = 1234567890

        sp_user = spotify.ffi.cast("sp_user *", 44)
        lib_mock.sp_playlist_track_creator.return_value = sp_user
        user_mock.return_value = "alice-user-object"

        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist_track = spotify.PlaylistTrack(self.session, sp_playlist, 0)

        result = repr(playlist_track)

        self.assertEqual(
            result,
            "PlaylistTrack(uri=%r, creator=%r, create_time=%d)"
            % ("foo", "alice-user-object", 1234567890),
        )

    def test_eq(self, lib_mock):
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        track1 = spotify.PlaylistTrack(self.session, sp_playlist, 0)
        track2 = spotify.PlaylistTrack(self.session, sp_playlist, 0)

        self.assertTrue(track1 == track2)
        self.assertFalse(track1 == "foo")

    def test_ne(self, lib_mock):
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        track1 = spotify.PlaylistTrack(self.session, sp_playlist, 0)
        track2 = spotify.PlaylistTrack(self.session, sp_playlist, 0)
        track3 = spotify.PlaylistTrack(self.session, sp_playlist, 1)

        self.assertFalse(track1 != track2)
        self.assertTrue(track1 != track3)

    def test_hash(self, lib_mock):
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        track1 = spotify.PlaylistTrack(self.session, sp_playlist, 0)
        track2 = spotify.PlaylistTrack(self.session, sp_playlist, 0)
        track3 = spotify.PlaylistTrack(self.session, sp_playlist, 1)

        self.assertEqual(hash(track1), hash(track2))
        self.assertNotEqual(hash(track1), hash(track3))

    def test_create_time(self, lib_mock):
        lib_mock.sp_playlist_track_create_time.return_value = 1234567890
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist_track = spotify.PlaylistTrack(self.session, sp_playlist, 0)

        result = playlist_track.create_time

        lib_mock.sp_playlist_track_create_time.assert_called_with(sp_playlist, 0)
        self.assertEqual(result, 1234567890)

    @mock.patch("spotify.user.lib", spec=spotify.lib)
    def test_creator(self, user_lib_mock, lib_mock):
        sp_user = spotify.ffi.cast("sp_user *", 43)
        lib_mock.sp_playlist_track_creator.return_value = sp_user
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist_track = spotify.PlaylistTrack(self.session, sp_playlist, 0)

        result = playlist_track.creator

        lib_mock.sp_playlist_track_creator.assert_called_with(sp_playlist, 0)
        user_lib_mock.sp_user_add_ref.assert_called_with(sp_user)
        self.assertIsInstance(result, spotify.User)
        self.assertEqual(result._sp_user, sp_user)

    def test_is_seen(self, lib_mock):
        lib_mock.sp_playlist_track_seen.return_value = 0
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist_track = spotify.PlaylistTrack(self.session, sp_playlist, 0)

        result = playlist_track.seen

        lib_mock.sp_playlist_track_seen.assert_called_with(sp_playlist, 0)
        self.assertEqual(result, False)

    def test_set_seen(self, lib_mock):
        lib_mock.sp_playlist_track_set_seen.return_value = int(spotify.ErrorType.OK)
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist_track = spotify.PlaylistTrack(self.session, sp_playlist, 0)

        playlist_track.seen = True

        lib_mock.sp_playlist_track_set_seen.assert_called_with(sp_playlist, 0, 1)

    def test_set_seen_fails_if_error(self, lib_mock):
        lib_mock.sp_playlist_track_set_seen.return_value = int(
            spotify.ErrorType.BAD_API_VERSION
        )
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist_track = spotify.PlaylistTrack(self.session, sp_playlist, 0)

        with self.assertRaises(spotify.Error):
            playlist_track.seen = True

    def test_message(self, lib_mock):
        lib_mock.sp_playlist_track_message.return_value = spotify.ffi.new(
            "char[]", b"foo bar"
        )
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist_track = spotify.PlaylistTrack(self.session, sp_playlist, 0)

        result = playlist_track.message

        lib_mock.sp_playlist_track_message.assert_called_with(sp_playlist, 0)
        self.assertEqual(result, "foo bar")

    def test_message_is_none_when_null(self, lib_mock):
        lib_mock.sp_playlist_track_message.return_value = spotify.ffi.NULL
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist_track = spotify.PlaylistTrack(self.session, sp_playlist, 0)

        result = playlist_track.message

        lib_mock.sp_playlist_track_message.assert_called_with(sp_playlist, 0)
        self.assertIsNone(result)
