
import unittest
import _spotify

class MockClient:

    cache_location = "/foo"

class TestSession(unittest.TestCase):

    def test_initialisation(self):
        client = MockClient()
        session = _spotify.Session(client)
        self.assertEqual(session.client, client)

