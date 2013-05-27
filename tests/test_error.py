from __future__ import unicode_literals

import unittest

import six
import spotify


class ErrorTest(unittest.TestCase):

    def test_error_has_error_type(self):
        error = spotify.Error(0)
        self.assertEqual(error.error_type, 0)

        error = spotify.Error(1)
        self.assertEqual(error.error_type, 1)

    def test_is_equal_if_same_error_type(self):
        self.assertEqual(spotify.Error(0), spotify.Error(0))

    def test_is_not_equal_if_different_error_type(self):
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

    def test_has_error_constants(self):
        self.assertEqual(
            spotify.Error.OK, spotify.Error(spotify.ErrorType.OK))
        self.assertEqual(
            spotify.Error.BAD_API_VERSION,
            spotify.Error(spotify.ErrorType.BAD_API_VERSION))

    def test_maybe_raise(self):
        self.assertRaises(
            spotify.Error,
            spotify.Error.maybe_raise, spotify.ErrorType.BAD_API_VERSION)

    def test_maybe_raise_does_not_raise_if_ok(self):
        spotify.Error.maybe_raise(spotify.ErrorType.OK)

    def test_maybe_raise_does_not_raise_if_error_is_ignored(self):
        spotify.Error.maybe_raise(
            spotify.ErrorType.BAD_API_VERSION,
            ignores=[spotify.ErrorType.BAD_API_VERSION])

    def test_maybe_raise_works_with_any_iterable(self):
        spotify.Error.maybe_raise(
            spotify.ErrorType.BAD_API_VERSION,
            ignores=(spotify.ErrorType.BAD_API_VERSION,))


class ErrorTypeTest(unittest.TestCase):

    def test_has_error_type_constants(self):
        self.assertEqual(spotify.ErrorType.OK, 0)
        self.assertEqual(spotify.ErrorType.BAD_API_VERSION, 1)
