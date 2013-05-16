from __future__ import unicode_literals

import gc
import mock
import unittest

import spotify


@mock.patch('spotify.album.lib')
class AlbumTest(unittest.TestCase):

    def test_adds_ref_to_sp_album_when_created(self, lib_mock):
        sp_album = spotify.ffi.new('int *')

        spotify.Album(sp_album)

        lib_mock.sp_album_add_ref.assert_called_with(sp_album)

    def test_releases_sp_album_when_album_dies(self, lib_mock):
        sp_album = spotify.ffi.new('int *')

        album = spotify.Album(sp_album)
        album = None  # noqa
        gc.collect()  # Needed for PyPy

        lib_mock.sp_album_release.assert_called_with(sp_album)

    @mock.patch('spotify.link.Link')
    def test_as_link_creates_link_to_album(self, link_mock, lib_mock):
        link_mock.return_value = mock.sentinel.link
        sp_album = spotify.ffi.new('int *')
        album = spotify.Album(sp_album)

        result = album.as_link()

        link_mock.assert_called_once_with(album)
        self.assertEqual(result, mock.sentinel.link)
