from __future__ import unicode_literals

import unittest

import spotify
import tests
from tests import mock


@mock.patch("spotify.toplist.lib", spec=spotify.lib)
class ToplistTest(unittest.TestCase):
    def setUp(self):
        self.session = tests.create_session_mock()
        spotify._session_instance = self.session

    def tearDown(self):
        spotify._session_instance = None

    def assert_fails_if_error(self, lib_mock, func):
        lib_mock.sp_toplistbrowse_error.return_value = spotify.ErrorType.BAD_API_VERSION
        sp_toplistbrowse = spotify.ffi.cast("sp_toplistbrowse *", 42)
        toplist = spotify.Toplist(self.session, sp_toplistbrowse=sp_toplistbrowse)

        with self.assertRaises(spotify.Error):
            func(toplist)

    def test_create_without_type_or_region_or_sp_toplistbrowse_fails(self, lib_mock):
        with self.assertRaises(AssertionError):
            spotify.Toplist(self.session)

    def test_create_from_type_and_current_user_region(self, lib_mock):
        sp_toplistbrowse = spotify.ffi.cast("sp_toplistbrowse *", 42)
        lib_mock.sp_toplistbrowse_create.return_value = sp_toplistbrowse

        result = spotify.Toplist(
            self.session,
            type=spotify.ToplistType.TRACKS,
            region=spotify.ToplistRegion.USER,
        )

        lib_mock.sp_toplistbrowse_create.assert_called_with(
            self.session._sp_session,
            int(spotify.ToplistType.TRACKS),
            int(spotify.ToplistRegion.USER),
            spotify.ffi.NULL,
            mock.ANY,
            mock.ANY,
        )
        self.assertEqual(lib_mock.sp_toplistbrowse_add_ref.call_count, 0)
        self.assertEqual(result._sp_toplistbrowse, sp_toplistbrowse)

    def test_create_from_type_and_specific_user_region(self, lib_mock):
        sp_toplistbrowse = spotify.ffi.cast("sp_toplistbrowse *", 42)
        lib_mock.sp_toplistbrowse_create.return_value = sp_toplistbrowse

        spotify.Toplist(
            self.session,
            type=spotify.ToplistType.TRACKS,
            region=spotify.ToplistRegion.USER,
            canonical_username="alice",
        )

        lib_mock.sp_toplistbrowse_create.assert_called_with(
            self.session._sp_session,
            int(spotify.ToplistType.TRACKS),
            int(spotify.ToplistRegion.USER),
            mock.ANY,
            mock.ANY,
            mock.ANY,
        )
        self.assertEqual(
            spotify.ffi.string(lib_mock.sp_toplistbrowse_create.call_args[0][3]),
            b"alice",
        )

    def test_create_from_type_and_country(self, lib_mock):
        sp_toplistbrowse = spotify.ffi.cast("sp_toplistbrowse *", 42)
        lib_mock.sp_toplistbrowse_create.return_value = sp_toplistbrowse

        spotify.Toplist(self.session, type=spotify.ToplistType.TRACKS, region="NO")

        lib_mock.sp_toplistbrowse_create.assert_called_with(
            self.session._sp_session,
            int(spotify.ToplistType.TRACKS),
            20047,
            spotify.ffi.NULL,
            mock.ANY,
            mock.ANY,
        )

    def test_create_with_callback(self, lib_mock):
        sp_toplistbrowse = spotify.ffi.cast("sp_toplistbrowse *", 42)
        lib_mock.sp_toplistbrowse_create.return_value = sp_toplistbrowse
        callback = mock.Mock()

        result = spotify.Toplist(
            self.session,
            type=spotify.ToplistType.TRACKS,
            region=spotify.ToplistRegion.USER,
            callback=callback,
        )

        toplistbrowse_complete_cb = lib_mock.sp_toplistbrowse_create.call_args[0][4]
        userdata = lib_mock.sp_toplistbrowse_create.call_args[0][5]
        toplistbrowse_complete_cb(sp_toplistbrowse, userdata)

        result.loaded_event.wait(3)
        callback.assert_called_with(result)

    def test_toplist_is_gone_before_callback_is_called(self, lib_mock):
        sp_toplistbrowse = spotify.ffi.cast("sp_toplistbrowse *", 42)
        lib_mock.sp_toplistbrowse_create.return_value = sp_toplistbrowse
        callback = mock.Mock()

        result = spotify.Toplist(
            self.session,
            type=spotify.ToplistType.TRACKS,
            region=spotify.ToplistRegion.USER,
            callback=callback,
        )
        loaded_event = result.loaded_event
        result = None  # noqa
        tests.gc_collect()

        # The mock keeps the handle/userdata alive, thus this test doesn't
        # really test that session._callback_handles keeps the handle alive.
        toplistbrowse_complete_cb = lib_mock.sp_toplistbrowse_create.call_args[0][4]
        userdata = lib_mock.sp_toplistbrowse_create.call_args[0][5]
        toplistbrowse_complete_cb(sp_toplistbrowse, userdata)

        loaded_event.wait(3)
        self.assertEqual(callback.call_count, 1)
        self.assertEqual(callback.call_args[0][0]._sp_toplistbrowse, sp_toplistbrowse)

    def test_adds_ref_to_sp_toplistbrowse_when_created(self, lib_mock):
        sp_toplistbrowse = spotify.ffi.cast("sp_toplistbrowse *", 42)

        spotify.Toplist(self.session, sp_toplistbrowse=sp_toplistbrowse)

        lib_mock.sp_toplistbrowse_add_ref.assert_called_once_with(sp_toplistbrowse)

    def test_releases_sp_toplistbrowse_when_toplist_dies(self, lib_mock):
        sp_toplistbrowse = spotify.ffi.cast("sp_toplistbrowse *", 42)

        toplist = spotify.Toplist(self.session, sp_toplistbrowse=sp_toplistbrowse)
        toplist = None  # noqa
        tests.gc_collect()

        lib_mock.sp_toplistbrowse_release.assert_called_with(sp_toplistbrowse)

    def test_repr(self, lib_mock):
        sp_toplistbrowse = spotify.ffi.cast("sp_toplistbrowse *", 42)
        lib_mock.sp_toplistbrowse_create.return_value = sp_toplistbrowse
        toplist = spotify.Toplist(
            self.session, type=spotify.ToplistType.TRACKS, region="NO"
        )

        result = repr(toplist)

        self.assertEqual(
            result,
            "Toplist(type=<ToplistType.TRACKS: 2>, region=%r, "
            "canonical_username=None)" % "NO",
        )

    def test_eq(self, lib_mock):
        sp_toplistbrowse = spotify.ffi.cast("sp_toplistbrowse *", 42)
        toplist1 = spotify.Toplist(self.session, sp_toplistbrowse=sp_toplistbrowse)
        toplist2 = spotify.Toplist(self.session, sp_toplistbrowse=sp_toplistbrowse)

        self.assertTrue(toplist1 == toplist2)
        self.assertFalse(toplist1 == "foo")

    def test_ne(self, lib_mock):
        sp_toplistbrowse = spotify.ffi.cast("sp_toplistbrowse *", 42)
        toplist1 = spotify.Toplist(self.session, sp_toplistbrowse=sp_toplistbrowse)
        toplist2 = spotify.Toplist(self.session, sp_toplistbrowse=sp_toplistbrowse)

        self.assertFalse(toplist1 != toplist2)

    def test_hash(self, lib_mock):
        sp_toplistbrowse = spotify.ffi.cast("sp_toplistbrowse *", 42)
        toplist1 = spotify.Toplist(self.session, sp_toplistbrowse=sp_toplistbrowse)
        toplist2 = spotify.Toplist(self.session, sp_toplistbrowse=sp_toplistbrowse)

        self.assertEqual(hash(toplist1), hash(toplist2))

    def test_is_loaded(self, lib_mock):
        lib_mock.sp_toplistbrowse_is_loaded.return_value = 1
        sp_toplistbrowse = spotify.ffi.cast("sp_toplistbrowse *", 42)
        toplist = spotify.Toplist(self.session, sp_toplistbrowse=sp_toplistbrowse)

        result = toplist.is_loaded

        lib_mock.sp_toplistbrowse_is_loaded.assert_called_once_with(sp_toplistbrowse)
        self.assertTrue(result)

    @mock.patch("spotify.utils.load")
    def test_load(self, load_mock, lib_mock):
        sp_toplistbrowse = spotify.ffi.cast("sp_toplistbrowse *", 42)
        toplist = spotify.Toplist(self.session, sp_toplistbrowse=sp_toplistbrowse)

        toplist.load(10)

        load_mock.assert_called_with(self.session, toplist, timeout=10)

    def test_error(self, lib_mock):
        lib_mock.sp_toplistbrowse_error.return_value = int(
            spotify.ErrorType.OTHER_PERMANENT
        )
        sp_toplistbrowse = spotify.ffi.cast("sp_toplistbrowse *", 42)
        toplist = spotify.Toplist(self.session, sp_toplistbrowse=sp_toplistbrowse)

        result = toplist.error

        lib_mock.sp_toplistbrowse_error.assert_called_once_with(sp_toplistbrowse)
        self.assertIs(result, spotify.ErrorType.OTHER_PERMANENT)

    def test_backend_request_duration(self, lib_mock):
        lib_mock.sp_toplistbrowse_backend_request_duration.return_value = 137
        sp_toplistbrowse = spotify.ffi.cast("sp_toplistbrowse *", 42)
        toplist = spotify.Toplist(self.session, sp_toplistbrowse=sp_toplistbrowse)

        result = toplist.backend_request_duration

        lib_mock.sp_toplistbrowse_backend_request_duration.assert_called_with(
            sp_toplistbrowse
        )
        self.assertEqual(result, 137)

    def test_backend_request_duration_when_not_loaded(self, lib_mock):
        lib_mock.sp_toplistbrowse_is_loaded.return_value = 0
        sp_toplistbrowse = spotify.ffi.cast("sp_toplistbrowse *", 42)
        toplist = spotify.Toplist(self.session, sp_toplistbrowse=sp_toplistbrowse)

        result = toplist.backend_request_duration

        lib_mock.sp_toplistbrowse_is_loaded.assert_called_with(sp_toplistbrowse)
        self.assertEqual(
            lib_mock.sp_toplistbrowse_backend_request_duration.call_count, 0
        )
        self.assertIsNone(result)

    @mock.patch("spotify.track.lib", spec=spotify.lib)
    def test_tracks(self, track_lib_mock, lib_mock):
        lib_mock.sp_toplistbrowse_error.return_value = spotify.ErrorType.OK
        sp_track = spotify.ffi.cast("sp_track *", 43)
        lib_mock.sp_toplistbrowse_num_tracks.return_value = 1
        lib_mock.sp_toplistbrowse_track.return_value = sp_track
        sp_toplistbrowse = spotify.ffi.cast("sp_toplistbrowse *", 42)
        toplist = spotify.Toplist(self.session, sp_toplistbrowse=sp_toplistbrowse)

        self.assertEqual(lib_mock.sp_toplistbrowse_add_ref.call_count, 1)
        result = toplist.tracks
        self.assertEqual(lib_mock.sp_toplistbrowse_add_ref.call_count, 2)

        self.assertEqual(len(result), 1)
        lib_mock.sp_toplistbrowse_num_tracks.assert_called_with(sp_toplistbrowse)

        item = result[0]
        self.assertIsInstance(item, spotify.Track)
        self.assertEqual(item._sp_track, sp_track)
        self.assertEqual(lib_mock.sp_toplistbrowse_track.call_count, 1)
        lib_mock.sp_toplistbrowse_track.assert_called_with(sp_toplistbrowse, 0)
        track_lib_mock.sp_track_add_ref.assert_called_with(sp_track)

    def test_tracks_if_no_tracks(self, lib_mock):
        lib_mock.sp_toplistbrowse_error.return_value = spotify.ErrorType.OK
        lib_mock.sp_toplistbrowse_num_tracks.return_value = 0
        sp_toplistbrowse = spotify.ffi.cast("sp_toplistbrowse *", 42)
        toplist = spotify.Toplist(self.session, sp_toplistbrowse=sp_toplistbrowse)

        result = toplist.tracks

        self.assertEqual(len(result), 0)
        lib_mock.sp_toplistbrowse_num_tracks.assert_called_with(sp_toplistbrowse)
        self.assertEqual(lib_mock.sp_toplistbrowse_track.call_count, 0)

    def test_tracks_if_unloaded(self, lib_mock):
        lib_mock.sp_toplistbrowse_error.return_value = spotify.ErrorType.OK
        lib_mock.sp_toplistbrowse_is_loaded.return_value = 0
        sp_toplistbrowse = spotify.ffi.cast("sp_toplistbrowse *", 42)
        toplist = spotify.Toplist(self.session, sp_toplistbrowse=sp_toplistbrowse)

        result = toplist.tracks

        lib_mock.sp_toplistbrowse_is_loaded.assert_called_with(sp_toplistbrowse)
        self.assertEqual(len(result), 0)

    def test_tracks_fails_if_error(self, lib_mock):
        self.assert_fails_if_error(lib_mock, lambda s: s.tracks)

    @mock.patch("spotify.album.lib", spec=spotify.lib)
    def test_albums(self, album_lib_mock, lib_mock):
        lib_mock.sp_toplistbrowse_error.return_value = spotify.ErrorType.OK
        sp_album = spotify.ffi.cast("sp_album *", 43)
        lib_mock.sp_toplistbrowse_num_albums.return_value = 1
        lib_mock.sp_toplistbrowse_album.return_value = sp_album
        sp_toplistbrowse = spotify.ffi.cast("sp_toplistbrowse *", 42)
        toplist = spotify.Toplist(self.session, sp_toplistbrowse=sp_toplistbrowse)

        self.assertEqual(lib_mock.sp_toplistbrowse_add_ref.call_count, 1)
        result = toplist.albums
        self.assertEqual(lib_mock.sp_toplistbrowse_add_ref.call_count, 2)

        self.assertEqual(len(result), 1)
        lib_mock.sp_toplistbrowse_num_albums.assert_called_with(sp_toplistbrowse)

        item = result[0]
        self.assertIsInstance(item, spotify.Album)
        self.assertEqual(item._sp_album, sp_album)
        self.assertEqual(lib_mock.sp_toplistbrowse_album.call_count, 1)
        lib_mock.sp_toplistbrowse_album.assert_called_with(sp_toplistbrowse, 0)
        album_lib_mock.sp_album_add_ref.assert_called_with(sp_album)

    def test_albums_if_no_albums(self, lib_mock):
        lib_mock.sp_toplistbrowse_error.return_value = spotify.ErrorType.OK
        lib_mock.sp_toplistbrowse_num_albums.return_value = 0
        sp_toplistbrowse = spotify.ffi.cast("sp_toplistbrowse *", 42)
        toplist = spotify.Toplist(self.session, sp_toplistbrowse=sp_toplistbrowse)

        result = toplist.albums

        self.assertEqual(len(result), 0)
        lib_mock.sp_toplistbrowse_num_albums.assert_called_with(sp_toplistbrowse)
        self.assertEqual(lib_mock.sp_toplistbrowse_album.call_count, 0)

    def test_albums_if_unloaded(self, lib_mock):
        lib_mock.sp_toplistbrowse_error.return_value = spotify.ErrorType.OK
        lib_mock.sp_toplistbrowse_is_loaded.return_value = 0
        sp_toplistbrowse = spotify.ffi.cast("sp_toplistbrowse *", 42)
        toplist = spotify.Toplist(self.session, sp_toplistbrowse=sp_toplistbrowse)

        result = toplist.albums

        lib_mock.sp_toplistbrowse_is_loaded.assert_called_with(sp_toplistbrowse)
        self.assertEqual(len(result), 0)

    def test_albums_fails_if_error(self, lib_mock):
        self.assert_fails_if_error(lib_mock, lambda s: s.albums)

    @mock.patch("spotify.artist.lib", spec=spotify.lib)
    def test_artists(self, artist_lib_mock, lib_mock):
        lib_mock.sp_toplistbrowse_error.return_value = spotify.ErrorType.OK
        sp_artist = spotify.ffi.cast("sp_artist *", 43)
        lib_mock.sp_toplistbrowse_num_artists.return_value = 1
        lib_mock.sp_toplistbrowse_artist.return_value = sp_artist
        sp_toplistbrowse = spotify.ffi.cast("sp_toplistbrowse *", 42)
        toplist = spotify.Toplist(self.session, sp_toplistbrowse=sp_toplistbrowse)

        self.assertEqual(lib_mock.sp_toplistbrowse_add_ref.call_count, 1)
        result = toplist.artists
        self.assertEqual(lib_mock.sp_toplistbrowse_add_ref.call_count, 2)

        self.assertEqual(len(result), 1)
        lib_mock.sp_toplistbrowse_num_artists.assert_called_with(sp_toplistbrowse)

        item = result[0]
        self.assertIsInstance(item, spotify.Artist)
        self.assertEqual(item._sp_artist, sp_artist)
        self.assertEqual(lib_mock.sp_toplistbrowse_artist.call_count, 1)
        lib_mock.sp_toplistbrowse_artist.assert_called_with(sp_toplistbrowse, 0)
        artist_lib_mock.sp_artist_add_ref.assert_called_with(sp_artist)

    def test_artists_if_no_artists(self, lib_mock):
        lib_mock.sp_toplistbrowse_error.return_value = spotify.ErrorType.OK
        lib_mock.sp_toplistbrowse_num_artists.return_value = 0
        sp_toplistbrowse = spotify.ffi.cast("sp_toplistbrowse *", 42)
        toplist = spotify.Toplist(self.session, sp_toplistbrowse=sp_toplistbrowse)

        result = toplist.artists

        self.assertEqual(len(result), 0)
        lib_mock.sp_toplistbrowse_num_artists.assert_called_with(sp_toplistbrowse)
        self.assertEqual(lib_mock.sp_toplistbrowse_artist.call_count, 0)

    def test_artists_if_unloaded(self, lib_mock):
        lib_mock.sp_toplistbrowse_error.return_value = spotify.ErrorType.OK
        lib_mock.sp_toplistbrowse_is_loaded.return_value = 0
        sp_toplistbrowse = spotify.ffi.cast("sp_toplistbrowse *", 42)
        toplist = spotify.Toplist(self.session, sp_toplistbrowse=sp_toplistbrowse)

        result = toplist.artists

        lib_mock.sp_toplistbrowse_is_loaded.assert_called_with(sp_toplistbrowse)
        self.assertEqual(len(result), 0)

    def test_artists_fails_if_error(self, lib_mock):
        self.assert_fails_if_error(lib_mock, lambda s: s.artists)


class ToplistRegionTest(unittest.TestCase):
    def test_has_toplist_region_constants(self):
        self.assertEqual(spotify.ToplistRegion.EVERYWHERE, 0)
        self.assertEqual(spotify.ToplistRegion.USER, 1)


class ToplistTypeTest(unittest.TestCase):
    def test_has_toplist_type_constants(self):
        self.assertEqual(spotify.ToplistType.ARTISTS, 0)
        self.assertEqual(spotify.ToplistType.ALBUMS, 1)
        self.assertEqual(spotify.ToplistType.TRACKS, 2)
