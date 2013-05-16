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

    @mock.patch('spotify.link.Link', spec=spotify.Link)
    def test_as_link_creates_link_to_search(self, link_mock, lib_mock):
        link_mock.return_value = mock.sentinel.link
        sp_search = spotify.ffi.new('int *')
        search = spotify.Search(sp_search)

        result = search.as_link()

        link_mock.assert_called_once_with(search)
        self.assertEqual(result, mock.sentinel.link)
