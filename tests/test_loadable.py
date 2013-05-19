from __future__ import unicode_literals

import mock
import unittest

import spotify


class Foo(spotify.Loadable):
    @property
    def is_loaded(self):
        return True


class FooWithError(Foo):
    def error(self):
        return spotify.Error(spotify.Error.OK)


@mock.patch('spotify.loadable.time')
@mock.patch('spotify.loadable.spotify.session_instance')
@mock.patch.object(Foo, 'is_loaded', new_callable=mock.PropertyMock)
class LoadableTest(unittest.TestCase):

    def test_load_processes_events_until_loaded(
            self, is_loaded_mock, session_mock, time_mock):
        is_loaded_mock.side_effect = [False, False, True]

        foo = Foo()
        foo.load()

        self.assertEqual(session_mock.process_events.call_count, 2)
        self.assertEqual(time_mock.sleep.call_count, 2)

    def test_load_raises_exception_on_error(
            self, is_loaded_mock, session_mock, time_mock):
        is_loaded_mock.side_effect = [False, False, True]

        foo = Foo()
        foo.error = mock.Mock(return_value=spotify.Error.OTHER_PERMANENT)
        self.assertRaises(spotify.Error, foo.load)

        self.assertEqual(session_mock.process_events.call_count, 1)
        self.assertEqual(time_mock.sleep.call_count, 0)

    def test_load_does_not_abort_on_is_loading_error(
            self, is_loaded_mock, session_mock, time_mock):
        is_loaded_mock.side_effect = [False, False, True]

        foo = Foo()
        foo.error = mock.Mock(return_value=spotify.Error.IS_LOADING)
        foo.load()

        self.assertEqual(session_mock.process_events.call_count, 2)
        self.assertEqual(time_mock.sleep.call_count, 2)
