from __future__ import unicode_literals

import gc
import mock
import unittest

import spotify


@mock.patch('spotify.search.lib', spec=spotify.lib)
class SearchTest(unittest.TestCase):

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

    @mock.patch('spotify.link.Link', spec=spotify.Link)
    def test_link_creates_link_to_search(self, link_mock, lib_mock):
        link_mock.return_value = mock.sentinel.link
        sp_search = spotify.ffi.new('int *')
        search = spotify.Search(sp_search)

        result = search.link

        link_mock.assert_called_once_with(search)
        self.assertEqual(result, mock.sentinel.link)
