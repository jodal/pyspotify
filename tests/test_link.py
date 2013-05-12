from __future__ import unicode_literals

import gc
import mock
import unittest

import spotify


@mock.patch('spotify.link.lib')
class LinkTest(unittest.TestCase):

    def setUp(self):
        spotify.session_instance = mock.sentinel.session

    def tearDown(self):
        spotify.session_instance = None

    def test_create_from_string(self, lib_mock):
        sp_link = spotify.ffi.new('int *')
        lib_mock.sp_link_create_from_string.return_value = sp_link

        spotify.Link('spotify:track:foo')

        lib_mock.sp_link_create_from_string.assert_called_once_with(
            mock.ANY)
        self.assertEqual(
            spotify.ffi.string(
                lib_mock.sp_link_create_from_string.call_args[0][0]),
            b'spotify:track:foo')

    def test_raises_error_if_session_doesnt_exist(self, lib_mock):
        spotify.session_instance = None

        self.assertRaises(RuntimeError, spotify.Link, 'spotify:track:foo')

    def test_raises_error_if_string_isnt_parseable(self, lib_mock):
        lib_mock.sp_link_create_from_string.return_value = spotify.ffi.NULL

        self.assertRaises(ValueError, spotify.Link, 'invalid link string')

    def test_releases_sp_link_when_link_dies(self, lib_mock):
        sp_link = spotify.ffi.new('int *')
        lib_mock.sp_link_create_from_string.return_value = sp_link

        link = spotify.Link('spotify:track:foo')
        link = None  # noqa
        gc.collect()  # Needed for PyPy

        lib_mock.sp_link_release.assert_called_with(sp_link)

    def test_str_grows_buffer_to_fit_link(self, lib_mock):
        sp_link = spotify.ffi.new('int *')
        lib_mock.sp_link_create_from_string.return_value = sp_link
        string = 'foo' * 100

        def func(sp_link, buffer_, buffer_size):
            # -1 to keep a char free for \0 terminating the string
            length = min(len(string), buffer_size - 1)
            # Due to Python 3 treating bytes as an array of ints, we have to
            # encode and copy chars one by one.
            for i in range(length):
                buffer_[i] = string[i].encode('utf-8')
            return len(string)

        lib_mock.sp_link_as_string.side_effect = func
        link = spotify.Link(string)

        result = str(link)

        lib_mock.sp_link_as_string.assert_called_with(
            sp_link, mock.ANY, mock.ANY)
        self.assertEqual(result, string)
