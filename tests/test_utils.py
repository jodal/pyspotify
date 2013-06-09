# encoding: utf-8

from __future__ import unicode_literals

import unittest

import spotify
from spotify import utils


class IntEnumTest(unittest.TestCase):

    def setUp(self):
        class Foo(utils.IntEnum):
            pass

        self.Foo = Foo

        self.Foo.add('bar', 1)
        self.Foo.add('baz', 2)

    def test_has_pretty_repr(self):
        self.assertEqual(repr(self.Foo.bar), '<Foo.bar: 1>')
        self.assertEqual(repr(self.Foo.baz), '<Foo.baz: 2>')

    def test_is_equal_to_the_int_value(self):
        self.assertEqual(self.Foo.bar, 1)
        self.assertEqual(self.Foo.baz, 2)

    def test_two_instances_with_same_value_is_identical(self):
        self.assertIs(self.Foo(1), self.Foo.bar)
        self.assertIs(self.Foo(2), self.Foo.baz)
        self.assertIsNot(self.Foo(2), self.Foo.bar)
        self.assertIsNot(self.Foo(1), self.Foo.baz)


class ToBytesTest(unittest.TestCase):

    def test_unicode_to_bytes_is_encoded_as_utf8(self):
        self.assertEqual(utils.to_bytes('æøå'), 'æøå'.encode('utf-8'))

    def test_bytes_to_bytes_is_passed_through(self):
        self.assertEqual(
            utils.to_bytes('æøå'.encode('utf-8')), 'æøå'.encode('utf-8'))

    def test_cdata_to_bytes_is_unwrapped(self):
        cdata = spotify.ffi.new('char[]', 'æøå'.encode('utf-8'))
        self.assertEqual(utils.to_bytes(cdata), 'æøå'.encode('utf-8'))

    def test_anything_else_to_bytes_fails(self):
        self.assertRaises(ValueError, utils.to_bytes, [])
        self.assertRaises(ValueError, utils.to_bytes, 123)


class ToUnicodeTest(unittest.TestCase):

    def test_unicode_to_unicode_is_passed_through(self):
        self.assertEqual(utils.to_unicode('æøå'), 'æøå')

    def test_bytes_to_unicode_is_decoded_as_utf8(self):
        self.assertEqual(utils.to_unicode('æøå'.encode('utf-8')), 'æøå')

    def test_cdata_to_unicode_is_unwrapped_and_decoded_as_utf8(self):
        cdata = spotify.ffi.new('char[]', 'æøå'.encode('utf-8'))
        self.assertEqual(utils.to_unicode(cdata), 'æøå')

    def test_anything_else_to_unicode_fails(self):
        self.assertRaises(ValueError, utils.to_unicode, [])
        self.assertRaises(ValueError, utils.to_unicode, 123)


class ToCountryCode(unittest.TestCase):

    def test_unicode_to_country_code(self):
        self.assertEqual(utils.to_country_code('NO'), 20047)
        self.assertEqual(utils.to_country_code('SE'), 21317)

    def test_bytes_to_country_code(self):
        self.assertEqual(utils.to_country_code(b'NO'), 20047)
        self.assertEqual(utils.to_country_code(b'SE'), 21317)

    def test_fails_if_not_exactly_two_chars(self):
        self.assertRaises(ValueError, utils.to_country_code, 'NOR')

    def test_fails_if_not_in_uppercase(self):
        self.assertRaises(ValueError, utils.to_country_code, 'no')


class ToCountry(unittest.TestCase):

    def test_to_country(self):
        self.assertEqual(utils.to_country(20047), 'NO')
        self.assertEqual(utils.to_country(21317), 'SE')
