
import unittest
from spotify import client

class TestGlobals(unittest.TestCase):

    def test_api_version(self):
        self.assertEqual(client.Client.api_version, 2)
