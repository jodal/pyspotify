# encoding: utf-8

import unittest
from spotify._mockspotify import Artist, mock_artist

class TestArtist(unittest.TestCase):

    def test_str(self):
        artist = mock_artist("test_name", 1)
        self.assertEqual(str(artist), "test_name")


    def test_is_loaded(self):
        artist = mock_artist("test_name", 1)
        self.assertEqual(artist.is_loaded(), 1)
        artist = mock_artist("test_name", 0)
        self.assertEqual(artist.is_loaded(), 0)

    def test_name(self):
        artist = mock_artist("test_name", 1)
        self.assertEqual(artist.name(), "test_name")

    def test_unicode(self):
        artist = mock_artist(u'æâ€êþÿ', 1)
        self.assertEqual(artist.name(), u'æâ€êþÿ')
