import unittest
import spotify

class TestGlobals(unittest.TestCase):

    def test_api_version(self):
        self.assertEqual(spotify.api_version, 11)
