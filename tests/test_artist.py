# encoding: utf-8

import unittest
from spotify._mockspotify import Artist, mock_artist

class TestArtist(unittest.TestCase):

    def test_str(self):
        artist = mock_artist("test_name")
        self.assertEqual(str(artist), "test_name")


    def test_is_loaded(self):
        artist = mock_artist("test_name", is_loaded=1)
        self.assertTrue(artist.is_loaded())
        artist = mock_artist("test_name", is_loaded=0)
        self.assertFalse(artist.is_loaded())

    def test_name(self):
        artist = mock_artist("test_name")
        self.assertEqual(artist.name(), "test_name")

    def test_unicode(self):
        artist = mock_artist(u'æâ€êþÿ')
        self.assertEqual(artist.name(), u'æâ€êþÿ')
