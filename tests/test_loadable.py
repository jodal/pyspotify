from __future__ import unicode_literals

import time
import unittest

import spotify
import tests
from spotify.utils import load
from tests import mock


class Foo(object):
    def __init__(self, session):
        self._session = session

    @property
    def is_loaded(self):
        return True

    def load(self, timeout=None):
        return load(self._session, self, timeout=timeout)


class FooWithError(Foo):
    @property
    def error(self):
        return spotify.Error(spotify.Error.OK)


@mock.patch("spotify.utils.time")
@mock.patch.object(Foo, "is_loaded", new_callable=mock.PropertyMock)
class LoadableTest(unittest.TestCase):
    def setUp(self):
        self.session = tests.create_session_mock()
        self.session.connection.state = spotify.ConnectionState.LOGGED_IN

    def test_load_raises_error_if_not_logged_in(self, is_loaded_mock, time_mock):
        is_loaded_mock.return_value = False
        self.session.connection.state = spotify.ConnectionState.LOGGED_OUT
        foo = Foo(self.session)

        with self.assertRaises(spotify.Error):
            foo.load()

    def test_load_raises_error_if_offline(self, is_loaded_mock, time_mock):
        is_loaded_mock.return_value = False
        self.session.connection.state = spotify.ConnectionState.OFFLINE
        foo = Foo(self.session)

        with self.assertRaises(spotify.Error):
            foo.load()

    def test_load_returns_immediately_if_offline_but_already_loaded(
        self, is_loaded_mock, time_mock
    ):
        is_loaded_mock.return_value = True
        self.session.connection.state = spotify.ConnectionState.OFFLINE
        foo = Foo(self.session)

        result = foo.load()

        self.assertEqual(result, foo)
        self.assertEqual(self.session.process_events.call_count, 0)

    def test_load_raises_error_when_timeout_is_reached(self, is_loaded_mock, time_mock):
        is_loaded_mock.return_value = False
        time_mock.time.side_effect = time.time
        foo = Foo(self.session)

        with self.assertRaises(spotify.Timeout):
            foo.load(timeout=0)

    def test_load_processes_events_until_loaded(self, is_loaded_mock, time_mock):
        is_loaded_mock.side_effect = [False, False, False, False, False, True]
        time_mock.time.side_effect = time.time

        foo = Foo(self.session)
        foo.load()

        self.assertEqual(self.session.process_events.call_count, 2)
        self.assertEqual(time_mock.sleep.call_count, 2)

    @mock.patch.object(FooWithError, "error", new_callable=mock.PropertyMock)
    def test_load_raises_exception_on_error(
        self, error_mock, is_loaded_mock, time_mock
    ):
        error_mock.side_effect = [
            spotify.ErrorType.IS_LOADING,
            spotify.ErrorType.OTHER_PERMANENT,
        ]
        is_loaded_mock.side_effect = [False, False, True]

        foo = FooWithError(self.session)

        with self.assertRaises(spotify.Error):
            foo.load()

        self.assertEqual(self.session.process_events.call_count, 1)
        self.assertEqual(time_mock.sleep.call_count, 0)

    def test_load_raises_exception_on_error_even_if_already_loaded(
        self, is_loaded_mock, time_mock
    ):
        is_loaded_mock.return_value = True

        foo = Foo(self.session)
        foo.error = spotify.ErrorType.OTHER_PERMANENT

        with self.assertRaises(spotify.Error):
            foo.load()

    def test_load_does_not_abort_on_is_loading_error(self, is_loaded_mock, time_mock):
        is_loaded_mock.side_effect = [False, False, False, False, False, True]
        time_mock.time.side_effect = time.time

        foo = Foo(self.session)
        foo.error = spotify.ErrorType.IS_LOADING
        foo.load()

        self.assertEqual(self.session.process_events.call_count, 2)
        self.assertEqual(time_mock.sleep.call_count, 2)

    def test_load_returns_self(self, is_loaded_mock, time_mock):
        is_loaded_mock.return_value = True

        foo = Foo(self.session)
        result = foo.load()

        self.assertEqual(result, foo)
