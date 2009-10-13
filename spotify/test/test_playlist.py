
import unittest
from spotify import _mockspotify

class TestPlaylistContainer(unittest.TestCase):

    def test_sq_item(self):
        p1 = _mockspotify.mock_playlist("foo")
        p2 = _mockspotify.mock_playlist("bar")
        pc = _mockspotify.mock_playlistcontainer([p1, p2])
        self.assertEqual(pc[0].name(), "foo")
        #self.assertEqual(pc[1].name(), "bar")


