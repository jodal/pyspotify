from __future__ import unicode_literals

import gc
import mock
import unittest

import spotify


@mock.patch('spotify.user.lib')
class UserTest(unittest.TestCase):

    def test_adds_ref_to_sp_user_when_created(self, lib_mock):
        sp_user = spotify.ffi.new('int *')

        spotify.User(sp_user)

        lib_mock.sp_user_add_ref.assert_called_once_with(sp_user)

    def test_releases_sp_user_when_user_dies(self, lib_mock):
        sp_user = spotify.ffi.new('int *')

        user = spotify.User(sp_user)
        user = None  # noqa
        gc.collect()  # Needed for PyPy

        lib_mock.sp_user_release.assert_called_with(sp_user)

    def test_canonical_name(self, lib_mock):
        lib_mock.sp_user_canonical_name.return_value = spotify.ffi.new(
            'char[]', b'alicefoobar')
        sp_user = spotify.ffi.new('int *')
        user = spotify.User(sp_user)

        result = user.canonical_name

        lib_mock.sp_user_canonical_name.assert_called_once_with(sp_user)
        self.assertEqual(result, 'alicefoobar')

    def test_display_name(self, lib_mock):
        lib_mock.sp_user_display_name.return_value = spotify.ffi.new(
            'char[]', b'Alice Foobar')
        sp_user = spotify.ffi.new('int *')
        user = spotify.User(sp_user)

        result = user.display_name

        lib_mock.sp_user_display_name.assert_called_once_with(sp_user)
        self.assertEqual(result, 'Alice Foobar')

    def test_is_loaded(self, lib_mock):
        lib_mock.sp_user_is_loaded.return_value = 1
        sp_user = spotify.ffi.new('int *')
        user = spotify.User(sp_user)

        result = user.is_loaded

        lib_mock.sp_user_is_loaded.assert_called_once_with(sp_user)
        self.assertTrue(result)

    @mock.patch('spotify.link.Link')
    def test_as_link_creates_link_to_user(self, link_mock, lib_mock):
        link_mock.return_value = mock.sentinel.link
        sp_user = spotify.ffi.new('int *')
        user = spotify.User(sp_user)

        result = user.as_link()

        link_mock.assert_called_once_with(user)
        self.assertEqual(result, mock.sentinel.link)
