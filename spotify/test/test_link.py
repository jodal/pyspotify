import unittest
from spotify.link import Link

class TestLink(unittest.TestCase):

    def test_playlist_string(self):
        s = "spotify:user:winjer:playlist:4gzM1HrVHQXvCnALez6xhr"
        l = Link.from_string(s)
        self.assertEqual(str(l), s)

