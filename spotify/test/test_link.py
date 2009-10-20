import unittest
from spotify._mockspotify import Link, mock_artist, mock_track, mock_album, mock_playlist
from spotify import SpotifyError

class TestLink(unittest.TestCase):

    def test_from_string(self):
        s = "from_string_test"
        l = Link.from_string(s)
        self.assertEqual(str(l), "link:from_string_test")

    def test_from_track(self):
        t = mock_track("foo", 0, mock_album("bar"), 0, 0, 0, 0, 0, 1)
        l2 = Link.from_track(t, 42)
        self.assertEqual(str(l2), "link_from_track:foo")

    def test_from_album(self):
        a = mock_album("foo")
        l2 = Link.from_album(a)
        self.assertEqual(str(l2), "link_from_album:foo")

    def test_from_artist(self):
        a = mock_artist("artist", 1)
        l = Link.from_artist(a)
        self.assertEqual(str(l), "link_from_artist:artist")

    def test_from_search(self):
        s = mock_search("query")
        l2 = Link.from_search(s)
        self.assertEqual(str(l2), "link_from_search:query")

    def test_from_playlist(self):
        p = mock_playlist("foo", [])
        l = Link.from_playlist(p)
        self.assertEqual(str(l), "link_from_playlist:foo")

    def test_type(self):
        t = mock_track("foo", 0, mock_album("bar"), 0, 0, 0, 0, 0, 1)
        l2 = Link.from_track(t, 42)
        self.assertEqual(l2.type(), Link.LINK_TRACK)
        a = mock_album("foo")
        l2 = Link.from_album(a)
        self.assertEqual(l2.type(), Link.LINK_ALBUM)
        a = mock_artist("artist", 1)
        l = Link.from_artist(a)
        self.assertEqual(l.type(), Link.LINK_ARTIST)
        s = mock_search("query")
        l2 = Link.from_search(s)
        self.assertEqual(l.type(), Link.LINK_SEARCH)
        p = mock_playlist("foo", [])
        l = Link.from_playlist(p)
        self.assertEqual(l.type(), Link.LINK_PLAYLIST)

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
