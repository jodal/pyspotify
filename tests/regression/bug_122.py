import logging
import threading
import time

import spotify


def login(session, username, password):
    logged_in_event = threading.Event()

    def logged_in_listener(session, error_type):
        logged_in_event.set()

    session.on(spotify.SessionEvent.LOGGED_IN, logged_in_listener)
    session.login(username, password)

    if not logged_in_event.wait(10):
        raise RuntimeError('Login timed out')

    while session.connection_state != spotify.ConnectionState.LOGGED_IN:
        time.sleep(0.1)


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

session = spotify.Session()
loop = spotify.EventLoop(session)
loop.start()

login(session, username, password)

logger.debug('Getting playlist')
pl = session.get_playlist(
    'spotify:user:durden20:playlist:1chOHrXPCFcShCwB357MFX')
logger.debug('Got playlist %r %r', pl, pl._sp_playlist)
logger.debug('Loading playlist %r %r', pl, pl._sp_playlist)
pl.load()
logger.debug('Loaded playlist %r %r', pl, pl._sp_playlist)

print pl
print pl.tracks
