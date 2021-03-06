from __future__ import unicode_literals

import unittest

import spotify
import tests
from tests import mock


@mock.patch("spotify.playlist_unseen_tracks.lib", spec=spotify.lib)
class PlaylistUnseenTracksTest(unittest.TestCase):

    # TODO Test that the collection releases sp_playlistcontainer and
    # sp_playlist when no longer referenced.

    def setUp(self):
        self.session = tests.create_session_mock()

    @mock.patch("spotify.track.lib", spec=spotify.lib)
    def test_normal_usage(self, track_lib_mock, lib_mock):
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        sp_playlist = spotify.ffi.cast("sp_playlist *", 43)

        total_num_tracks = 3
        sp_tracks = [
            spotify.ffi.cast("sp_track *", 44 + i) for i in range(total_num_tracks)
        ]

        def func(sp_pc, sp_p, sp_t, num_t):
            for i in range(min(total_num_tracks, num_t)):
                sp_t[i] = sp_tracks[i]
            return total_num_tracks

        lib_mock.sp_playlistcontainer_get_unseen_tracks.side_effect = func

        tracks = spotify.PlaylistUnseenTracks(
            self.session, sp_playlistcontainer, sp_playlist
        )

        # Collection keeps references to container and playlist:
        lib_mock.sp_playlistcontainer_add_ref.assert_called_with(sp_playlistcontainer)
        lib_mock.sp_playlist_add_ref.assert_called_with(sp_playlist)

        # Getting collection and length causes no tracks to be retrieved:
        self.assertEqual(len(tracks), total_num_tracks)
        self.assertEqual(lib_mock.sp_playlistcontainer_get_unseen_tracks.call_count, 1)
        lib_mock.sp_playlistcontainer_get_unseen_tracks.assert_called_with(
            sp_playlistcontainer, sp_playlist, mock.ANY, 0
        )

        # Getting items causes more tracks to be retrieved:
        track0 = tracks[0]
        self.assertEqual(lib_mock.sp_playlistcontainer_get_unseen_tracks.call_count, 2)
        lib_mock.sp_playlistcontainer_get_unseen_tracks.assert_called_with(
            sp_playlistcontainer, sp_playlist, mock.ANY, total_num_tracks
        )
        self.assertIsInstance(track0, spotify.Track)
        self.assertEqual(track0._sp_track, sp_tracks[0])

        # Getting already retrieved tracks causes no new retrieval:
        track1 = tracks[1]
        self.assertEqual(lib_mock.sp_playlistcontainer_get_unseen_tracks.call_count, 2)
        self.assertIsInstance(track1, spotify.Track)
        self.assertEqual(track1._sp_track, sp_tracks[1])

        # Getting item with negative index
        track2 = tracks[-3]
        self.assertEqual(track2._sp_track, track0._sp_track)
        self.assertEqual(lib_mock.sp_playlistcontainer_get_unseen_tracks.call_count, 2)

    def test_raises_error_on_failure(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        sp_playlist = spotify.ffi.cast("sp_playlist *", 43)
        lib_mock.sp_playlistcontainer_get_unseen_tracks.return_value = -3

        with self.assertRaises(spotify.Error):
            spotify.PlaylistUnseenTracks(
                self.session, sp_playlistcontainer, sp_playlist
            )

    @mock.patch("spotify.track.lib", spec=spotify.lib)
    def test_getitem_with_slice(self, track_lib_mock, lib_mock):
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        sp_playlist = spotify.ffi.cast("sp_playlist *", 43)

        total_num_tracks = 3
        sp_tracks = [
            spotify.ffi.cast("sp_track *", 44 + i) for i in range(total_num_tracks)
        ]

        def func(sp_pc, sp_p, sp_t, num_t):
            for i in range(min(total_num_tracks, num_t)):
                sp_t[i] = sp_tracks[i]
            return total_num_tracks

        lib_mock.sp_playlistcontainer_get_unseen_tracks.side_effect = func

        tracks = spotify.PlaylistUnseenTracks(
            self.session, sp_playlistcontainer, sp_playlist
        )

        result = tracks[0:2]

        # Only a subslice of length 2 is returned
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], spotify.Track)
        self.assertEqual(result[0]._sp_track, sp_tracks[0])
        self.assertIsInstance(result[1], spotify.Track)
        self.assertEqual(result[1]._sp_track, sp_tracks[1])

    def test_getitem_raises_index_error_on_too_low_index(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        sp_playlist = spotify.ffi.cast("sp_playlist *", 43)
        lib_mock.sp_playlistcontainer_get_unseen_tracks.return_value = 0
        tracks = spotify.PlaylistUnseenTracks(
            self.session, sp_playlistcontainer, sp_playlist
        )

        with self.assertRaises(IndexError) as ctx:
            tracks[-1]

        self.assertEqual(str(ctx.exception), "list index out of range")

    def test_getitem_raises_index_error_on_too_high_index(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        sp_playlist = spotify.ffi.cast("sp_playlist *", 43)
        lib_mock.sp_playlistcontainer_get_unseen_tracks.return_value = 0
        tracks = spotify.PlaylistUnseenTracks(
            self.session, sp_playlistcontainer, sp_playlist
        )

        with self.assertRaises(IndexError) as ctx:
            tracks[1]

        self.assertEqual(str(ctx.exception), "list index out of range")

    def test_getitem_raises_type_error_on_non_integral_index(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        sp_playlist = spotify.ffi.cast("sp_playlist *", 43)
        lib_mock.sp_playlistcontainer_get_unseen_tracks.return_value = 0
        tracks = spotify.PlaylistUnseenTracks(
            self.session, sp_playlistcontainer, sp_playlist
        )

        with self.assertRaises(TypeError):
            tracks["abc"]

    def test_repr(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        sp_playlist = spotify.ffi.cast("sp_playlist *", 43)
        lib_mock.sp_playlistcontainer_get_unseen_tracks.return_value = 0
        tracks = spotify.PlaylistUnseenTracks(
            self.session, sp_playlistcontainer, sp_playlist
        )

        self.assertEqual(repr(tracks), "PlaylistUnseenTracks([])")
