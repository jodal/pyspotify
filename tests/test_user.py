# encoding: utf-8

import unittest

from spotify._mockspotify import User, mock_user

class TestUser(unittest.TestCase):

    def test_str(self):
        user = mock_user(u'foo',u'bar',1);
        self.assertEqual(str(user), u'foo')

    def test_is_loaded(self):
        user = mock_user('','',1);
        self.assertEqual(user.is_loaded(), True)
        user = mock_user('','',0);
        self.assertEqual(user.is_loaded(), False)

    def test_canonical_name(self):
        user = mock_user(u'foo',u'bar',1);
        self.assertEqual(user.canonical_name(), u'foo')

    def test_display_name(self):
        user = mock_user(u'foo',u'bar',1);
        self.assertEqual(user.display_name(), u'bar')

    def test_unicode(self):
        user = mock_user(u'føø',u'bãr',1);
        self.assertEqual(user.canonical_name(), u'føø')
        self.assertEqual(user.display_name(), u'bãr')
