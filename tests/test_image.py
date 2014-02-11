from __future__ import unicode_literals

import mock
import unittest

import spotify
import tests


@mock.patch('spotify.image.lib', spec=spotify.lib)
class ImageTest(unittest.TestCase):

    def test_create_without_uri_or_sp_image_fails(self, lib_mock):
        with self.assertRaises(AssertionError):
            spotify.Image()

    @mock.patch('spotify.Link', spec=spotify.Link)
    def test_create_from_uri(self, link_mock, lib_mock):
        sp_image = spotify.ffi.new('int *')
        link_instance_mock = link_mock.return_value
        link_instance_mock.as_image.return_value = spotify.Image(
            sp_image=sp_image)
        lib_mock.sp_image_create_from_link.return_value = sp_image
        uri = 'spotify:image:foo'

        result = spotify.Image(uri)

        link_mock.assert_called_with(uri)
        link_instance_mock.as_image.assert_called_with()
        lib_mock.sp_image_add_ref.assert_called_with(sp_image)
        self.assertEqual(result._sp_image, sp_image)

    @mock.patch('spotify.Link', spec=spotify.Link)
    def test_create_from_uri_fail_raises_error(self, link_mock, lib_mock):
        link_instance_mock = link_mock.return_value
        link_instance_mock.as_image.return_value = None
        uri = 'spotify:image:foo'

        with self.assertRaises(ValueError):
            spotify.Image(uri)

    def test_adds_ref_to_sp_image_when_created(self, lib_mock):
        sp_image = spotify.ffi.new('int *')

        spotify.Image(sp_image=sp_image)

        lib_mock.sp_image_add_ref.assert_called_with(sp_image)

    def test_releases_sp_image_when_image_dies(self, lib_mock):
        sp_image = spotify.ffi.new('int *')

        image = spotify.Image(sp_image=sp_image)
        image = None  # noqa
        tests.gc_collect()

        lib_mock.sp_image_release.assert_called_with(sp_image)

    @mock.patch('spotify.Link', spec=spotify.Link)
    def test_repr(self, link_mock, lib_mock):
        link_instance_mock = link_mock.return_value
        link_instance_mock.uri = 'foo'
        sp_image = spotify.ffi.new('int *')
        image = spotify.Image(sp_image=sp_image)

        result = repr(image)

        self.assertEqual(result, 'Image(%r)' % 'foo')

    def test_load_event_is_unset_by_default(self, lib_mock):
        sp_image = spotify.ffi.new('int *')
        image = spotify.Image(sp_image=sp_image)

        self.assertFalse(image.load_event.is_set())

    def test_add_and_call_load_callback(self, lib_mock):
        lib_mock.sp_image_add_load_callback.return_value = int(
            spotify.ErrorType.OK)
        lib_mock.sp_image_remove_load_callback.return_value = int(
            spotify.ErrorType.OK)
        sp_image = spotify.ffi.cast('sp_image *', spotify.ffi.new('int *'))
        image = spotify.Image(sp_image=sp_image)
        callback = mock.Mock()

        # Add
        callback_handle = image.add_load_callback(callback)
        lib_mock.sp_image_add_load_callback.assert_called_with(
            sp_image, mock.ANY, callback_handle)
        image_load_cb = lib_mock.sp_image_add_load_callback.call_args[0][1]

        # Call
        self.assertEqual(callback.call_count, 0)
        image_load_cb(sp_image, callback_handle)
        self.assertEqual(callback.call_count, 1)

    def test_add_and_remove_load_callback(self, lib_mock):
        lib_mock.sp_image_add_load_callback.return_value = int(
            spotify.ErrorType.OK)
        lib_mock.sp_image_remove_load_callback.return_value = int(
            spotify.ErrorType.OK)
        sp_image = spotify.ffi.cast('sp_image *', spotify.ffi.new('int *'))
        image = spotify.Image(sp_image=sp_image)
        callback = mock.Mock()

        # Add
        callback_handle = image.add_load_callback(callback)
        lib_mock.sp_image_add_load_callback.assert_called_with(
            sp_image, mock.ANY, callback_handle)
        image_load_cb = lib_mock.sp_image_add_load_callback.call_args[0][1]

        # Remove
        image.remove_load_callback(callback_handle)
        lib_mock.sp_image_remove_load_callback.assert_called_with(
            sp_image, image_load_cb, callback_handle)

    def test_add_load_callback_fails_if_error(self, lib_mock):
        lib_mock.sp_image_add_load_callback.return_value = int(
            spotify.ErrorType.BAD_API_VERSION)
        sp_image = spotify.ffi.new('int *')
        image = spotify.Image(sp_image=sp_image)

        with self.assertRaises(spotify.Error):
            image.add_load_callback(None)

    def test_remove_load_callback_fails_if_error(self, lib_mock):
        lib_mock.sp_image_add_load_callback.return_value = int(
            spotify.ErrorType.OK)
        lib_mock.sp_image_remove_load_callback.return_value = int(
            spotify.ErrorType.BAD_API_VERSION)
        sp_image = spotify.ffi.new('int *')
        image = spotify.Image(sp_image=sp_image)
        callback_id = image.add_load_callback(None)

        with self.assertRaises(spotify.Error):
            image.remove_load_callback(callback_id)

    def test_remove_load_callback_fails_if_unknown_callback(self, lib_mock):
        sp_image = spotify.ffi.new('int *')
        image = spotify.Image(sp_image=sp_image)

        with self.assertRaises(LookupError):
            image.remove_load_callback(b'foo')

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

        with self.assertRaises(ValueError):
            image.data_uri

    @mock.patch('spotify.Link', spec=spotify.Link)
    def test_link_creates_link_to_image(self, link_mock, lib_mock):
        sp_image = spotify.ffi.new('int *')
        image = spotify.Image(sp_image=sp_image)
        sp_link = spotify.ffi.new('int *')
        lib_mock.sp_link_create_from_image.return_value = sp_link
        link_mock.return_value = mock.sentinel.link

        result = image.link

        link_mock.assert_called_once_with(sp_link=sp_link)
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
