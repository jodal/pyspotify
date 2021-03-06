from __future__ import unicode_literals

import time
import unittest

try:
    # Python 3
    import queue
except ImportError:
    # Python 2
    import Queue as queue

import spotify
from tests import mock


class EventLoopTest(unittest.TestCase):
    def setUp(self):
        self.timeout = 0.1
        self.session = mock.Mock(spec=spotify.Session)
        self.session.process_events.return_value = int(self.timeout * 1000)
        self.loop = spotify.EventLoop(self.session)

    def tearDown(self):
        self.loop.stop()
        while self.loop.is_alive():
            self.loop.join(1)

    def test_is_a_daemon_thread(self):
        self.assertTrue(self.loop.daemon)

    def test_has_a_descriptive_thread_name(self):
        self.assertEqual(self.loop.name, "SpotifyEventLoop")

    def test_can_be_started_and_stopped_and_joined(self):
        self.assertFalse(self.loop.is_alive())

        self.loop.start()
        self.assertTrue(self.loop.is_alive())

        self.loop.stop()
        self.loop.join(1)
        self.assertFalse(self.loop.is_alive())

    def test_start_registers_notify_main_thread_listener(self):
        self.loop.start()

        self.session.on.assert_called_once_with(
            spotify.SessionEvent.NOTIFY_MAIN_THREAD,
            self.loop._on_notify_main_thread,
        )

    def test_stop_unregisters_notify_main_thread_listener(self):
        self.loop.stop()

        self.session.off.assert_called_once_with(
            spotify.SessionEvent.NOTIFY_MAIN_THREAD,
            self.loop._on_notify_main_thread,
        )

    def test_run_immediately_process_events(self):
        self.loop._runnable = False  # Short circuit run()
        self.loop.run()

        self.session.process_events.assert_called_once_with()

    def test_processes_events_if_no_notify_main_thread_before_timeout(self):
        self.loop._queue = mock.Mock(spec=queue.Queue)
        self.loop._queue.get = lambda timeout: time.sleep(timeout)
        self.loop.start()

        time.sleep(0.25)
        self.loop.stop()
        self.assertGreaterEqual(self.session.process_events.call_count, 3)

    def test_puts_on_queue_on_notify_main_thread(self):
        self.loop._queue = mock.Mock(spec=queue.Queue)

        self.loop._on_notify_main_thread(self.session)

        self.loop._queue.put_nowait.assert_called_once_with(mock.ANY)

    def test_on_notify_main_thread_fails_nicely_if_queue_is_full(self):
        self.loop._queue = mock.Mock(spec=queue.Queue)
        self.loop._queue.put_nowait.side_effect = queue.Full

        self.loop._on_notify_main_thread(self.session)

        self.loop._queue.put_nowait.assert_called_once_with(mock.ANY)
