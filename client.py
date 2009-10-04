from spotify import client
import sys

class Client(client.Client):
    def logged_in(self, session, error):
        print "LOGGED IN CALLED"
        username = session.username()
        print "username", username
        print "display name", session.display_name()
        print "loaded", session.user_is_loaded()
        session.logout()
        sys.exit()

client = Client("winjer", "route66")
client.connect()

