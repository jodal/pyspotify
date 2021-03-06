import spotify

# Assuming a spotify_appkey.key in the current dir:
session = spotify.Session()

# Assuming a previous login with remember_me=True and a proper logout:
session.relogin()

while session.connection.state != spotify.ConnectionState.LOGGED_IN:
    session.process_events()

album = session.get_album("spotify:album:4m2880jivSbbyEGAKfITCa").load()
cover = album.cover(spotify.ImageSize.LARGE).load()

open("/tmp/cover.jpg", "wb").write(cover.data)
open("/tmp/cover.html", "w").write('<img src="%s">' % cover.data_uri)
