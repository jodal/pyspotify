# encoding: utf-8

from __future__ import unicode_literals

import gc
import mock
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


@mock.patch('spotify.search.lib', spec=spotify.lib)
class SequenceTest(unittest.TestCase):

    def test_does_not_add_ref_to_sp_obj_when_created(self, lib_mock):
        sp_search = spotify.ffi.new('int *')

        utils.Sequence(sp_search, None, None)

        self.assertEqual(lib_mock.sp_search_add_ref.call_count, 0)

    def test_does_not_release_sp_search_when_search_dies(self, lib_mock):
        sp_search = spotify.ffi.new('int *')

        seq = utils.Sequence(sp_search, None, None)
        seq = None  # noqa
        gc.collect()  # Needed for PyPy

        self.assertEqual(lib_mock.sp_search_release.call_count, 0)

    def test_len_calls_len_func(self, lib_mock):
        sp_search = spotify.ffi.new('int *')

        len_func = mock.Mock()
        len_func.return_value = 0
        seq = utils.Sequence(sp_search, len_func, None)

        result = len(seq)

        self.assertEqual(result, 0)
        len_func.assert_called_with(sp_search)

    def test_getitem_calls_getitem_func(self, lib_mock):
        sp_search = spotify.ffi.new('int *')

        getitem_func = mock.Mock()
        getitem_func.return_value = mock.sentinel.item_one
        seq = utils.Sequence(sp_search, lambda x: 1, getitem_func)

        result = seq[0]

        self.assertEqual(result, mock.sentinel.item_one)
        getitem_func.assert_called_with(sp_search, 0)

    def test_getitem_raises_index_error_on_negative_index(self, lib_mock):
        sp_search = spotify.ffi.new('int *')

        seq = utils.Sequence(sp_search, lambda x: 1, None)

        self.assertRaises(IndexError, seq.__getitem__, -1)

    def test_getitem_raises_index_error_on_too_high_index(self, lib_mock):
        sp_search = spotify.ffi.new('int *')

        seq = utils.Sequence(sp_search, lambda x: 1, None)

        self.assertRaises(IndexError, seq.__getitem__, 1)

    def test_getitem_raises_type_error_on_non_integral_index(self, lib_mock):
        sp_search = spotify.ffi.new('int *')

        seq = utils.Sequence(sp_search, lambda x: 1, None)

        self.assertRaises(TypeError, seq.__getitem__, 'abc')


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
