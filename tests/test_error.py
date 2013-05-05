from __future__ import unicode_literals

import unittest

import six
import spotify


class ErrorTest(unittest.TestCase):

    def test_error_has_error_code(self):
        error = spotify.Error(0)
        self.assertEqual(error.error_code, 0)

        error = spotify.Error(1)
        self.assertEqual(error.error_code, 1)

    def test_is_equal_if_same_error_code(self):
        self.assertEqual(spotify.Error(0), spotify.Error(0))

    def test_is_not_equal_if_different_error_code(self):
        self.assertNotEqual(spotify.Error(0), spotify.Error(1))

    def test_error_has_useful_repr(self):
        error = spotify.Error(0)
        self.assertIn('No error', repr(error))

    def test_error_has_useful_string_representation(self):
        error = spotify.Error(0)
        self.assertEqual('%s' % error, 'No error')
        self.assertIsInstance('%s' % error, six.text_type)

        error = spotify.Error(1)
        self.assertEqual('%s' % error, 'Invalid library version')

    def test_error_has_error_constants(self):
        self.assertEqual(spotify.Error.OK, 0)
        self.assertEqual(spotify.Error.BAD_API_VERSION, 1)
