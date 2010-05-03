# $Id$
#
# Copyright 2009 Doug Winter
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
from spotify import _mockspotify
from spotify._mockspotify import mock_album, mock_artist, mock_track
from spotify import Album

class TestPlaylistContainer(unittest.TestCase):

    def test_len(self):
        p1 = _mockspotify.mock_playlist("foo", [])
        p2 = _mockspotify.mock_playlist("bar", [])
        pc = _mockspotify.mock_playlistcontainer([p1, p2])
        self.assertEqual(len(pc), 2)

    def test_sq_item(self):
        p1 = _mockspotify.mock_playlist("foo", [])
        p2 = _mockspotify.mock_playlist("bar", [])
        pc = _mockspotify.mock_playlistcontainer([p1, p2])
        self.assertEqual(pc[0].name(), "foo")
        self.assertEqual(pc[1].name(), "bar")

    def test_sq_item_exception(self):
        p1 = _mockspotify.mock_playlist("foo", [])
        p2 = _mockspotify.mock_playlist("bar", [])
        pc = _mockspotify.mock_playlistcontainer([p1, p2])
        def _():
            return pc[2]
        self.assertRaises(IndexError, _)

class TestPlaylist(unittest.TestCase):

    def _mock_track(self, name):
        return mock_track(name, 0, mock_album("foo", mock_artist("bar", 1), 2006, "01234567890123456789", Album.ALBUM, 1), 0, 0, 0, 0, 0, 1)

    def test_name(self):
        p1 = _mockspotify.mock_playlist("foo", [])
        self.assertEqual(p1.name(), "foo")

    def test_len(self):
        p1 = self._mock_track("foo")
        p2 = self._mock_track("bar")
        pc = _mockspotify.mock_playlist("foobar", [p1, p2])
        self.assertEqual(len(pc), 2)

    def test_sq_item(self):
        p1 = self._mock_track("foo")
        p2 = self._mock_track("bar")
        pc = _mockspotify.mock_playlist("foobar", [p1, p2])
        self.assertEqual(pc[0].name(), "foo")
        self.assertEqual(pc[1].name(), "bar")
