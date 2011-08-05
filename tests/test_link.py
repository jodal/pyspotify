import unittest
from spotify._mockspotify import Link, mock_artist, mock_track, mock_album, mock_playlist, mock_search
from spotify import SpotifyError

# fake change

class TestLink(unittest.TestCase):

    def test_from_string(self):
        s = "spotify:artist:test"
        l = Link.from_string(s)
        self.assertEqual(str(l), "spotify:artist:test")

    def test_from_track(self):
        t = mock_track("foo", 0, mock_album("bar", mock_artist("baz", 1), 0, "",
                                            0, 1, 1), 0, 0, 0, 0, 0, 1)
        l2 = Link.from_track(t, 42)
        self.assertEqual(str(l2), "spotify:track:foo/42")

    def test_from_album(self):
        a = mock_album("bar", mock_artist("baz", 1), 0, "", 0, 1, 1)
        l2 = Link.from_album(a)
        self.assertEqual(str(l2), "spotify:album:bar")

    def test_from_artist(self):
        a = mock_artist("artist", 1)
        l = Link.from_artist(a)
        self.assertEqual(str(l), "spotify:artist:artist")

    def test_from_search(self):
        s = mock_search("query")
        l2 = Link.from_search(s)
        self.assertEqual(str(l2), "spotify:search:query")

    def test_from_playlist(self):
        p = mock_playlist("foo", [])
        l = Link.from_playlist(p)
        self.assertEqual(str(l), "spotify:playlist:foo")

    def test_type(self):
        t = mock_track("foo", 0, mock_album("bar", mock_artist("baz", 1), 0, "",
                                            0, 1, 1), 0, 0, 0, 0, 0, 1)
        l2 = Link.from_track(t, 42)
        self.assertEqual(l2.type(), Link.LINK_TRACK)

    def test_badlink(self):
        self.assertRaises(SpotifyError, Link.from_string , "BADLINK");

    def test_as_track(self):
        l = Link.from_string("spotify:track:as_track_test")
        t = l.as_track()
        self.assertEqual(str(t), "as_track_test")

    def test_as_album(self):
        l = Link.from_string("spotify:album:as_album_test")
        t = l.as_album()
        self.assertEqual(str(t), "as_album_test")

    def test_as_artist(self):
        l = Link.from_string("spotify:artist:test_as_artist")
        a = l.as_artist()
        self.assertEqual(str(a), "test_as_artist")

    def test_as_string(self):
        s = "spotify:track:str_test"
        l = Link.from_string(s)
        self.assertEqual(str(l), "spotify:track:str_test")
