# encoding: utf-8

import unittest
import threading

from spotify import _mockspotify
import spotify.manager.session
# monkeypatch for testing
spotify.manager.session.spotify = spotify._mockspotify

from spotify import Settings
from spotify.manager import SpotifySessionManager
from spotify._mockspotify import mock_track, mock_album, Session


class BaseMockClient(SpotifySessionManager):

    cache_location = "/foo"
    settings_location = "/foo"
    application_key = "appkey_good"
    user_agent = "user_agent_foo"

    def __init__(self):
        SpotifySessionManager.__init__(self, "username_good", "password_good")

class BaseMockUnicodeClient(SpotifySessionManager):

    cache_location = u'/f××'
    settings_location = u'/f××'
    application_key = "appkey_good"
    user_agent = u'üser_âgent_f©©'

    def __init__(self):
        SpotifySessionManager.__init__(self, "username_good", "password_good")

class TestSession(unittest.TestCase):

    def test_create(self):
        c = BaseMockClient()
        s = Settings()
        s.application_key = "appkey_good"
        session = Session.create(c, s)

    def test_initialisation(self):
        class MockClient(BaseMockClient):
            def logged_in(self, session, error):
                username = session.username()
                self.found_username = username
                self.disconnect()

        c = MockClient()
        c.connect()
        self.assertEqual(c.username, c.found_username)

    def test_unicode(self):
        class MockClient(BaseMockUnicodeClient):
            def logged_in(self, session, error):
                username = session.username()
                self.found_username = username
                self.disconnect()

        c = MockClient()
        c.connect()
        self.assertEqual(c.username, c.found_username)

    def NOtest_load(self):
        class MockClient(BaseMockClient):
            def logged_in(self, session, error):
                track = mock_track("foo", 0, mock_album("bar", mock_artist("baz", 1), 0, "", 0), 0, 0, 0, 0, 0, 1)
                session.load(track)
                session.seek(40000)
                session.play(True)
                self.disconnect()

            def music_delivery(self, sess, mformat, frames):
                pass

        c = MockClient()
        c.connect()
