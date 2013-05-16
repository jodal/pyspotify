from __future__ import unicode_literals

import gc
import mock
import unittest

import spotify


@mock.patch('spotify.playlist.lib')
class PlaylistTest(unittest.TestCase):

    def test_adds_ref_to_sp_playlist_when_created(self, lib_mock):
        sp_playlist = spotify.ffi.new('int *')

        spotify.Playlist(sp_playlist)

        lib_mock.sp_playlist_add_ref.assert_called_with(sp_playlist)

    def test_releases_sp_playlist_when_playlist_dies(self, lib_mock):
        sp_playlist = spotify.ffi.new('int *')

        playlist = spotify.Playlist(sp_playlist)
        playlist = None  # noqa
        gc.collect()  # Needed for PyPy

        lib_mock.sp_playlist_release.assert_called_with(sp_playlist)

    @mock.patch('spotify.link.Link')
    def test_as_link_creates_link_to_playlist(self, link_mock, lib_mock):
        link_mock.return_value = mock.sentinel.link
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist)

        result = playlist.as_link()

        link_mock.assert_called_once_with(playlist)
        self.assertEqual(result, mock.sentinel.link)


@mock.patch('spotify.playlist.lib')
class PlaylistContainerTest(unittest.TestCase):
    pass
