from __future__ import unicode_literals

import logging
import threading

try:
    # Python 3
    import queue
except ImportError:
    # Python 2
    import Queue as queue

import spotify

__all__ = ["EventLoop"]

logger = logging.getLogger(__name__)


class EventLoop(threading.Thread):

    """Event loop for automatically processing events from libspotify.

    The event loop is a :class:`~threading.Thread` that listens to
    :attr:`~spotify.SessionEvent.NOTIFY_MAIN_THREAD` events and calls
    :meth:`~spotify.Session.process_events` when needed.

    To use it, pass it your :class:`~spotify.Session` instance and call
    :meth:`start`::

        >>> session = spotify.Session()
        >>> event_loop = spotify.EventLoop(session)
        >>> event_loop.start()

    The event loop thread is a daemon thread, so it will not stop your
    application from exiting. If you wish to stop the event loop without
    stopping your entire application, call :meth:`stop`. You may call
    :meth:`~threading.Thread.join` to block until the event loop thread has
    finished, just like for any other thread.

    .. warning::

        If you use :class:`EventLoop` to process the libspotify events, any
        event listeners you've registered will be called from the event loop
        thread. pyspotify itself is thread safe, but you'll need to ensure that
        you have proper synchronization in your own application code, as always
        when working with threads.
    """

    daemon = True
    name = "SpotifyEventLoop"

    def __init__(self, session):
        threading.Thread.__init__(self)

        self._session = session
        self._runnable = True
        self._queue = queue.Queue()

    def start(self):
        """Start the event loop."""
        self._session.on(
            spotify.SessionEvent.NOTIFY_MAIN_THREAD, self._on_notify_main_thread
        )
        threading.Thread.start(self)

    def stop(self):
        """Stop the event loop."""
        self._runnable = False
        self._session.off(
            spotify.SessionEvent.NOTIFY_MAIN_THREAD, self._on_notify_main_thread
        )

    def run(self):
        logger.debug("Spotify event loop started")
        timeout = self._session.process_events() / 1000.0
        while self._runnable:
            try:
                logger.debug("Waiting %.3fs for new events", timeout)
                self._queue.get(timeout=timeout)
            except queue.Empty:
                logger.debug("Timeout reached; processing events")
            else:
                logger.debug("Notification received; processing events")
            finally:
                timeout = self._session.process_events() / 1000.0
        logger.debug("Spotify event loop stopped")

    def _on_notify_main_thread(self, session):
        # WARNING: This event listener is called from an internal libspotify
        # thread. It must not block.
        try:
            self._queue.put_nowait(1)
        except queue.Full:
            logger.warning(
                "pyspotify event loop queue full; dropped notification event"
            )
