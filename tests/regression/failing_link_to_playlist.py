# TODO This example should work, but fails to get the URIs of the playlists.

from __future__ import print_function

import logging
import time

import spotify

logging.basicConfig(level=logging.INFO)

# Assuming a spotify_appkey.key in the current dir:
session = spotify.Session()

# Assuming a previous login with remember_me=True and a proper logout:
session.relogin()

while session.connection.state != spotify.ConnectionState.LOGGED_IN:
    session.process_events()

user = session.get_user("spotify:user:p3.no").load()
user.published_playlists.load()

time.sleep(10)
session.process_events()

print("%d playlists found" % len(user.published_playlists))

for playlist in user.published_playlists:
    playlist.load()
    print("Loaded", playlist)

print(user.published_playlists)

session.logout()
session.process_events()
