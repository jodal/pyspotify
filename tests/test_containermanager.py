#
# Copyright 2011 Antoine Pierlot-Garcin
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
from spotify._mockspotify import mock_playlist, mock_event_trigger
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
        self.playlist = mock_playlist('foo_', [])
        self.container = mock_playlistcontainer([])

    def test_container_loaded(self):
        global callback_called
        callback = self.manager.container_loaded
        self.container.add_loaded_callback(callback, self.manager)
        mock_event_trigger(7, self.container)

        self.assertNotEqual(callback_called, None)
        name, args = callback_called
        self.assertEqual(name, "container_loaded")
        self.assertEqual(len(args), 3)
        self.assertEqual(args[0], self.manager)
        self.assertEqual(type(args[1]), type(self.container))

    def test_playlist_added(self):
        global callback_called
        callback = self.manager.playlist_added
        self.container.add_playlist_added_callback(callback, self.manager)
        mock_event_trigger(8, self.container)

        self.assertNotEqual(callback_called, None)
        name, args = callback_called
        self.assertEqual(name, "playlist_added")
        self.assertEqual(len(args), 5)
        self.assertEqual(args[0], self.manager)
        self.assertEqual(type(args[1]), type(self.container))
        self.assertEqual(type(args[2]), type(self.playlist))
        self.assertEqual(args[2].name(), 'foo')
        self.assertEqual(type(args[3]), int)

    def test_playlist_moved(self):
        global callback_called
        callback = self.manager.playlist_moved
        self.container.add_playlist_moved_callback(callback, self.manager)
        mock_event_trigger(9, self.container)

        self.assertNotEqual(callback_called, None)
        name, args = callback_called
        self.assertEqual(name, "playlist_moved")
        self.assertEqual(len(args), 6)
        self.assertEqual(args[0], self.manager)
        self.assertEqual(type(args[1]), type(self.container))
        self.assertEqual(type(args[2]), type(self.playlist))
        self.assertEqual(args[2].name(), 'foo')
        self.assertEqual(type(args[3]), int)
        self.assertEqual(type(args[4]), int)

    def test_playlist_removed(self):
        global callback_called
        callback = self.manager.playlist_removed
        self.container.add_playlist_removed_callback(callback, self.manager)
        mock_event_trigger(10, self.container)

        self.assertNotEqual(callback_called, None)
        name, args = callback_called
        self.assertEqual(name, "playlist_removed")
        self.assertEqual(len(args), 5)
        self.assertEqual(args[0], self.manager)
        self.assertEqual(type(args[1]), type(self.container))
        self.assertEqual(type(args[2]), type(self.playlist))
        self.assertEqual(args[2].name(), 'foo')
        self.assertEqual(type(args[3]), int)
