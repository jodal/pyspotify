from spotify import client, Link
import sys
import traceback
import time

class Client(client.Client):
    queued = False
    def logged_in(self, session, error):
        try:
            self.ctr = session.playlist_container()
        except:
            traceback.print_exc()

    def metadata_updated(self, session):
        try:
            for p in self.ctr:
                if p.is_loaded():
                    print p.name()
            if not self.queued:
                playlist = self.ctr[27]
                if playlist.is_loaded():
                    session.load(playlist[0])
                    session.play(1)
        except:
            traceback.print_exc()

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

