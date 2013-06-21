from __future__ import unicode_literals

import gc
import mock
import unittest

import spotify


@mock.patch('spotify.artist.lib', spec=spotify.lib)
class ArtistTest(unittest.TestCase):

    def create_session(self, lib_mock):
        session = mock.sentinel.session
        session._sp_session = mock.sentinel.sp_session
        spotify.session_instance = session
        return session

    def tearDown(self):
        spotify.session_instance = None

    def test_create_without_uri_or_sp_artist_fails(self, lib_mock):
        self.assertRaises(AssertionError, spotify.Artist)

    @mock.patch('spotify.Link', spec=spotify.Link)
    def test_create_from_uri(self, link_mock, lib_mock):
        self.create_session(lib_mock)
        sp_link = spotify.ffi.new('int *')
        link_instance_mock = link_mock.return_value
        link_instance_mock._sp_link = sp_link
        sp_artist = spotify.ffi.new('int *')
        lib_mock.sp_link_as_artist.return_value = sp_artist
        uri = 'spotify:artist:foo'

        result = spotify.Artist(uri)

        link_mock.assert_called_with(uri)
        lib_mock.sp_link_as_artist.assert_called_with(sp_link)
        lib_mock.sp_artist_add_ref.assert_called_with(sp_artist)
        self.assertEqual(result._sp_artist, sp_artist)

    @mock.patch('spotify.Link', spec=spotify.Link)
    def test_create_from_uri_fail_raises_error(self, link_mock, lib_mock):
        self.create_session(lib_mock)
        sp_link = spotify.ffi.new('int *')
        link_instance_mock = link_mock.return_value
        link_instance_mock._sp_link = sp_link
        lib_mock.sp_link_as_artist.return_value = spotify.ffi.NULL
        uri = 'spotify:artist:foo'

        self.assertRaises(ValueError, spotify.Artist, uri)

    def test_adds_ref_to_sp_artist_when_created(self, lib_mock):
        sp_artist = spotify.ffi.new('int *')

        spotify.Artist(sp_artist=sp_artist)

        lib_mock.sp_artist_add_ref.assert_called_with(sp_artist)

    def test_releases_sp_artist_when_artist_dies(self, lib_mock):
        sp_artist = spotify.ffi.new('int *')

        artist = spotify.Artist(sp_artist=sp_artist)
        artist = None  # noqa
        gc.collect()  # Needed for PyPy

        lib_mock.sp_artist_release.assert_called_with(sp_artist)

    def test_name(self, lib_mock):
        lib_mock.sp_artist_name.return_value = spotify.ffi.new(
            'char[]', b'Foo Bar Baz')
        sp_artist = spotify.ffi.new('int *')
        artist = spotify.Artist(sp_artist=sp_artist)

        result = artist.name

        lib_mock.sp_artist_name.assert_called_once_with(sp_artist)
        self.assertEqual(result, 'Foo Bar Baz')

    def test_name_is_none_if_unloaded(self, lib_mock):
        lib_mock.sp_artist_name.return_value = spotify.ffi.new('char[]', b'')
        sp_artist = spotify.ffi.new('int *')
        artist = spotify.Artist(sp_artist=sp_artist)

        result = artist.name

        lib_mock.sp_artist_name.assert_called_once_with(sp_artist)
        self.assertIsNone(result)

    def test_is_loaded(self, lib_mock):
        lib_mock.sp_artist_is_loaded.return_value = 1
        sp_artist = spotify.ffi.new('int *')
        artist = spotify.Artist(sp_artist=sp_artist)

        result = artist.is_loaded

        lib_mock.sp_artist_is_loaded.assert_called_once_with(sp_artist)
        self.assertTrue(result)

    @mock.patch('spotify.utils.load')
    def test_load(self, load_mock, lib_mock):
        sp_artist = spotify.ffi.new('int *')
        artist = spotify.Artist(sp_artist=sp_artist)

        artist.load(10)

        load_mock.assert_called_with(artist, timeout=10)

    @mock.patch('spotify.image.lib', spec=spotify.lib)
    def test_portrait(self, image_lib_mock, lib_mock):
        session = self.create_session(lib_mock)
        sp_image_id = spotify.ffi.new('char[]', b'portrait-id')
        lib_mock.sp_artist_portrait.return_value = sp_image_id
        sp_image = spotify.ffi.new('int *')
        lib_mock.sp_image_create.return_value = sp_image
        sp_artist = spotify.ffi.new('int *')
        artist = spotify.Artist(sp_artist=sp_artist)
        image_size = spotify.ImageSize.SMALL

        result = artist.portrait(image_size)

        lib_mock.sp_artist_portrait.assert_called_with(
            sp_artist, int(image_size))
        lib_mock.sp_image_create.assert_called_with(
            session._sp_session, sp_image_id)

        self.assertIsInstance(result, spotify.Image)
        self.assertEqual(result._sp_image, sp_image)

        # Since we *created* the sp_image, we already have a refcount of 1 and
        # shouldn't increase the refcount when wrapping this sp_image in an
        # Image object
        self.assertEqual(image_lib_mock.sp_image_add_ref.call_count, 0)

    def test_portrait_is_none_if_null(self, lib_mock):
        lib_mock.sp_artist_portrait.return_value = spotify.ffi.NULL
        sp_artist = spotify.ffi.new('int *')
        artist = spotify.Artist(sp_artist=sp_artist)

        result = artist.portrait()

        lib_mock.sp_artist_portrait.assert_called_with(
            sp_artist, int(spotify.ImageSize.NORMAL))
        self.assertIsNone(result)

    @mock.patch('spotify.Link', spec=spotify.Link)
    def test_link_creates_link_to_artist(self, link_mock, lib_mock):
        link_mock.return_value = mock.sentinel.link
        sp_artist = spotify.ffi.new('int *')
        artist = spotify.Artist(sp_artist=sp_artist)

        result = artist.link

        link_mock.assert_called_once_with(artist)
        self.assertEqual(result, mock.sentinel.link)
