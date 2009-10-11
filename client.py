from spotify import client, Link
import sys
import traceback
import time

class Client(client.Client):
    def logged_in(self, session, error):
        print "LOGGED IN CALLED"
        #print "Loading track..."
        #l = Link.from_string("spotify:track:35QLYzQCz629mzQeQiQCwb")
        #l = Link.from_string("spotify:track:3i1EXbQPWMjFWGzaJagAmr")
        #track = l.as_track()
        #print "Session is", session
        #try:
        #    session.load(track)
        #except Exception:
        #    traceback.print_exc()
        #print sys.stderr, "Playing track..."
        #session.play(1)

client = Client(sys.argv[1], sys.argv[2])
client.connect()

