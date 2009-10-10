import unittest
from spotify._mockspotify import Link, mock_artist
from spotify import SpotifyError

class TestLink(unittest.TestCase):

    def test_from_string(self):
        s = "from_string_test"
        l = Link.from_string(s)
        self.assertEqual(str(l), "link:from_string_test")

    def test_from_track(self):
        s = "track:from_track_test"
        l = Link.from_string(s)
        t = l.as_track()
        l2 = Link.from_track(t, 42)
        self.assertEqual(str(l2), "link:from_track_test/42")

    def test_from_album(self):
        pass

    def test_from_artist(self):
        a = mock_artist("test_from_artist", 1)
        l = Link.from_artist(a)
        self.assertEqual(str(l), "link_from_artist:test_from_artist");

    def test_from_search(self):
        pass

    def test_from_playlist(self):
        pass

    def test_type(self):
        pass

    def test_as_track(self):
        l = Link.from_string("track:as_track_test")
        t = l.as_track()
        self.assertEqual(str(t), "as_track_test")

    def test_as_track_badlink(self):
        l = Link.from_string("NOTtrack:as_track_test")
        self.assertRaises(SpotifyError, l.as_track)

    def test_as_album(self):
        pass

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

