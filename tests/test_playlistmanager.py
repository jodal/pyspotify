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
from spotify.manager import SpotifyPlaylistManager
import spotify

callback_called = None

class MyPlaylistManager(SpotifyPlaylistManager):

    def tracks_added(*args):
        global callback_called
        callback_called = 'tracks_added', args

    def tracks_moved(*args):
        global callback_called
        callback_called = 'tracks_moved', args

    def tracks_removed(*args):
        global callback_called
        callback_called = 'tracks_removed', args


class TestPlaylistManager(unittest.TestCase):

    def setUp(self):
        global callback_called
        self.manager = MyPlaylistManager()
        self.playlist = mock_playlist('foo_', [])
        callback_called = None

    def test_tracks_added(self):
        global callback_called
        callback = self.manager.tracks_added
        self.playlist.add_tracks_added_callback(callback, self.manager)
        mock_event_trigger(4, self.playlist)

        self.assertNotEqual(callback_called, None)
        name, args = callback_called
        self.assertEqual(name,"tracks_added")
        self.assertEqual(len(args), 5)
        self.assertEqual(args[0], self.manager)
        self.assertEqual(type(args[1]), type(self.playlist))
        self.assertEqual(args[1].name(), self.playlist.name())
        self.assertEqual(type(args[2]), list)
        self.assertEqual(len(args[2]), 3)
        self.assertEqual(map(lambda x: x.name(), args[2]), ['foo', 'bar', 'baz'])
        self.assertEqual(type(args[3]), int)

    def test_tracks_moved(self):
        global callback_called
        callback = self.manager.tracks_moved
        self.playlist.add_tracks_moved_callback(callback, self.manager)
        mock_event_trigger(5, self.playlist)

        self.assertNotEqual(callback_called, None)
        name, args = callback_called
        self.assertEqual(name, "tracks_moved")
        self.assertEqual(len(args), 5)
        self.assertEqual(args[0], self.manager)
        self.assertEqual(type(args[1]), type(self.playlist))
        self.assertEqual(args[1].name(), self.playlist.name())
        self.assertEqual(type(args[2]), list)
        self.assertEqual(len(args[2]), 3)
        self.assertEqual(args[2], [0, 1, 2])
        self.assertEqual(type(args[3]), int)

    def test_tracks_removed(self):
        global callback_called
        callback = self.manager.tracks_removed
        self.playlist.add_tracks_removed_callback(callback, self.manager)
        mock_event_trigger(6, self.playlist)

        self.assertNotEqual(callback_called, None)
        name, args = callback_called
        self.assertEqual(name, "tracks_removed")
        self.assertEqual(len(args), 4)
        self.assertEqual(args[0], self.manager)
        self.assertEqual(type(args[1]), type(self.playlist))
        self.assertEqual(args[1].name(), self.playlist.name())
        self.assertEqual(type(args[2]), list)
        self.assertEqual(len(args[2]), 3)
        self.assertEqual(args[2], [0, 1, 2])
