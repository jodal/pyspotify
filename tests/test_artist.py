from __future__ import unicode_literals

import gc
import mock
import unittest

import spotify


@mock.patch('spotify.artist.lib')
class ArtistTest(unittest.TestCase):

    def test_adds_ref_to_sp_artist_when_created(self, lib_mock):
        sp_artist = spotify.ffi.new('int *')

        spotify.Artist(sp_artist)

        lib_mock.sp_artist_add_ref.assert_called_with(sp_artist)

    def test_releases_sp_artist_when_artist_dies(self, lib_mock):
        sp_artist = spotify.ffi.new('int *')

        artist = spotify.Artist(sp_artist)
        artist = None  # noqa
        gc.collect()  # Needed for PyPy

        lib_mock.sp_artist_release.assert_called_with(sp_artist)

    @mock.patch('spotify.link.Link')
    def test_as_link_creates_link_to_artist(self, link_mock, lib_mock):
        link_mock.return_value = mock.sentinel.link
        sp_artist = spotify.ffi.new('int *')
        artist = spotify.Artist(sp_artist)

        result = artist.as_link()

        link_mock.assert_called_once_with(artist)
        self.assertEqual(result, mock.sentinel.link)
