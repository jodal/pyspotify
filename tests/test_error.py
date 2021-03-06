from __future__ import unicode_literals

import unittest

import spotify
from spotify import compat


class ErrorTest(unittest.TestCase):
    def test_error_is_an_exception(self):
        error = spotify.Error(0)
        self.assertIsInstance(error, Exception)

    def test_maybe_raise(self):
        with self.assertRaises(spotify.LibError):
            spotify.Error.maybe_raise(spotify.ErrorType.BAD_API_VERSION)

    def test_maybe_raise_does_not_raise_if_ok(self):
        spotify.Error.maybe_raise(spotify.ErrorType.OK)

    def test_maybe_raise_does_not_raise_if_error_is_ignored(self):
        spotify.Error.maybe_raise(
            spotify.ErrorType.BAD_API_VERSION,
            ignores=[spotify.ErrorType.BAD_API_VERSION],
        )

    def test_maybe_raise_works_with_any_iterable(self):
        spotify.Error.maybe_raise(
            spotify.ErrorType.BAD_API_VERSION,
            ignores=(spotify.ErrorType.BAD_API_VERSION,),
        )


class LibErrorTest(unittest.TestCase):
    def test_is_an_error(self):
        error = spotify.LibError(0)
        self.assertIsInstance(error, spotify.Error)

    def test_has_error_type(self):
        error = spotify.LibError(0)
        self.assertEqual(error.error_type, 0)

        error = spotify.LibError(1)
        self.assertEqual(error.error_type, 1)

    def test_is_equal_if_same_error_type(self):
        self.assertEqual(spotify.LibError(0), spotify.LibError(0))

    def test_is_not_equal_if_different_error_type(self):
        self.assertNotEqual(spotify.LibError(0), spotify.LibError(1))

    def test_error_has_useful_repr(self):
        error = spotify.LibError(0)
        self.assertIn("No error", repr(error))

    def test_error_has_useful_string_representation(self):
        error = spotify.LibError(0)
        self.assertEqual("%s" % error, "No error")
        self.assertIsInstance("%s" % error, compat.text_type)

        error = spotify.LibError(1)
        self.assertEqual("%s" % error, "Invalid library version")

    def test_has_error_constants(self):
        self.assertEqual(spotify.LibError.OK, spotify.LibError(spotify.ErrorType.OK))
        self.assertEqual(
            spotify.LibError.BAD_API_VERSION,
            spotify.LibError(spotify.ErrorType.BAD_API_VERSION),
        )


class ErrorTypeTest(unittest.TestCase):
    def test_has_error_type_constants(self):
        self.assertEqual(spotify.ErrorType.OK, 0)
        self.assertEqual(spotify.ErrorType.BAD_API_VERSION, 1)


class TimeoutTest(unittest.TestCase):
    def test_is_an_error(self):
        error = spotify.Timeout(0.5)
        self.assertIsInstance(error, spotify.Error)

    def test_has_useful_repr(self):
        error = spotify.Timeout(0.5)
        self.assertIn("Operation did not complete in 0.500s", repr(error))

    def test_has_useful_string_representation(self):
        error = spotify.Timeout(0.5)
        self.assertEqual("%s" % error, "Operation did not complete in 0.500s")
        self.assertIsInstance("%s" % error, compat.text_type)
