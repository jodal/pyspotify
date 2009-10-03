
import unittest
from pyspotify import spotify

class TestGlobals(unittest.TestCase):

    def test_api_version(self):
        self.assertEqual(spotify.Client.api_version, 2)
