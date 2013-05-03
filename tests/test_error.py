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
