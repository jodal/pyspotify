from __future__ import unicode_literals

import mock
import unittest
import time

import spotify
from spotify.utils import load


class Foo(object):
    @property
    def is_loaded(self):
        return True

    def load(self, timeout=None):
        return load(self, timeout=timeout)


class FooWithError(Foo):
    def error(self):
        return spotify.Error(spotify.Error.OK)


@mock.patch('spotify.utils.time')
@mock.patch('spotify.utils.spotify.session_instance')
@mock.patch.object(Foo, 'is_loaded', new_callable=mock.PropertyMock)
class LoadableTest(unittest.TestCase):

    def test_load_raises_error_if_session_doesnt_exist(
            self, is_loaded_mock, session_mock, time_mock):
        spotify.session_instance = None
        foo = Foo()

        with self.assertRaises(RuntimeError):
            foo.load()

    def test_load_raises_error_if_not_logged_in(
            self, is_loaded_mock, session_mock, time_mock):
        spotify.session_instance = mock.Mock(spec=spotify.Session)
        spotify.session_instance.user = None
        foo = Foo()

        with self.assertRaises(RuntimeError):
            foo.load()

    def test_load_raises_error_when_timeout_is_reached(
            self, is_loaded_mock, session_mock, time_mock):
        is_loaded_mock.return_value = False
        time_mock.time.side_effect = time.time
        foo = Foo()

        with self.assertRaises(spotify.Timeout):
            foo.load(timeout=0)

    def test_load_processes_events_until_loaded(
            self, is_loaded_mock, session_mock, time_mock):
        is_loaded_mock.side_effect = [False, False, True]
        time_mock.time.side_effect = time.time

        foo = Foo()
        foo.load()

        self.assertEqual(session_mock.process_events.call_count, 2)
        self.assertEqual(time_mock.sleep.call_count, 2)

    def test_load_raises_exception_on_error(
            self, is_loaded_mock, session_mock, time_mock):
        is_loaded_mock.side_effect = [False, False, True]

        foo = Foo()
        foo.error = spotify.ErrorType.OTHER_PERMANENT

        with self.assertRaises(spotify.Error):
            foo.load()

        self.assertEqual(session_mock.process_events.call_count, 1)
        self.assertEqual(time_mock.sleep.call_count, 0)

    def test_load_raises_exception_on_error_even_if_already_loaded(
            self, is_loaded_mock, session_mock, time_mock):
        is_loaded_mock.return_value = True

        foo = Foo()
        foo.error = spotify.ErrorType.OTHER_PERMANENT

        with self.assertRaises(spotify.Error):
            foo.load()

    def test_load_does_not_abort_on_is_loading_error(
            self, is_loaded_mock, session_mock, time_mock):
        is_loaded_mock.side_effect = [False, False, True]
        time_mock.time.side_effect = time.time

        foo = Foo()
        foo.error = spotify.ErrorType.IS_LOADING
        foo.load()

        self.assertEqual(session_mock.process_events.call_count, 2)
        self.assertEqual(time_mock.sleep.call_count, 2)

    def test_load_returns_self(
            self, is_loaded_mock, session_mock, time_mock):
        is_loaded_mock.return_value = True

        foo = Foo()
        result = foo.load()

        self.assertEqual(result, foo)
