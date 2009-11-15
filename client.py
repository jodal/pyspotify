#!/usr/bin/env python
from spotify import client, Link
import sys
import traceback
import time
import alsaaudio
import Queue
import threading

class AudioData:

    def __init__(self, nsamples, rate, channels, samples):
        self.nsamples = nsamples
        self.rate = rate
        self.channels = channels
        self.samples = samples

class AlsaController(object):

    mode = alsaaudio.PCM_NORMAL

    def __init__(self):
        self.out = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK, mode=self.mode)
        self.out.setformat(alsaaudio.PCM_FORMAT_S16_LE) # actually native endian
        self.__rate = None
        self.__periodsize = None
        self.__channels = None
        self.periodsize = 2048
        self.channels = 2
        self.rate = 44100

    def getperiodsize(self):
        return self.__periodsize

    def setperiodsize(self, siz):
        if self.__periodsize != siz:
            self.out.setperiodsize(siz)
            self.__periodsize = siz

    periodsize = property(getperiodsize, setperiodsize)

    def getrate(self):
        return self.__rate

    def setrate(self, rate):
        if self.__rate != rate:
            self.out.setrate(rate)
            self.__rate = rate

    rate = property(getrate, setrate)

    def getchannels(self):
        return self.__channels

    def setchannels(self, channels):
        if self.__channels != channels:
            self.out.setchannels(channels)
            self.__channels = channels

    channels = property(getchannels, setchannels)

class AlsaPlayer(AlsaController, threading.Thread):

    def __init__(self, *a, **kw):
        threading.Thread.__init__(self, *a, **kw)
        AlsaController.__init__(self)
        self.queue = Queue.Queue(800)

    def run(self):
        while True:
            try:
                ad = self.queue.get(block=False)
            except Queue.Empty:
                print "empty"
                time.sleep(5)
                continue
            if ad.nsamples != self.periodsize:
                print "Sample count mismatch %d != %d" % (ad.nsamples, self.periodsize)
            self.rate = ad.rate
            self.channels = ad.channels
            self.out.write(ad.samples)

class PlayAutoTrack(object):
    queued = False
    playlist = 4
    track = 2

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
                playlist = self.ctr[self.playlist]
                if playlist.is_loaded():
                    if playlist[self.track].is_loaded():
                        session.load(playlist[self.track])
                        session.play(1)
                        self.start()
                        self.queued = True
                        print "Playing", playlist[self.track].name()
        except:
            traceback.print_exc()

    def start(self):
        pass

    def end_of_track(self, session):
        session.logout()

    def logged_out(self, sess):
        sys.exit(0)

class ThreadedClient(PlayAutoTrack, client.Client):

    def __init__(self, *a, **kw):
        client.Client.__init__(self, *a, **kw)
        self.player = AlsaPlayer()

    def start(self):
        self.player.start()

    def music_delivery(self, session, frames, frame_size, num_frames, sample_type, sample_rate, channels):
        print "delivery", frame_size, num_frames, sample_type, sample_rate, channels
        try:
            if frames == 0:
                return 0 # audio discontinuity, do nothing
            assert len(frames) == num_frames * 2 * channels
            ad = AudioData(num_frames, sample_rate, channels, frames)
            self.player.queue.put(ad, block=True)
            return num_frames
        except:
            traceback.print_exc()

class SynchronousClient(AlsaController, PlayAutoTrack, client.Client):

    mode = alsaaudio.PCM_NONBLOCK

    def __init__(self, *a, **kw):
        client.Client.__init__(self, *a, **kw)
        AlsaController.__init__(self)

    def music_delivery(self, session, frames, frame_size, num_frames, sample_type, sample_rate, channels):
        try:
            self.channels = 2
            self.periodsize = num_frames
            self.rate = sample_rate
            written = self.out.write(frames)
            return written
        except:
            traceback.print_exc()

Client = SynchronousClient

if __name__ == '__main__':
    import optparse
    op = optparse.OptionParser(version="%prog 0.1")
    op.add_option("-u", "--username", help="spotify username")
    op.add_option("-p", "--password", help="spotify password")
    (options, args) = op.parse_args()
    if not options.username or not options.password:
        op.print_help()
        raise SystemExit
    client = Client(options.username, options.password)
    client.connect()

