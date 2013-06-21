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
