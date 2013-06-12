from __future__ import unicode_literals

import gc
import mock
import unittest

import spotify


@mock.patch('spotify.user.lib', spec=spotify.lib)
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

    @mock.patch('spotify.utils.load')
    def test_load(self, load_mock, lib_mock):
        sp_user = spotify.ffi.new('int *')
        user = spotify.User(sp_user)

        user.load(10)

        load_mock.assert_called_with(user, timeout=10)

    @mock.patch('spotify.link.Link', spec=spotify.Link)
    def test_link_creates_link_to_user(self, link_mock, lib_mock):
        link_mock.return_value = mock.sentinel.link
        sp_user = spotify.ffi.new('int *')
        user = spotify.User(sp_user)

        result = user.link

        link_mock.assert_called_once_with(user)
        self.assertEqual(result, mock.sentinel.link)

    @mock.patch('spotify.session_instance', spec=spotify.Session)
    def test_starred(self, session_mock, lib_mock):
        session_mock.starred_for_user.return_value = mock.sentinel.playlist
        lib_mock.sp_user_canonical_name.return_value = spotify.ffi.new(
            'char[]', b'alice')
        sp_user = spotify.ffi.new('int *')
        user = spotify.User(sp_user)

        result = user.starred

        session_mock.starred_for_user.assert_called_with('alice')
        self.assertEqual(result, mock.sentinel.playlist)

    def test_starred_if_no_session(self, lib_mock):
        spotify.session_instance = None
        lib_mock.sp_user_canonical_name.return_value = spotify.ffi.new(
            'char[]', b'alice')
        sp_user = spotify.ffi.new('int *')
        user = spotify.User(sp_user)

        result = user.starred

        self.assertIsNone(result)

    @mock.patch('spotify.session_instance', spec=spotify.Session)
    def test_published_container(self, session_mock, lib_mock):
        session_mock.published_container_for_user.return_value = (
            mock.sentinel.playlist_container)
        lib_mock.sp_user_canonical_name.return_value = spotify.ffi.new(
            'char[]', b'alice')
        sp_user = spotify.ffi.new('int *')
        user = spotify.User(sp_user)

        result = user.published_container

        session_mock.published_container_for_user.assert_called_with('alice')
        self.assertEqual(result, mock.sentinel.playlist_container)

    def test_published_container_if_no_session(self, lib_mock):
        spotify.session_instance = None
        lib_mock.sp_user_canonical_name.return_value = spotify.ffi.new(
            'char[]', b'alice')
        sp_user = spotify.ffi.new('int *')
        user = spotify.User(sp_user)

        result = user.published_container

        self.assertIsNone(result)
