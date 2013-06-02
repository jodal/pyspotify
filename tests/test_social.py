from __future__ import unicode_literals

import unittest

import spotify


class ScrobblingStateTest(unittest.TestCase):

    def test_has_constants(self):
        self.assertEqual(spotify.ScrobblingState.USE_GLOBAL_SETTING, 0)
        self.assertEqual(spotify.ScrobblingState.LOCAL_ENABLED, 1)


class SocialProviderTest(unittest.TestCase):

    def test_has_constants(self):
        self.assertEqual(spotify.SocialProvider.SPOTIFY, 0)
        self.assertEqual(spotify.SocialProvider.FACEBOOK, 1)
