from spotify import client, Link
import sys
import traceback
import time
import alsaaudio
import Queue
import threading

class AlsaPlayer(threading.Thread):

    def __init__(self, *a, **kw):
        threading.Thread.__init__(self, *a, **kw)
        self.queue = Queue.Queue()
        self.out = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK)
        self.out.setformat(alsaaudio.PCM_FORMAT_S16_LE) # actually native endian
        self.out.setperiodsize(2048)
        self.out.setchannels(2)
        self.out.setrate(44100)

    def run(self):
        while True:
            # each of these calls will block as appropriate
            data = self.queue.get()
            print self.out.write(data)

class Client(client.Client):
    queued = False

    def __init__(self, *a, **kw):
        client.Client.__init__(self, *a, **kw)
        self.player = AlsaPlayer()

    def logged_in(self, session, error):
        print "logged_in"
        try:
            self.ctr = session.playlist_container()
            print "Got playlist container", repr(self.ctr)
        except:
            traceback.print_exc()

    def metadata_updated(self, session):
        print "metadata_updated called"
        try:
            if not self.queued:
                playlist = self.ctr[27]
                if playlist.is_loaded():
                    if playlist[0].is_loaded():
                        session.load(playlist[0])
                        session.play(1)
                        self.player.start()
                        self.queued = True
                        print "Playing", playlist[0].name()
        except:
            traceback.print_exc()

    def music_delivery(self, session, frames, frame_size, num_frames, sample_type, sample_rate, channels):
        try:
            if self.player.queue.full():
                print "Queue full"
                return 0
            else:
                self.player.queue.put(frames)
                return num_frames
        except:
            traceback.print_exc()

client = Client(sys.argv[1], sys.argv[2])
client.connect()

