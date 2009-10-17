from spotify import client, Link
import sys
import traceback
import time
import alsaaudio

class Client(client.Client):
    queued = False

    def __init__(self, *a, **kw):
        global out
        client.Client.__init__(self, *a, **kw)
        self.out = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK)
        self.out.setformat(alsaaudio.PCM_FORMAT_S16_LE)
        self.out.setperiodsize(160)

    def logged_in(self, session, error):
        try:
            self.ctr = session.playlist_container()
        except:
            traceback.print_exc()

    def metadata_updated(self, session):
        try:
            if not self.queued:
                playlist = self.ctr[27]
                if playlist.is_loaded():
                    if playlist[0].is_loaded():
                        session.load(playlist[0])
                        session.play(1)
                        self.queued = True
                        print "Playing", playlist[0].name()
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
            self.out.setchannels(channels)
            self.out.setrate(sample_rate)
            self.out.write(frames)
        except:
            traceback.print_exc()

client = Client(sys.argv[1], sys.argv[2])
client.connect()

