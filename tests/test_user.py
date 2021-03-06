from __future__ import unicode_literals

import unittest

import spotify
import tests
from tests import mock


@mock.patch("spotify.user.lib", spec=spotify.lib)
class UserTest(unittest.TestCase):
    def setUp(self):
        self.session = tests.create_session_mock()

    def test_create_without_uri_or_sp_user_fails(self, lib_mock):
        with self.assertRaises(AssertionError):
            spotify.User(self.session)

    @mock.patch("spotify.Link", spec=spotify.Link)
    def test_create_from_uri(self, link_mock, lib_mock):
        sp_user = spotify.ffi.cast("sp_user *", 42)
        link_instance_mock = link_mock.return_value
        link_instance_mock.as_user.return_value = spotify.User(
            self.session, sp_user=sp_user
        )
        uri = "spotify:user:foo"

        result = spotify.User(self.session, uri=uri)

        link_mock.assert_called_with(self.session, uri=uri)
        link_instance_mock.as_user.assert_called_with()
        lib_mock.sp_user_add_ref.assert_called_with(sp_user)
        self.assertEqual(result._sp_user, sp_user)

    @mock.patch("spotify.Link", spec=spotify.Link)
    def test_create_from_uri_fail_raises_error(self, link_mock, lib_mock):
        link_instance_mock = link_mock.return_value
        link_instance_mock.as_user.return_value = None
        uri = "spotify:user:foo"

        with self.assertRaises(ValueError):
            spotify.User(self.session, uri=uri)

    def test_adds_ref_to_sp_user_when_created(self, lib_mock):
        sp_user = spotify.ffi.cast("sp_user *", 42)

        spotify.User(self.session, sp_user=sp_user)

        lib_mock.sp_user_add_ref.assert_called_once_with(sp_user)

    def test_releases_sp_user_when_user_dies(self, lib_mock):
        sp_user = spotify.ffi.cast("sp_user *", 42)

        user = spotify.User(self.session, sp_user=sp_user)
        user = None  # noqa
        tests.gc_collect()

        lib_mock.sp_user_release.assert_called_with(sp_user)

    @mock.patch("spotify.Link", spec=spotify.Link)
    def test_repr(self, link_mock, lib_mock):
        link_instance_mock = link_mock.return_value
        link_instance_mock.uri = "foo"
        sp_user = spotify.ffi.cast("sp_user *", 42)
        user = spotify.User(self.session, sp_user=sp_user)

        result = repr(user)

        self.assertEqual(result, "User(%r)" % "foo")

    def test_canonical_name(self, lib_mock):
        lib_mock.sp_user_canonical_name.return_value = spotify.ffi.new(
            "char[]", b"alicefoobar"
        )
        sp_user = spotify.ffi.cast("sp_user *", 42)
        user = spotify.User(self.session, sp_user=sp_user)

        result = user.canonical_name

        lib_mock.sp_user_canonical_name.assert_called_once_with(sp_user)
        self.assertEqual(result, "alicefoobar")

    def test_display_name(self, lib_mock):
        lib_mock.sp_user_display_name.return_value = spotify.ffi.new(
            "char[]", b"Alice Foobar"
        )
        sp_user = spotify.ffi.cast("sp_user *", 42)
        user = spotify.User(self.session, sp_user=sp_user)

        result = user.display_name

        lib_mock.sp_user_display_name.assert_called_once_with(sp_user)
        self.assertEqual(result, "Alice Foobar")

    def test_is_loaded(self, lib_mock):
        lib_mock.sp_user_is_loaded.return_value = 1
        sp_user = spotify.ffi.cast("sp_user *", 42)
        user = spotify.User(self.session, sp_user=sp_user)

        result = user.is_loaded

        lib_mock.sp_user_is_loaded.assert_called_once_with(sp_user)
        self.assertTrue(result)

    @mock.patch("spotify.utils.load")
    def test_load(self, load_mock, lib_mock):
        sp_user = spotify.ffi.cast("sp_user *", 42)
        user = spotify.User(self.session, sp_user=sp_user)

        user.load(10)

        load_mock.assert_called_with(self.session, user, timeout=10)

    @mock.patch("spotify.Link", spec=spotify.Link)
    def test_link_creates_link_to_user(self, link_mock, lib_mock):
        sp_user = spotify.ffi.cast("sp_user *", 42)
        user = spotify.User(self.session, sp_user=sp_user)
        sp_link = spotify.ffi.cast("sp_link *", 43)
        lib_mock.sp_link_create_from_user.return_value = sp_link
        link_mock.return_value = mock.sentinel.link

        result = user.link

        link_mock.assert_called_once_with(self.session, sp_link=sp_link, add_ref=False)
        self.assertEqual(result, mock.sentinel.link)

    def test_starred(self, lib_mock):
        self.session.get_starred.return_value = mock.sentinel.playlist
        lib_mock.sp_user_canonical_name.return_value = spotify.ffi.new(
            "char[]", b"alice"
        )
        sp_user = spotify.ffi.cast("sp_user *", 42)
        user = spotify.User(self.session, sp_user=sp_user)

        result = user.starred

        self.session.get_starred.assert_called_with("alice")
        self.assertEqual(result, mock.sentinel.playlist)

    def test_published_playlists(self, lib_mock):
        self.session.get_published_playlists.return_value = (
            mock.sentinel.playlist_container
        )
        lib_mock.sp_user_canonical_name.return_value = spotify.ffi.new(
            "char[]", b"alice"
        )
        sp_user = spotify.ffi.cast("sp_user *", 42)
        user = spotify.User(self.session, sp_user=sp_user)

        result = user.published_playlists

        self.session.get_published_playlists.assert_called_with("alice")
        self.assertEqual(result, mock.sentinel.playlist_container)
