from __future__ import unicode_literals

import gc
import mock
import unittest

import spotify


@mock.patch('spotify.image.lib', spec=spotify.lib)
class ImageTest(unittest.TestCase):

    def create_session(self, lib_mock):
        session = mock.sentinel.session
        session._sp_session = mock.sentinel.sp_session
        spotify.session_instance = session
        return session

    def tearDown(self):
        spotify.session_instance = None

    def test_create_without_uri_or_sp_image_fails(self, lib_mock):
        self.assertRaises(AssertionError, spotify.Image)

    @mock.patch('spotify.Link')
    def test_create_from_uri(self, link_mock, lib_mock):
        session = self.create_session(lib_mock)
        sp_link = spotify.ffi.new('int *')
        link_instance_mock = link_mock.return_value
        link_instance_mock._sp_link = sp_link
        sp_image = spotify.ffi.new('int *')
        lib_mock.sp_image_create_from_link.return_value = sp_image
        uri = 'spotify:image:foo'

        result = spotify.Image(uri)

        link_mock.assert_called_with(uri)
        lib_mock.sp_image_create_from_link.assert_called_with(
            session._sp_session, sp_link)
        self.assertEqual(lib_mock.sp_image_add_ref.call_count, 0)
        self.assertEqual(result._sp_image, sp_image)

    @mock.patch('spotify.Link')
    def test_create_from_uri_fail_raises_error(self, link_mock, lib_mock):
        self.create_session(lib_mock)
        sp_link = spotify.ffi.new('int *')
        link_instance_mock = link_mock.return_value
        link_instance_mock._sp_link = sp_link
        lib_mock.sp_image_create_from_link.return_value = spotify.ffi.NULL
        uri = 'spotify:image:foo'

        self.assertRaises(ValueError, spotify.Image, uri)

    def test_adds_ref_to_sp_image_when_created(self, lib_mock):
        sp_image = spotify.ffi.new('int *')

        spotify.Image(sp_image=sp_image)

        lib_mock.sp_image_add_ref.assert_called_with(sp_image)

    def test_releases_sp_image_when_image_dies(self, lib_mock):
        sp_image = spotify.ffi.new('int *')

        image = spotify.Image(sp_image=sp_image)
        image = None  # noqa
        gc.collect()  # Needed for PyPy

        lib_mock.sp_image_release.assert_called_with(sp_image)

    def test_is_loaded(self, lib_mock):
        lib_mock.sp_image_is_loaded.return_value = 1
        sp_image = spotify.ffi.new('int *')
        image = spotify.Image(sp_image=sp_image)

        result = image.is_loaded

        lib_mock.sp_image_is_loaded.assert_called_once_with(sp_image)
        self.assertTrue(result)

    def test_error(self, lib_mock):
        lib_mock.sp_image_error.return_value = int(
            spotify.ErrorType.IS_LOADING)
        sp_image = spotify.ffi.new('int *')
        image = spotify.Image(sp_image=sp_image)

        result = image.error

        lib_mock.sp_image_error.assert_called_once_with(sp_image)
        self.assertIs(result, spotify.ErrorType.IS_LOADING)

    @mock.patch('spotify.utils.load')
    def test_load(self, load_mock, lib_mock):
        sp_image = spotify.ffi.new('int *')
        image = spotify.Image(sp_image=sp_image)

        image.load(10)

        load_mock.assert_called_with(image, timeout=10)

    def test_format(self, lib_mock):
        lib_mock.sp_image_is_loaded.return_value = 1
        lib_mock.sp_image_format.return_value = int(spotify.ImageFormat.JPEG)
        sp_image = spotify.ffi.new('int *')
        image = spotify.Image(sp_image=sp_image)

        result = image.format

        lib_mock.sp_image_format.assert_called_with(sp_image)
        self.assertIs(result, spotify.ImageFormat.JPEG)

    def test_format_is_none_if_unloaded(self, lib_mock):
        lib_mock.sp_image_is_loaded.return_value = 0
        sp_image = spotify.ffi.new('int *')
        image = spotify.Image(sp_image=sp_image)

        result = image.format

        lib_mock.sp_image_is_loaded.assert_called_with(sp_image)
        self.assertIsNone(result)

    def test_data(self, lib_mock):
        lib_mock.sp_image_is_loaded.return_value = 1

        def func(sp_image_ptr, data_size_ptr):
            size = 20
            data = spotify.ffi.new('char[]', size)
            data[0:3] = [b'a', b'b', b'c']
            data_void_ptr = spotify.ffi.cast('void *', data)
            data_size_ptr[0] = size
            return data_void_ptr

        lib_mock.sp_image_data.side_effect = func
        sp_image = spotify.ffi.new('int *')
        image = spotify.Image(sp_image=sp_image)

        result = image.data

        lib_mock.sp_image_data.assert_called_with(sp_image, mock.ANY)
        self.assertEqual(result[:5], b'abc\x00\x00')

    def test_data_is_none_if_unloaded(self, lib_mock):
        lib_mock.sp_image_is_loaded.return_value = 0
        sp_image = spotify.ffi.new('int *')
        image = spotify.Image(sp_image=sp_image)

        result = image.data

        lib_mock.sp_image_is_loaded.assert_called_with(sp_image)
        self.assertIsNone(result)

    def test_data_uri(self, lib_mock):
        lib_mock.sp_image_format.return_value = int(spotify.ImageFormat.JPEG)
        sp_image = spotify.ffi.new('int *')

        prop_mock = mock.PropertyMock()
        with mock.patch.object(spotify.Image, 'data', prop_mock):
            image = spotify.Image(sp_image=sp_image)
            prop_mock.return_value = b'01234\x006789'

            result = image.data_uri

        self.assertEqual(result, 'data:image/jpeg;base64,MDEyMzQANjc4OQ==')

    def test_data_uri_is_none_if_unloaded(self, lib_mock):
        lib_mock.sp_image_is_loaded.return_value = 0
        sp_image = spotify.ffi.new('int *')
        image = spotify.Image(sp_image=sp_image)

        result = image.data_uri

        self.assertIsNone(result)

    def test_data_uri_fails_if_unknown_image_format(self, lib_mock):
        sp_image = spotify.ffi.new('int *')
        image = spotify.Image(sp_image=sp_image)
        image.__dict__['format'] = mock.Mock(
            return_value=spotify.ImageFormat.UNKNOWN)
        image.__dict__['data'] = mock.Mock(return_value=b'01234\x006789')

        self.assertRaises(ValueError, lambda: image.data_uri)

    @mock.patch('spotify.link.Link', spec=spotify.Link)
    def test_link_creates_link_to_image(self, link_mock, lib_mock):
        link_mock.return_value = mock.sentinel.link
        sp_image = spotify.ffi.new('int *')
        image = spotify.Image(sp_image=sp_image)

        result = image.link

        link_mock.assert_called_once_with(image)
        self.assertEqual(result, mock.sentinel.link)


class ImageFormatTest(unittest.TestCase):

    def test_has_constants(self):
        self.assertEqual(spotify.ImageFormat.UNKNOWN, -1)
        self.assertEqual(spotify.ImageFormat.JPEG, 0)


class ImageSizeTest(unittest.TestCase):

    def test_has_size_constants(self):
        self.assertEqual(spotify.ImageSize.NORMAL, 0)
        self.assertEqual(spotify.ImageSize.SMALL, 1)
        self.assertEqual(spotify.ImageSize.LARGE, 2)
