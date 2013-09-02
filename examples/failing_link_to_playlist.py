"""
This example should work, but fails to get the URIs of the playlists.
See related comment in :meth:`spotify.Link.__init__`.
"""

from __future__ import print_function

import time

import spotify

session = spotify.Session()
session.relogin()
session.process_events()

user = spotify.User('spotify:user:p3.no')
user.load()
user.published_playlists.load()

time.sleep(10)
session.process_events()

print('%d playlists found' % len(user.published_playlists))

for playlist in user.published_playlists:
    playlist.load()
    print('Loaded', playlist)

print(user.published_playlists)

session.logout()
session.process_events()
