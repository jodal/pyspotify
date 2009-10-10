from spotify import client, Link
import sys

class Client(client.Client):
    def logged_in(self, session, error):
        print "LOGGED IN CALLED"
        username = session.username()
        print "username", username
        print "display name", session.display_name()
        print "loaded", session.user_is_loaded()
        track = Link.as_track("spotify:track:35QLYzQCz629mzQeQiQCwb")
        session.load(track)
        session.play()
        session.logout()
        sys.exit()

client = Client(sys.argv[1], sys.argv[2])
client.connect()

