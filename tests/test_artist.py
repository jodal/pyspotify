from __future__ import unicode_literals

import gc
import mock
import unittest

import spotify


@mock.patch('spotify.artist.lib', spec=spotify.lib)
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

    def test_name(self, lib_mock):
        lib_mock.sp_artist_name.return_value = spotify.ffi.new(
            'char[]', b'Foo Bar Baz')
        sp_artist = spotify.ffi.new('int *')
        artist = spotify.Artist(sp_artist)

        result = artist.name

        lib_mock.sp_artist_name.assert_called_once_with(sp_artist)
        self.assertEqual(result, 'Foo Bar Baz')

    def test_name_is_none_if_unloaded(self, lib_mock):
        lib_mock.sp_artist_name.return_value = spotify.ffi.new('char[]', b'')
        sp_artist = spotify.ffi.new('int *')
        artist = spotify.Artist(sp_artist)

        result = artist.name

        lib_mock.sp_artist_name.assert_called_once_with(sp_artist)
        self.assertIsNone(result)

    def test_is_loaded(self, lib_mock):
        lib_mock.sp_artist_is_loaded.return_value = 1
        sp_artist = spotify.ffi.new('int *')
        artist = spotify.Artist(sp_artist)

        result = artist.is_loaded

        lib_mock.sp_artist_is_loaded.assert_called_once_with(sp_artist)
        self.assertTrue(result)

    @mock.patch('spotify.artist.load')
    def test_load(self, load_mock, lib_mock):
        sp_artist = spotify.ffi.new('int *')
        artist = spotify.Artist(sp_artist)

        artist.load(10)

        load_mock.assert_called_with(artist, timeout=10)

    def test_portrait_id(self, lib_mock):
        lib_mock.sp_artist_portrait.return_value = spotify.ffi.new(
            'char[]', b'portrait-id')
        sp_artist = spotify.ffi.new('int *')
        artist = spotify.Artist(sp_artist)
        image_size = spotify.ImageSize.SMALL

        result = artist.portrait_id(image_size)

        lib_mock.sp_artist_portrait.assert_called_with(
            sp_artist, int(image_size))
        self.assertEqual(result, b'portrait-id')

    def test_portrait_id_is_none_if_null(self, lib_mock):
        lib_mock.sp_artist_portrait.return_value = spotify.ffi.NULL
        sp_artist = spotify.ffi.new('int *')
        artist = spotify.Artist(sp_artist)

        result = artist.portrait_id()

        lib_mock.sp_artist_portrait.assert_called_with(
            sp_artist, int(spotify.ImageSize.NORMAL))
        self.assertIsNone(result)

    @mock.patch('spotify.link.Link', spec=spotify.Link)
    def test_link_creates_link_to_artist(self, link_mock, lib_mock):
        link_mock.return_value = mock.sentinel.link
        sp_artist = spotify.ffi.new('int *')
        artist = spotify.Artist(sp_artist)

        result = artist.link

        link_mock.assert_called_once_with(artist)
        self.assertEqual(result, mock.sentinel.link)
