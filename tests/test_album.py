# encoding: utf-8

import unittest
from spotify._mockspotify import mock_album, mock_artist, Album

class TestAlbum(unittest.TestCase):

    album = mock_album(u'æâ€êþÿ', mock_artist("bar"), 2006,
                       "01234567890123456789", Album.ALBUM, 1, 1)

    def test_is_loaded(self):
        self.assertEqual(self.album.is_loaded(), 1)

    def test_name(self):
        self.assertEqual(self.album.name(), u'æâ€êþÿ')

    def test_artist(self):
        self.assertEqual(self.album.artist().name(), "bar")

    def test_year(self):
        self.assertEqual(self.album.year(), 2006)

    def test_cover(self):
        self.assertEqual(self.album.cover(), "01234567890123456789")

    def test_type(self):
        self.assertEqual(self.album.type(), Album.ALBUM)

