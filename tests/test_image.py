from __future__ import unicode_literals

import gc
import mock
import unittest

import spotify


@mock.patch('spotify.image.lib', spec=spotify.lib)
class ImageTest(unittest.TestCase):

    def test_adds_ref_to_sp_image_when_created(self, lib_mock):
        sp_image = spotify.ffi.new('int *')

        spotify.Image(sp_image)

        lib_mock.sp_image_add_ref.assert_called_with(sp_image)

    def test_releases_sp_image_when_image_dies(self, lib_mock):
        sp_image = spotify.ffi.new('int *')

        image = spotify.Image(sp_image)
        image = None  # noqa
        gc.collect()  # Needed for PyPy

        lib_mock.sp_image_release.assert_called_with(sp_image)

    def test_is_loaded(self, lib_mock):
        lib_mock.sp_image_is_loaded.return_value = 1
        sp_image = spotify.ffi.new('int *')
        image = spotify.Image(sp_image)

        result = image.is_loaded

        lib_mock.sp_image_is_loaded.assert_called_once_with(sp_image)
        self.assertTrue(result)

    def test_error(self, lib_mock):
        lib_mock.sp_image_error.return_value = int(
            spotify.ErrorType.IS_LOADING)
        sp_image = spotify.ffi.new('int *')
        image = spotify.Image(sp_image)

        result = image.error

        lib_mock.sp_image_error.assert_called_once_with(sp_image)
        self.assertIs(result, spotify.ErrorType.IS_LOADING)

    @mock.patch('spotify.image.load')
    def test_load(self, load_mock, lib_mock):
        sp_image = spotify.ffi.new('int *')
        image = spotify.Image(sp_image)

        image.load(10)

        load_mock.assert_called_with(image, timeout=10)

    @mock.patch('spotify.link.Link', spec=spotify.Link)
    def test_link_creates_link_to_image(self, link_mock, lib_mock):
        link_mock.return_value = mock.sentinel.link
        sp_image = spotify.ffi.new('int *')
        image = spotify.Image(sp_image)

        result = image.link

        link_mock.assert_called_once_with(image)
        self.assertEqual(result, mock.sentinel.link)


class ImageSizeTest(unittest.TestCase):

    def test_has_size_constants(self):
        self.assertEqual(spotify.ImageSize.NORMAL, 0)
        self.assertEqual(spotify.ImageSize.SMALL, 1)
        self.assertEqual(spotify.ImageSize.LARGE, 2)
