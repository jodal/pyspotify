from __future__ import unicode_literals

import unittest

import spotify


class ConnectionRuleTest(unittest.TestCase):

    def test_has_constants(self):
        self.assertEqual(spotify.ConnectionRule.NETWORK, 1)
        self.assertEqual(spotify.ConnectionRule.ALLOW_SYNC_OVER_WIFI, 8)


class ConnectionStateTest(unittest.TestCase):

    def test_has_constants(self):
        self.assertEqual(spotify.ConnectionState.LOGGED_OUT, 0)


class ConnectionTypeTest(unittest.TestCase):

    def test_has_constants(self):
        self.assertEqual(spotify.ConnectionType.UNKNOWN, 0)
