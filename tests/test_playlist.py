from __future__ import unicode_literals

import gc
import mock
import unittest

import spotify


@mock.patch('spotify.playlist.lib', spec=spotify.lib)
class PlaylistTest(unittest.TestCase):

    def create_session(self, lib_mock):
        session = mock.sentinel.session
        session._sp_session = mock.sentinel.sp_session
        spotify.session_instance = session
        return session

    def tearDown(self):
        spotify.session_instance = None

    def test_create_without_uri_or_sp_playlist_fails(self, lib_mock):
        self.assertRaises(AssertionError, spotify.Playlist)

    @mock.patch('spotify.Link', spec=spotify.Link)
    def test_create_from_uri(self, link_mock, lib_mock):
        session = self.create_session(lib_mock)
        sp_link = spotify.ffi.new('int *')
        link_instance_mock = link_mock.return_value
        link_instance_mock._sp_link = sp_link
        sp_playlist = spotify.ffi.new('int *')
        lib_mock.sp_playlist_create.return_value = sp_playlist
        uri = 'spotify:playlist:foo'

        result = spotify.Playlist(uri)

        link_mock.assert_called_with(uri)
        lib_mock.sp_playlist_create.assert_called_with(
            session._sp_session, sp_link)
        self.assertEqual(lib_mock.sp_playlist_add_ref.call_count, 0)
        self.assertEqual(result._sp_playlist, sp_playlist)

    @mock.patch('spotify.Link', spec=spotify.Link)
    def test_create_from_uri_fail_raises_error(self, link_mock, lib_mock):
        self.create_session(lib_mock)
        sp_link = spotify.ffi.new('int *')
        link_instance_mock = link_mock.return_value
        link_instance_mock._sp_link = sp_link
        lib_mock.sp_playlist_create.return_value = spotify.ffi.NULL
        uri = 'spotify:playlist:foo'

        self.assertRaises(ValueError, spotify.Playlist, uri)

    def test_adds_ref_to_sp_playlist_when_created(self, lib_mock):
        sp_playlist = spotify.ffi.new('int *')

        spotify.Playlist(sp_playlist=sp_playlist)

        lib_mock.sp_playlist_add_ref.assert_called_with(sp_playlist)

    def test_releases_sp_playlist_when_playlist_dies(self, lib_mock):
        sp_playlist = spotify.ffi.new('int *')

        playlist = spotify.Playlist(sp_playlist=sp_playlist)
        playlist = None  # noqa
        gc.collect()  # Needed for PyPy

        lib_mock.sp_playlist_release.assert_called_with(sp_playlist)

    def test_is_loaded(self, lib_mock):
        lib_mock.sp_playlist_is_loaded.return_value = 1
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        result = playlist.is_loaded

        lib_mock.sp_playlist_is_loaded.assert_called_once_with(sp_playlist)
        self.assertTrue(result)

    @mock.patch('spotify.utils.load')
    def test_load(self, load_mock, lib_mock):
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        playlist.load(10)

        load_mock.assert_called_with(playlist, timeout=10)

    def test_name(self, lib_mock):
        lib_mock.sp_playlist_name.return_value = spotify.ffi.new(
            'char[]', b'Foo Bar Baz')
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        result = playlist.name

        lib_mock.sp_playlist_name.assert_called_once_with(sp_playlist)
        self.assertEqual(result, 'Foo Bar Baz')

    def test_name_is_none_if_unloaded(self, lib_mock):
        lib_mock.sp_playlist_name.return_value = spotify.ffi.new('char[]', b'')
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        result = playlist.name

        lib_mock.sp_playlist_name.assert_called_once_with(sp_playlist)
        self.assertIsNone(result)

    def test_rename(self, lib_mock):
        lib_mock.sp_playlist_rename.return_value = int(spotify.ErrorType.OK)
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        playlist.rename('Quux')

        lib_mock.sp_playlist_rename.assert_called_with(sp_playlist, mock.ANY)
        self.assertEqual(
            spotify.ffi.string(lib_mock.sp_playlist_rename.call_args[0][1]),
            b'Quux')

    def test_rename_fails_if_error(self, lib_mock):
        lib_mock.sp_playlist_rename.return_value = int(
            spotify.ErrorType.BAD_API_VERSION)
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        self.assertRaises(spotify.Error, playlist.rename, 'Quux')

    def test_name_setter(self, lib_mock):
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)
        playlist.rename = mock.Mock()

        playlist.name = 'Quux'

        playlist.rename.assert_called_with('Quux')

    @mock.patch('spotify.user.lib', spec=spotify.lib)
    def test_owner(self, user_lib_mock, lib_mock):
        sp_user = spotify.ffi.new('int *')
        lib_mock.sp_playlist_owner.return_value = sp_user
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        result = playlist.owner

        lib_mock.sp_playlist_owner.assert_called_with(sp_playlist)
        self.assertIsInstance(result, spotify.User)
        self.assertEqual(result._sp_user, sp_user)
        user_lib_mock.sp_user_add_ref.assert_called_with(sp_user)

    @mock.patch('spotify.Link', spec=spotify.Link)
    def test_link_creates_link_to_playlist(self, link_mock, lib_mock):
        link_mock.return_value = mock.sentinel.link
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        result = playlist.link

        link_mock.assert_called_once_with(playlist)
        self.assertEqual(result, mock.sentinel.link)


@mock.patch('spotify.playlist.lib', spec=spotify.lib)
class PlaylistContainerTest(unittest.TestCase):

    def test_adds_ref_to_sp_playlistcontainer_when_created(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.new('int *')

        spotify.PlaylistContainer(sp_playlistcontainer)

        lib_mock.sp_playlistcontainer_add_ref.assert_called_with(
            sp_playlistcontainer)

    def test_releases_sp_playlistcontainer_when_container_dies(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.new('int *')

        playlist_container = spotify.PlaylistContainer(sp_playlistcontainer)
        playlist_container = None  # noqa
        gc.collect()  # Needed for PyPy

        lib_mock.sp_playlistcontainer_release.assert_called_with(
            sp_playlistcontainer)
