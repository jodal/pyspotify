
import unittest
from spotify import _mockspotify

class TestPlaylistContainer(unittest.TestCase):

    def test_len(self):
        p1 = _mockspotify.mock_playlist("foo")
        p2 = _mockspotify.mock_playlist("bar")
        pc = _mockspotify.mock_playlistcontainer([p1, p2])
        self.assertEqual(len(pc), 2)
        
    def test_sq_item(self):
        p1 = _mockspotify.mock_playlist("foo")
        p2 = _mockspotify.mock_playlist("bar")
        pc = _mockspotify.mock_playlistcontainer([p1, p2])
        self.assertEqual(pc[0].name(), "foo")
        self.assertEqual(pc[1].name(), "bar")

    def test_sq_item_exception(self):
        p1 = _mockspotify.mock_playlist("foo")
        p2 = _mockspotify.mock_playlist("bar")
        pc = _mockspotify.mock_playlistcontainer([p1, p2])
        def _():
            return pc[2]
        self.assertRaises(IndexError, _)
 
class TestPlaylist(unittest.TestCase):
    
    def test_name(self):
        p1 = _mockspotify.mock_playlist("foo")
        self.assertEqual(p1.name(), "foo")
        