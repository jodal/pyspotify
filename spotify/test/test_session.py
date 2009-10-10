
import unittest
import threading

from spotify import client
from spotify import _mockspotify

client.spotify = _mockspotify

class MockClient(client.Client):

    cache_location = "/foo"
    settings_location = "/foo"
    application_key = "appkey_good"
    user_agent = "user_agent_foo"
    username = "username_good"
    password = "password_good"

    def __init__(self):
        self.awoken = threading.Event() # used to block until awoken

    def logged_in(self, session, error):
        print "MockClient: logged_in"
        username = session.username()
        self.found_username = username
        session.logout()
        self.disconnect()

class TestSession(unittest.TestCase):

    def test_initialisation(self):
        c = MockClient()
        c.connect()
        self.assertEqual(c.username, c.found_username)




