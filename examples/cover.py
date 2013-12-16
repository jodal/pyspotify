import spotify

# Assuming a spotify_appkey.key in the current dir:
session = spotify.Session()

# Assuming a previous login with remember_me=True and a proper logout:
session.relogin()

# TODO Process events until logged in, not just once
session.process_events()

album = spotify.Album('spotify:album:4m2880jivSbbyEGAKfITCa').load()
cover = album.cover(spotify.ImageSize.LARGE).load()

open('/tmp/cover.jpg', 'w+').write(cover.data)
open('/tmp/cover.html', 'w+').write('<img src="%s">' % cover.data_uri)
