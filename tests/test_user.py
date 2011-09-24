# encoding: utf-8

import unittest

from spotify._mockspotify import User, mock_user, mock_session
from spotify.constant import RELATION_TYPE_BIDIRECTIONAL

class TestUser(unittest.TestCase):

    def test_str(self):
        user = mock_user(u'foo',u'bar',u'baz',u'url',0,1);
        self.assertEqual(str(user), u'foo')

    def test_is_loaded(self):
        user = mock_user('','','','',0,1);
        self.assertEqual(user.is_loaded(), True)
        user = mock_user('','','','',0,0);
        self.assertEqual(user.is_loaded(), False)

    def test_canonical_name(self):
        user = mock_user(u'foo',u'bar',u'baz',u'url',0,1);
        self.assertEqual(user.canonical_name(), u'foo')

    def test_display_name(self):
        user = mock_user(u'foo',u'bar',u'baz',u'url',0,1);
        self.assertEqual(user.display_name(), u'bar')

    def test_full_name(self):
        user = mock_user(u'foo',u'bar',u'baz',u'url',0,1);
        self.assertEqual(user.full_name(), u'baz')

    def test_full_name_not_loaded(self):
        user = mock_user(u'foo',u'bar',u'baz',u'url',0,0);
        self.assertEqual(user.full_name(), None)

    def test_picture(self):
        user = mock_user(u'foo',u'bar',u'baz',u'url',0,1);
        self.assertEqual(user.picture(), u'url')

    def test_picture_not_loaded(self):
        user = mock_user(u'foo',u'bar',u'baz',u'url',0,0);
        self.assertEqual(user.picture(), None)

    def test_relation(self):
        user = mock_user(u'foo',u'bar',u'baz',u'url',3,1);
        self.assertEqual(user.relation(), RELATION_TYPE_BIDIRECTIONAL)

    def test_unicode(self):
        user = mock_user(u'føø',u'bãr',u'båz',u'ürl',0,1);
        self.assertEqual(user.canonical_name(), u'føø')
        self.assertEqual(user.display_name(), u'bãr')
        self.assertEqual(user.full_name(), u'båz')
        self.assertEqual(user.picture(), u'ürl')
