import unittest
from spotify._mockspotify import Link

class TestLink(unittest.TestCase):

    def test_from_string(self):
        s = "from_string_test"
        l = Link.from_string(s)
        self.assertEqual(str(l), "link:from_string_test")

    def test_as_track(self):
        s = "as_track_test"
        l = Link.from_string(s)
        print "l is", l
        t = l.as_track()
        self.assertEqual(str(t), "track:link:as_track_test")


