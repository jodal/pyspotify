# $Id$
#
# Copyright 2009 Doug Winter
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
import threading

from spotify import _mockspotify
from spotify import manager
# monkeypatch for testing
manager.spotify = _mockspotify

from spotify.manager import SpotifySessionManager
from spotify._mockspotify import mock_track, mock_album


class BaseMockClient(SpotifySessionManager):

    cache_location = "/foo"
    settings_location = "/foo"
    application_key = "appkey_good"
    user_agent = "user_agent_foo"

    def __init__(self):
        SpotifySessionManager.__init__(self, "username_good", "password_good")
        self.awoken = threading.Event() # used to block until awoken

class TestSession(unittest.TestCase):

    def test_initialisation(self):
        class MockClient(BaseMockClient):
            def logged_in(self, session, error):
                username = session.username()
                self.found_username = username
                session.logout()
                self.disconnect()

        c = MockClient()
        c.connect()
        self.assertEqual(c.username, c.found_username)

    def NOtest_load(self):
        class MockClient(BaseMockClient):
            def logged_in(self, session, error):
                track = mock_track("foo", 0, mock_album("bar", mock_artist("baz", 1), 0, "", 0), 0, 0, 0, 0, 0, 1)
                session.load(track)
                session.play(True)
                session.logout()
                self.disconnect()

            def music_delivery(self, sess, mformat, frames):
                pass

        c = MockClient()
        c.connect()
