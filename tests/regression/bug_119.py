from __future__ import print_function

import logging
import sys
import threading
import time

import spotify

logger = logging.getLogger(__name__)


ALBUMS = [
    "spotify:album:02Zb13fM8k04tRwTfMUhe9",  # OK
    "spotify:album:3ph1ceuYuayuzoIJzPQji2",  # Fails
    "spotify:album:4IBQvwIbtDluogvDe2qpaB",  # Fails
    "spotify:album:5VppVyy751PTQWrfJbrJ4H",  # Fails
    "spotify:album:2cRMVS71c49Pf5SnIlJX3U",  # OK
    "spotify:album:6mulYcpWRDAiv7KIouWvyP",  # OK
    "spotify:album:02jqf49ws9bcTvXLPGtjbT",  # Fails
    "spotify:album:17orrZznh0gmxYtpNP47nK",  # Fails
    "spotify:album:5lnQLEUiVDkLbFJHXHQu9m",  # Fails
    "spotify:album:3ph1ceuYuayuzoIJzPQji2",  # Fails
]


def init():
    session = spotify.Session()
    loop = spotify.EventLoop(session)
    loop.start()
    return session


def login(session, username, password):
    logged_in_event = threading.Event()

    def logged_in_listener(session, error_type):
        logged_in_event.set()

    session.on(spotify.SessionEvent.LOGGED_IN, logged_in_listener)
    session.login(username, password)

    if not logged_in_event.wait(10):
        raise RuntimeError("Login timed out")

    while session.connection.state != spotify.ConnectionState.LOGGED_IN:
        time.sleep(0.1)


def logout(session):
    logged_out_event = threading.Event()

    def logged_out_listener(session):
        logged_out_event.set()

    session.on(spotify.SessionEvent.LOGGED_OUT, logged_out_listener)
    session.logout()

    if not logged_out_event.wait(10):
        raise RuntimeError("Logout timed out")


def get_albums(session):
    logger.info("Getting albums")
    for uri in ALBUMS:
        logger.info("Loading %s...", uri)
        try:
            album = session.get_album(uri)
            # album.browse()  # Add this line, and everything works
            logger.info(album.load(3).name)
        except spotify.Timeout:
            logger.warning("Timeout")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("Usage: %s USERNAME PASSWORD" % sys.argv[0])

    logging.basicConfig(level=logging.INFO)

    username, password = sys.argv[1], sys.argv[2]
    session = init()
    login(session, username, password)

    try:
        get_albums(session)
        logout(session)
    except KeyboardInterrupt:
        logout(session)
