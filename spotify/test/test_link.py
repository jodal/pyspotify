import unittest
from spotify._mockspotify import Link

class TestLink(unittest.TestCase):

    def test_from_string(self):
        s = "from_string_test"
        l = Link.from_string(s)
        self.assertEqual(str(l), "link:from_string_test")

    def test_from_track(self):
        s = "from_track_test"
        l = Link.from_string(s)
        t = l.as_track()
        l2 = Link.from_track(t, 42)
        self.assertEqual(str(l2), "link:track:link:from_track_test/42")

    def test_from_album(self):
        pass

    def test_from_artist(self):
        pass

    def test_from_search(self):
        pass

    def test_from_playlist(self):
        pass

    def test_type(self):
        pass

    def test_as_track(self):
        s = "as_track_test"
        l = Link.from_string(s)
        print "l is", l
        t = l.as_track()
        self.assertEqual(str(t), "track:link:as_track_test")

    def test_as_album(self):
        pass

    def test_as_artist(self):
        pass

    def test_str(self):
        pass



