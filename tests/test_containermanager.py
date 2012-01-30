import unittest
from spotify._mockspotify import mock_playlist, mock_event_trigger, mock_user
from spotify._mockspotify import mock_playlistcontainer
from spotify.manager import SpotifyContainerManager
import spotify

callback_called = None

class MyContainerManager(SpotifyContainerManager):

    def container_loaded(*args):
        global callback_called
        callback_called = 'container_loaded', args

    def playlist_added(*args):
        global callback_called
        callback_called = 'playlist_added', args

    def playlist_moved(*args):
        global callback_called
        callback_called = 'playlist_moved', args

    def playlist_removed(*args):
        global callback_called
        callback_called = 'playlist_removed', args


class TestPlaylistManager(unittest.TestCase):

    def setUp(self):
        self.manager = MyContainerManager()
        self.container = mock_playlistcontainer(mock_user('user'), [])

    def test_container_loaded(self):
        global callback_called
        callback = self.manager.container_loaded
        self.container.add_loaded_callback(callback, self.manager)
        mock_event_trigger(40, self.container)

        self.assertNotEqual(callback_called, None)
        name, args = callback_called
        self.assertEqual(name, "container_loaded")
        self.assertEqual(len(args), 3)
        self.assertEqual(args[0], self.manager)
        self.assertEqual(type(args[1]), spotify._mockspotify.PlaylistContainer)

    def test_playlist_added(self):
        global callback_called
        callback = self.manager.playlist_added
        self.container.add_playlist_added_callback(callback, self.manager)
        mock_event_trigger(41, self.container)

        self.assertNotEqual(callback_called, None)
        name, args = callback_called
        self.assertEqual(name, "playlist_added")
        self.assertEqual(len(args), 5)
        self.assertEqual(args[0], self.manager)
        self.assertEqual(type(args[1]), spotify._mockspotify.PlaylistContainer)
        self.assertEqual(type(args[2]), spotify._mockspotify.Playlist)
        self.assertEqual(args[2].name(), 'P')
        self.assertEqual(type(args[3]), int)

    def test_playlist_moved(self):
        global callback_called
        callback = self.manager.playlist_moved
        self.container.add_playlist_moved_callback(callback, self.manager)
        mock_event_trigger(42, self.container)

        self.assertNotEqual(callback_called, None)
        name, args = callback_called
        self.assertEqual(name, "playlist_moved")
        self.assertEqual(len(args), 6)
        self.assertEqual(args[0], self.manager)
        self.assertEqual(type(args[1]), spotify._mockspotify.PlaylistContainer)
        self.assertEqual(type(args[2]), spotify._mockspotify.Playlist)
        self.assertEqual(args[2].name(), 'P')
        self.assertEqual(type(args[3]), int)
        self.assertEqual(type(args[4]), int)

    def test_playlist_removed(self):
        global callback_called
        callback = self.manager.playlist_removed
        self.container.add_playlist_removed_callback(callback, self.manager)
        mock_event_trigger(43, self.container)

        self.assertNotEqual(callback_called, None)
        name, args = callback_called
        self.assertEqual(name, "playlist_removed")
        self.assertEqual(len(args), 5)
        self.assertEqual(args[0], self.manager)
        self.assertEqual(type(args[1]), spotify._mockspotify.PlaylistContainer)
        self.assertEqual(type(args[2]), spotify._mockspotify.Playlist)
        self.assertEqual(args[2].name(), 'P')
        self.assertEqual(type(args[3]), int)
