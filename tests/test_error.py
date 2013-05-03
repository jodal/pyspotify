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

    def test_error_has_error_message(self):
        error = spotify.Error(0)
        self.assertEqual(error.message, 'No error')
        self.assertIsInstance(error.message, six.text_type)

        error = spotify.Error(1)
        self.assertEqual(error.message, 'Invalid library version')

    def test_error_has_useful_repr(self):
        error = spotify.Error(0)
        self.assertEqual(repr(error), 'No error (error code 0)')

    def test_error_has_useful_str(self):
        error = spotify.Error(0)
        self.assertEqual(str(error), error.message)

    def test_error_has_error_constants(self):
        self.assertEqual(spotify.Error.OK, 0)
        self.assertEqual(spotify.Error.BAD_API_VERSION, 1)
