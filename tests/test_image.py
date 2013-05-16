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

    @mock.patch('spotify.link.Link', spec=spotify.Link)
    def test_as_link_creates_link_to_image(self, link_mock, lib_mock):
        link_mock.return_value = mock.sentinel.link
        sp_image = spotify.ffi.new('int *')
        image = spotify.Image(sp_image)

        result = image.as_link()

        link_mock.assert_called_once_with(image)
        self.assertEqual(result, mock.sentinel.link)


class ImageSizeTest(unittest.TestCase):

    def test_has_size_constants(self):
        self.assertEqual(spotify.ImageSize.NORMAL, 0)
        self.assertEqual(spotify.ImageSize.SMALL, 1)
        self.assertEqual(spotify.ImageSize.LARGE, 2)
