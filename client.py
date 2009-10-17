from spotify import client, Link
import sys
import traceback
import time

class Client(client.Client):
    queued = False
    output = open("/tmp/music", "w")

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

    def music_delivery(self, session, frames, frame_size, num_frames, sample_type, sample_rate, channels):
        try:
            print "Music delivery called"
            print repr(frames)
            #print str(frames)
            print len(frames), "frame bytes"
            print frame_size, "frame size"
            print num_frames, "frames"
            print sample_type, "type"
            print sample_rate, "rate"
            print channels, "channels"
            self.output.write(frames)
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

