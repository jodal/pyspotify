from __future__ import unicode_literals

import gc
import mock
import unittest

import spotify


@mock.patch('spotify.album.lib', spec=spotify.lib)
class AlbumTest(unittest.TestCase):

    def create_session(self, lib_mock):
        session = mock.sentinel.session
        session.sp_session = mock.sentinel.sp_session
        spotify.session_instance = session
        return session

    def tearDown(self):
        spotify.session_instance = None

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

    def test_is_loaded(self, lib_mock):
        lib_mock.sp_album_is_loaded.return_value = 1
        sp_album = spotify.ffi.new('int *')
        album = spotify.Album(sp_album)

        result = album.is_loaded

        lib_mock.sp_album_is_loaded.assert_called_once_with(sp_album)
        self.assertTrue(result)

    @mock.patch('spotify.utils.load')
    def test_load(self, load_mock, lib_mock):
        sp_album = spotify.ffi.new('int *')
        album = spotify.Album(sp_album)

        album.load(10)

        load_mock.assert_called_with(album, timeout=10)

    def test_is_available(self, lib_mock):
        lib_mock.sp_album_is_available.return_value = 1
        sp_album = spotify.ffi.new('int *')
        album = spotify.Album(sp_album)

        result = album.is_available

        lib_mock.sp_album_is_available.assert_called_once_with(sp_album)
        self.assertTrue(result)

    def test_is_available_is_none_if_unloaded(self, lib_mock):
        lib_mock.sp_album_is_loaded.return_value = 0
        sp_album = spotify.ffi.new('int *')
        album = spotify.Album(sp_album)

        result = album.is_available

        lib_mock.sp_album_is_loaded.assert_called_once_with(sp_album)
        self.assertIsNone(result)

    @mock.patch('spotify.artist.lib', spec=spotify.lib)
    def test_artist(self, artist_lib_mock, lib_mock):
        sp_artist = spotify.ffi.new('int *')
        lib_mock.sp_album_artist.return_value = sp_artist
        sp_album = spotify.ffi.new('int *')
        album = spotify.Album(sp_album)

        result = album.artist

        lib_mock.sp_album_artist.assert_called_with(sp_album)
        self.assertEqual(artist_lib_mock.sp_artist_add_ref.call_count, 1)
        self.assertIsInstance(result, spotify.Artist)
        self.assertEqual(result.sp_artist, sp_artist)

    @mock.patch('spotify.artist.lib', spec=spotify.lib)
    def test_artist_if_unloaded(self, artist_lib_mock, lib_mock):
        lib_mock.sp_album_artist.return_value = 0
        sp_album = spotify.ffi.new('int *')
        album = spotify.Album(sp_album)

        result = album.artist

        lib_mock.sp_album_artist.assert_called_with(sp_album)
        self.assertIsNone(result)

    @mock.patch('spotify.image.lib', spec=spotify.lib)
    def test_cover(self, image_lib_mock, lib_mock):
        session = self.create_session(lib_mock)
        sp_image_id = spotify.ffi.new('char[]', b'cover-id')
        lib_mock.sp_album_cover.return_value = sp_image_id
        sp_image = spotify.ffi.new('int *')
        lib_mock.sp_image_create.return_value = sp_image
        sp_album = spotify.ffi.new('int *')
        album = spotify.Album(sp_album)
        image_size = spotify.ImageSize.SMALL

        result = album.cover(image_size)

        lib_mock.sp_album_cover.assert_called_with(
            sp_album, int(image_size))
        lib_mock.sp_image_create.assert_called_with(
            session.sp_session, sp_image_id)

        self.assertIsInstance(result, spotify.Image)
        self.assertEqual(result.sp_image, sp_image)

        # Since we *created* the sp_image, we already have a refcount of 1 and
        # shouldn't increase the refcount when wrapping this sp_image in an
        # Image object
        self.assertEqual(image_lib_mock.sp_image_add_ref.call_count, 0)

    def test_cover_is_none_if_null(self, lib_mock):
        lib_mock.sp_album_cover.return_value = spotify.ffi.NULL
        sp_album = spotify.ffi.new('int *')
        album = spotify.Album(sp_album)

        result = album.cover()

        lib_mock.sp_album_cover.assert_called_with(
            sp_album, int(spotify.ImageSize.NORMAL))
        self.assertIsNone(result)

    def test_name(self, lib_mock):
        lib_mock.sp_album_name.return_value = spotify.ffi.new(
            'char[]', b'Foo Bar Baz')
        sp_album = spotify.ffi.new('int *')
        album = spotify.Album(sp_album)

        result = album.name

        lib_mock.sp_album_name.assert_called_once_with(sp_album)
        self.assertEqual(result, 'Foo Bar Baz')

    def test_name_is_none_if_unloaded(self, lib_mock):
        lib_mock.sp_album_name.return_value = spotify.ffi.new('char[]', b'')
        sp_album = spotify.ffi.new('int *')
        album = spotify.Album(sp_album)

        result = album.name

        lib_mock.sp_album_name.assert_called_once_with(sp_album)
        self.assertIsNone(result)

    def test_year(self, lib_mock):
        lib_mock.sp_album_year.return_value = 2013
        sp_album = spotify.ffi.new('int *')
        album = spotify.Album(sp_album)

        result = album.year

        lib_mock.sp_album_year.assert_called_once_with(sp_album)
        self.assertEqual(result, 2013)

    def test_year_is_none_if_unloaded(self, lib_mock):
        lib_mock.sp_album_is_loaded.return_value = 0
        sp_album = spotify.ffi.new('int *')
        album = spotify.Album(sp_album)

        result = album.year

        lib_mock.sp_album_is_loaded.assert_called_once_with(sp_album)
        self.assertIsNone(result)

    def test_type(self, lib_mock):
        lib_mock.sp_album_type.return_value = int(spotify.AlbumType.SINGLE)
        sp_album = spotify.ffi.new('int *')
        album = spotify.Album(sp_album)

        result = album.type

        lib_mock.sp_album_type.assert_called_once_with(sp_album)
        self.assertIs(result, spotify.AlbumType.SINGLE)

    def test_type_is_none_if_unloaded(self, lib_mock):
        lib_mock.sp_album_is_loaded.return_value = 0
        sp_album = spotify.ffi.new('int *')
        album = spotify.Album(sp_album)

        result = album.type

        lib_mock.sp_album_is_loaded.assert_called_once_with(sp_album)
        self.assertIsNone(result)

    @mock.patch('spotify.link.Link', spec=spotify.Link)
    def test_link_creates_link_to_album(self, link_mock, lib_mock):
        link_mock.return_value = mock.sentinel.link
        sp_album = spotify.ffi.new('int *')
        album = spotify.Album(sp_album)

        result = album.link

        link_mock.assert_called_once_with(album)
        self.assertEqual(result, mock.sentinel.link)


class AlbumTypeTest(unittest.TestCase):

    def test_has_constants(self):
        self.assertEqual(spotify.AlbumType.ALBUM, 0)
        self.assertEqual(spotify.AlbumType.SINGLE, 1)
