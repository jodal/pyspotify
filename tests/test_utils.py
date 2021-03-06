# encoding: utf-8

from __future__ import unicode_literals

import unittest

import spotify
import tests
from spotify import utils
from tests import mock


class EventEmitterTest(unittest.TestCase):
    def test_listener_receives_event_args(self):
        listener_mock = mock.Mock()
        emitter = utils.EventEmitter()
        emitter.on("some_event", listener_mock)

        emitter.emit("some_event", "abc", "def")

        listener_mock.assert_called_with("abc", "def")

    def test_listener_receives_both_user_and_event_args(self):
        listener_mock = mock.Mock()
        emitter = utils.EventEmitter()

        emitter.on("some_event", listener_mock, 1, 2, 3)
        emitter.emit("some_event", "abc")

        listener_mock.assert_called_with("abc", 1, 2, 3)

    def test_multiple_listeners_for_same_event(self):
        listener_mock1 = mock.Mock()
        listener_mock2 = mock.Mock()
        emitter = utils.EventEmitter()

        emitter.on("some_event", listener_mock1, 1, 2, 3)
        emitter.on("some_event", listener_mock2, 4, 5)
        emitter.emit("some_event", "abc")

        listener_mock1.assert_called_with("abc", 1, 2, 3)
        listener_mock2.assert_called_with("abc", 4, 5)

    def test_removing_a_listener(self):
        listener_mock1 = mock.Mock()
        listener_mock2 = mock.Mock()
        emitter = utils.EventEmitter()

        emitter.on("some_event", listener_mock1, 123)
        emitter.on("some_event", listener_mock1, 456)
        emitter.on("some_event", listener_mock2, 78)
        emitter.off("some_event", listener_mock1)
        emitter.emit("some_event")

        self.assertEqual(listener_mock1.call_count, 0)
        listener_mock2.assert_called_with(78)

    def test_removing_all_listeners_for_an_event(self):
        listener_mock1 = mock.Mock()
        listener_mock2 = mock.Mock()
        emitter = utils.EventEmitter()

        emitter.on("some_event", listener_mock1)
        emitter.on("some_event", listener_mock2)
        emitter.off("some_event")
        emitter.emit("some_event")

        self.assertEqual(listener_mock1.call_count, 0)
        self.assertEqual(listener_mock2.call_count, 0)

    def test_removing_all_listeners_for_all_events(self):
        listener_mock1 = mock.Mock()
        listener_mock2 = mock.Mock()
        emitter = utils.EventEmitter()

        emitter.on("some_event", listener_mock1)
        emitter.on("another_event", listener_mock2)
        emitter.off()
        emitter.emit("some_event")
        emitter.emit("another_event")

        self.assertEqual(listener_mock1.call_count, 0)
        self.assertEqual(listener_mock2.call_count, 0)

    def test_listener_returning_false_is_removed(self):
        listener_mock1 = mock.Mock(return_value=False)
        listener_mock2 = mock.Mock()
        emitter = utils.EventEmitter()

        emitter.on("some_event", listener_mock1)
        emitter.on("some_event", listener_mock2)
        emitter.emit("some_event")
        emitter.emit("some_event")

        self.assertEqual(listener_mock1.call_count, 1)
        self.assertEqual(listener_mock2.call_count, 2)

    def test_num_listeners_returns_total_number_of_listeners(self):
        listener_mock1 = mock.Mock()
        listener_mock2 = mock.Mock()
        emitter = utils.EventEmitter()

        self.assertEqual(emitter.num_listeners(), 0)

        emitter.on("some_event", listener_mock1)
        self.assertEqual(emitter.num_listeners(), 1)

        emitter.on("another_event", listener_mock1)
        emitter.on("another_event", listener_mock2)
        self.assertEqual(emitter.num_listeners(), 3)

    def test_num_listeners_returns_number_of_listeners_for_event(self):
        listener_mock1 = mock.Mock()
        listener_mock2 = mock.Mock()
        emitter = utils.EventEmitter()

        self.assertEqual(emitter.num_listeners("unknown_event"), 0)

        emitter.on("some_event", listener_mock1)
        self.assertEqual(emitter.num_listeners("some_event"), 1)

        emitter.on("another_event", listener_mock1)
        emitter.on("another_event", listener_mock2)
        self.assertEqual(emitter.num_listeners("another_event"), 2)

    def test_call_fails_if_zero_listeners_for_event(self):
        emitter = utils.EventEmitter()

        with self.assertRaises(AssertionError):
            emitter.call("some_event")

    def test_call_fails_if_multiple_listeners_for_event(self):
        listener_mock1 = mock.Mock()
        listener_mock2 = mock.Mock()
        emitter = utils.EventEmitter()

        emitter.on("some_event", listener_mock1)
        emitter.on("some_event", listener_mock2)

        with self.assertRaises(AssertionError):
            emitter.call("some_event")

    def test_call_calls_and_returns_result_of_a_single_listener(self):
        listener_mock = mock.Mock()
        emitter = utils.EventEmitter()

        emitter.on("some_event", listener_mock, 1, 2, 3)
        result = emitter.call("some_event", "abc")

        listener_mock.assert_called_with("abc", 1, 2, 3)
        self.assertEqual(result, listener_mock.return_value)


class IntEnumTest(unittest.TestCase):
    def setUp(self):
        class Foo(utils.IntEnum):
            pass

        self.Foo = Foo

        self.Foo.add("bar", 1)
        self.Foo.add("baz", 2)

    def test_has_pretty_repr(self):
        self.assertEqual(repr(self.Foo.bar), "<Foo.bar: 1>")
        self.assertEqual(repr(self.Foo.baz), "<Foo.baz: 2>")

    def test_is_equal_to_the_int_value(self):
        self.assertEqual(self.Foo.bar, 1)
        self.assertEqual(self.Foo.baz, 2)

    def test_two_instances_with_same_value_is_identical(self):
        self.assertIs(self.Foo(1), self.Foo.bar)
        self.assertIs(self.Foo(2), self.Foo.baz)
        self.assertIsNot(self.Foo(2), self.Foo.bar)
        self.assertIsNot(self.Foo(1), self.Foo.baz)


@mock.patch("spotify.search.lib", spec=spotify.lib)
class SequenceTest(unittest.TestCase):
    def test_adds_ref_to_sp_obj_when_created(self, lib_mock):
        sp_search = spotify.ffi.cast("sp_search *", 42)
        utils.Sequence(
            sp_obj=sp_search,
            add_ref_func=lib_mock.sp_search_add_ref,
            release_func=lib_mock.sp_search_release,
            len_func=None,
            getitem_func=None,
        )

        self.assertEqual(lib_mock.sp_search_add_ref.call_count, 1)

    def test_releases_sp_obj_when_sequence_dies(self, lib_mock):
        sp_search = spotify.ffi.cast("sp_search *", 42)
        seq = utils.Sequence(
            sp_obj=sp_search,
            add_ref_func=lib_mock.sp_search_add_ref,
            release_func=lib_mock.sp_search_release,
            len_func=None,
            getitem_func=None,
        )

        seq = None  # noqa
        tests.gc_collect()

        self.assertEqual(lib_mock.sp_search_release.call_count, 1)

    def test_len_calls_len_func(self, lib_mock):
        sp_search = spotify.ffi.cast("sp_search *", 42)
        len_func = mock.Mock()
        len_func.return_value = 0
        seq = utils.Sequence(
            sp_obj=sp_search,
            add_ref_func=lib_mock.sp_search_add_ref,
            release_func=lib_mock.sp_search_release,
            len_func=len_func,
            getitem_func=None,
        )

        result = len(seq)

        self.assertEqual(result, 0)
        len_func.assert_called_with(sp_search)

    def test_getitem_calls_getitem_func(self, lib_mock):
        sp_search = spotify.ffi.cast("sp_search *", 42)
        getitem_func = mock.Mock()
        getitem_func.return_value = mock.sentinel.item_one
        seq = utils.Sequence(
            sp_obj=sp_search,
            add_ref_func=lib_mock.sp_search_add_ref,
            release_func=lib_mock.sp_search_release,
            len_func=lambda x: 1,
            getitem_func=getitem_func,
        )

        result = seq[0]

        self.assertEqual(result, mock.sentinel.item_one)
        getitem_func.assert_called_with(sp_search, 0)

    def test_getitem_with_negative_index(self, lib_mock):
        sp_search = spotify.ffi.cast("sp_search *", 42)
        getitem_func = mock.Mock()
        getitem_func.return_value = mock.sentinel.item_one
        seq = utils.Sequence(
            sp_obj=sp_search,
            add_ref_func=lib_mock.sp_search_add_ref,
            release_func=lib_mock.sp_search_release,
            len_func=lambda x: 1,
            getitem_func=getitem_func,
        )

        result = seq[-1]

        self.assertEqual(result, mock.sentinel.item_one)
        getitem_func.assert_called_with(sp_search, 0)

    def test_getitem_with_slice(self, lib_mock):
        sp_search = spotify.ffi.cast("sp_search *", 42)
        getitem_func = mock.Mock()
        getitem_func.side_effect = [
            mock.sentinel.item_one,
            mock.sentinel.item_two,
            mock.sentinel.item_three,
        ]
        seq = utils.Sequence(
            sp_obj=sp_search,
            add_ref_func=lib_mock.sp_search_add_ref,
            release_func=lib_mock.sp_search_release,
            len_func=lambda x: 3,
            getitem_func=getitem_func,
        )

        result = seq[0:2]

        # Entire collection of length 3 is created as a list
        self.assertEqual(getitem_func.call_count, 3)

        # Only a subslice of length 2 is returned
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], mock.sentinel.item_one)
        self.assertEqual(result[1], mock.sentinel.item_two)

    def test_getitem_raises_index_error_on_too_low_index(self, lib_mock):
        sp_search = spotify.ffi.cast("sp_search *", 42)
        seq = utils.Sequence(
            sp_obj=sp_search,
            add_ref_func=lib_mock.sp_search_add_ref,
            release_func=lib_mock.sp_search_release,
            len_func=lambda x: 1,
            getitem_func=None,
        )

        with self.assertRaises(IndexError):
            seq[-3]

    def test_getitem_raises_index_error_on_too_high_index(self, lib_mock):
        sp_search = spotify.ffi.cast("sp_search *", 42)
        seq = utils.Sequence(
            sp_obj=sp_search,
            add_ref_func=lib_mock.sp_search_add_ref,
            release_func=lib_mock.sp_search_release,
            len_func=lambda x: 1,
            getitem_func=None,
        )

        with self.assertRaises(IndexError):
            seq[1]

    def test_getitem_raises_type_error_on_non_integral_index(self, lib_mock):
        sp_search = spotify.ffi.cast("sp_search *", 42)
        seq = utils.Sequence(
            sp_obj=sp_search,
            add_ref_func=lib_mock.sp_search_add_ref,
            release_func=lib_mock.sp_search_release,
            len_func=lambda x: 1,
            getitem_func=None,
        )

        with self.assertRaises(TypeError):
            seq["abc"]

    def test_repr(self, lib_mock):
        sp_search = spotify.ffi.cast("sp_search *", 42)
        seq = utils.Sequence(
            sp_obj=sp_search,
            add_ref_func=lib_mock.sp_search_add_ref,
            release_func=lib_mock.sp_search_release,
            len_func=lambda x: 1,
            getitem_func=lambda s, i: 123,
        )

        result = repr(seq)

        self.assertEqual(result, "Sequence([123])")


class ToBytesTest(unittest.TestCase):
    def test_unicode_to_bytes_is_encoded_as_utf8(self):
        self.assertEqual(utils.to_bytes("æøå"), "æøå".encode("utf-8"))

    def test_bytes_to_bytes_is_passed_through(self):
        self.assertEqual(utils.to_bytes("æøå".encode("utf-8")), "æøå".encode("utf-8"))

    def test_cdata_to_bytes_is_unwrapped(self):
        cdata = spotify.ffi.new("char[]", "æøå".encode("utf-8"))
        self.assertEqual(utils.to_bytes(cdata), "æøå".encode("utf-8"))

    def test_anything_else_to_bytes_fails(self):
        with self.assertRaises(ValueError):
            utils.to_bytes([])

        with self.assertRaises(ValueError):
            utils.to_bytes(123)


class ToBytesOrNoneTest(unittest.TestCase):
    def test_null_becomes_none(self):
        self.assertEqual(utils.to_bytes_or_none(spotify.ffi.NULL), None)

    def test_char_becomes_bytes(self):
        result = utils.to_bytes_or_none(spotify.ffi.new("char[]", b"abc"))

        self.assertEqual(result, b"abc")

    def test_anything_else_fails(self):
        with self.assertRaises(ValueError):
            utils.to_bytes_or_none(b"abc")


class ToUnicodeTest(unittest.TestCase):
    def test_unicode_to_unicode_is_passed_through(self):
        self.assertEqual(utils.to_unicode("æøå"), "æøå")

    def test_bytes_to_unicode_is_decoded_as_utf8(self):
        self.assertEqual(utils.to_unicode("æøå".encode("utf-8")), "æøå")

    def test_cdata_to_unicode_is_unwrapped_and_decoded_as_utf8(self):
        cdata = spotify.ffi.new("char[]", "æøå".encode("utf-8"))
        self.assertEqual(utils.to_unicode(cdata), "æøå")

    def test_anything_else_to_unicode_fails(self):
        with self.assertRaises(ValueError):
            utils.to_unicode([])

        with self.assertRaises(ValueError):
            utils.to_unicode(123)


class ToUnicodeOrNoneTest(unittest.TestCase):
    def test_null_becomes_none(self):
        self.assertEqual(utils.to_unicode_or_none(spotify.ffi.NULL), None)

    def test_char_becomes_bytes(self):
        result = utils.to_unicode_or_none(
            spotify.ffi.new("char[]", "æøå".encode("utf-8"))
        )

        self.assertEqual(result, "æøå")

    def test_anything_else_fails(self):
        with self.assertRaises(ValueError):
            utils.to_unicode_or_none("æøå")


class ToCharTest(unittest.TestCase):
    def test_bytes_becomes_char(self):
        result = utils.to_char(b"abc")

        self.assertIsInstance(result, spotify.ffi.CData)
        self.assertEqual(spotify.ffi.string(result), b"abc")

    def test_unicode_becomes_char(self):
        result = utils.to_char("æøå")

        self.assertIsInstance(result, spotify.ffi.CData)
        self.assertEqual(spotify.ffi.string(result).decode("utf-8"), "æøå")

    def test_anything_else_fails(self):
        with self.assertRaises(ValueError):
            utils.to_char(None)

        with self.assertRaises(ValueError):
            utils.to_char(123)


class ToCharOrNullTest(unittest.TestCase):
    def test_none_becomes_null(self):
        self.assertEqual(utils.to_char_or_null(None), spotify.ffi.NULL)

    def test_bytes_becomes_char(self):
        result = utils.to_char_or_null(b"abc")

        self.assertIsInstance(result, spotify.ffi.CData)
        self.assertEqual(spotify.ffi.string(result), b"abc")

    def test_unicode_becomes_char(self):
        result = utils.to_char_or_null("æøå")

        self.assertIsInstance(result, spotify.ffi.CData)
        self.assertEqual(spotify.ffi.string(result).decode("utf-8"), "æøå")

    def test_anything_else_fails(self):
        with self.assertRaises(ValueError):
            utils.to_char_or_null(123)


class ToCountryCodeTest(unittest.TestCase):
    def test_unicode_to_country_code(self):
        self.assertEqual(utils.to_country_code("NO"), 20047)
        self.assertEqual(utils.to_country_code("SE"), 21317)

    def test_bytes_to_country_code(self):
        self.assertEqual(utils.to_country_code(b"NO"), 20047)
        self.assertEqual(utils.to_country_code(b"SE"), 21317)

    def test_fails_if_not_exactly_two_chars(self):
        with self.assertRaises(ValueError):
            utils.to_country_code("NOR")

    def test_fails_if_not_in_uppercase(self):
        with self.assertRaises(ValueError):
            utils.to_country_code("no")


class ToCountryTest(unittest.TestCase):
    def test_to_country(self):
        self.assertEqual(utils.to_country(20047), "NO")
        self.assertEqual(utils.to_country(21317), "SE")
