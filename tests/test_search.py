from __future__ import unicode_literals

import gc
import mock
import unittest

import spotify


@mock.patch('spotify.search.lib', spec=spotify.lib)
class SearchTest(unittest.TestCase):

    def assert_fails_if_error(self, lib_mock, func):
        lib_mock.sp_search_error.return_value = (
            spotify.ErrorType.BAD_API_VERSION)
        sp_search = spotify.ffi.new('int *')
        search = spotify.Search(sp_search)

        self.assertRaises(spotify.Error, func, search)

    def test_adds_ref_to_sp_search_when_created(self, lib_mock):
        sp_search = spotify.ffi.new('int *')

        spotify.Search(sp_search)

        lib_mock.sp_search_add_ref.assert_called_with(sp_search)

    def test_releases_sp_search_when_search_dies(self, lib_mock):
        sp_search = spotify.ffi.new('int *')

        search = spotify.Search(sp_search)
        search = None  # noqa
        gc.collect()  # Needed for PyPy

        lib_mock.sp_search_release.assert_called_with(sp_search)

    def test_is_loaded(self, lib_mock):
        lib_mock.sp_search_is_loaded.return_value = 1
        sp_search = spotify.ffi.new('int *')
        search = spotify.Search(sp_search)

        result = search.is_loaded

        lib_mock.sp_search_is_loaded.assert_called_once_with(sp_search)
        self.assertTrue(result)

    def test_error(self, lib_mock):
        lib_mock.sp_search_error.return_value = int(
            spotify.ErrorType.IS_LOADING)
        sp_search = spotify.ffi.new('int *')
        search = spotify.Search(sp_search)

        result = search.error

        lib_mock.sp_search_error.assert_called_once_with(sp_search)
        self.assertIs(result, spotify.ErrorType.IS_LOADING)

    # TODO tracks
    # TODO albums
    # TODO playlists
    # TODO artists

    def test_query(self, lib_mock):
        lib_mock.sp_search_error.return_value = spotify.ErrorType.OK
        lib_mock.sp_search_query.return_value = spotify.ffi.new(
            'char[]', b'Foo Bar Baz')
        sp_search = spotify.ffi.new('int *')
        search = spotify.Search(sp_search)

        result = search.query

        lib_mock.sp_search_query.assert_called_once_with(sp_search)
        self.assertEqual(result, 'Foo Bar Baz')

    def test_query_is_none_if_empty(self, lib_mock):
        lib_mock.sp_search_error.return_value = spotify.ErrorType.OK
        lib_mock.sp_search_query.return_value = spotify.ffi.new('char[]', b'')
        sp_search = spotify.ffi.new('int *')
        search = spotify.Search(sp_search)

        result = search.query

        lib_mock.sp_search_query.assert_called_once_with(sp_search)
        self.assertIsNone(result)

    def test_query_fails_if_error(self, lib_mock):
        self.assert_fails_if_error(lib_mock, lambda s: s.query)

    def test_did_you_mean(self, lib_mock):
        lib_mock.sp_search_error.return_value = spotify.ErrorType.OK
        lib_mock.sp_search_did_you_mean.return_value = spotify.ffi.new(
            'char[]', b'Foo Bar Baz')
        sp_search = spotify.ffi.new('int *')
        search = spotify.Search(sp_search)

        result = search.did_you_mean

        lib_mock.sp_search_did_you_mean.assert_called_once_with(sp_search)
        self.assertEqual(result, 'Foo Bar Baz')

    def test_did_you_mean_is_none_if_empty(self, lib_mock):
        lib_mock.sp_search_error.return_value = spotify.ErrorType.OK
        lib_mock.sp_search_did_you_mean.return_value = spotify.ffi.new(
            'char[]', b'')
        sp_search = spotify.ffi.new('int *')
        search = spotify.Search(sp_search)

        result = search.did_you_mean

        lib_mock.sp_search_did_you_mean.assert_called_once_with(sp_search)
        self.assertIsNone(result)

    def test_did_you_mean_fails_if_error(self, lib_mock):
        self.assert_fails_if_error(lib_mock, lambda s: s.did_you_mean)

    def test_total_tracks(self, lib_mock):
        lib_mock.sp_search_error.return_value = spotify.ErrorType.OK
        lib_mock.sp_search_total_tracks.return_value = 75
        sp_search = spotify.ffi.new('int *')
        search = spotify.Search(sp_search)

        result = search.total_tracks

        lib_mock.sp_search_total_tracks.assert_called_with(sp_search)
        self.assertEqual(result, 75)

    def test_total_tracks_fails_if_error(self, lib_mock):
        self.assert_fails_if_error(lib_mock, lambda s: s.total_tracks)

    def test_total_albums(self, lib_mock):
        lib_mock.sp_search_error.return_value = spotify.ErrorType.OK
        lib_mock.sp_search_total_albums.return_value = 75
        sp_search = spotify.ffi.new('int *')
        search = spotify.Search(sp_search)

        result = search.total_albums

        lib_mock.sp_search_total_albums.assert_called_with(sp_search)
        self.assertEqual(result, 75)

    def test_total_albums_fails_if_error(self, lib_mock):
        self.assert_fails_if_error(lib_mock, lambda s: s.total_albums)

    @mock.patch('spotify.link.Link', spec=spotify.Link)
    def test_link_creates_link_to_search(self, link_mock, lib_mock):
        link_mock.return_value = mock.sentinel.link
        sp_search = spotify.ffi.new('int *')
        search = spotify.Search(sp_search)

        result = search.link

        link_mock.assert_called_once_with(search)
        self.assertEqual(result, mock.sentinel.link)
