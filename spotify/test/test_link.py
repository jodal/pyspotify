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
from spotify._mockspotify import Link, mock_artist, mock_track, mock_album, mock_playlist, mock_search
from spotify import SpotifyError

# fake change

class TestLink(unittest.TestCase):

    def test_from_string(self):
        s = "from_string_test"
        l = Link.from_string(s)
        self.assertEqual(str(l), "link:from_string_test")

    def test_from_track(self):
        t = mock_track("foo", 0, mock_album("bar", mock_artist("baz", 1), 0, "", 0, 1), 0, 0, 0, 0, 0, 1)
        l2 = Link.from_track(t, 42)
        self.assertEqual(str(l2), "link:track:foo/42")

    def test_from_album(self):
        a = mock_album("bar", mock_artist("baz", 1), 0, "", 0, 1)
        l2 = Link.from_album(a)
        self.assertEqual(str(l2), "link:album:bar")

    def test_from_artist(self):
        a = mock_artist("artist", 1)
        l = Link.from_artist(a)
        self.assertEqual(str(l), "link:artist:artist")

    def test_from_search(self):
        s = mock_search("query")
        l2 = Link.from_search(s)
        self.assertEqual(str(l2), "link:search:query")

    def test_from_playlist(self):
        p = mock_playlist("foo", [])
        l = Link.from_playlist(p)
        self.assertEqual(str(l), "link:playlist:foo")

    def test_type(self):
        t = mock_track("foo", 0, mock_album("bar", mock_artist("baz", 1), 0, "", 0, 1), 0, 0, 0, 0, 0, 1)
        l2 = Link.from_track(t, 42)
        self.assertEqual(l2.type(), Link.LINK_TRACK)

    def test_as_track(self):
        l = Link.from_string("track:as_track_test")
        t = l.as_track()
        self.assertEqual(str(t), "as_track_test")

    def test_as_track_badlink(self):
        l = Link.from_string("NOTtrack:as_track_test")
        self.assertRaises(SpotifyError, l.as_track)

    def test_as_album(self):
        l = Link.from_string("album:as_album_test")
        t = l.as_album()
        self.assertEqual(str(t), "as_album_test")

    def test_as_album_badlink(self):
        l = Link.from_string("NOTalbum:as_album_test")
        self.assertRaises(SpotifyError, l.as_album)

    def test_as_artist(self):
        l = Link.from_string("artist:test_as_artist")
        a = l.as_artist()
        self.assertEqual(str(a), "test_as_artist")

    def test_as_artist_badlink(self):
        l = Link.from_string("NOTartist:test_as_artist")
        self.assertRaises(SpotifyError, l.as_artist)

    def test_str(self):
        s = "str_test"
        l = Link.from_string(s)
        self.assertEqual(str(l), "link:str_test")
