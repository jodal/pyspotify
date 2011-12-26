import alsaaudio

from spotify.audiosink import BaseAudioSink

class AlsaSink(BaseAudioSink):
    """Audio sink wrapper for systems with ALSA, e.g. most Linux systems"""

    def __init__(self, mode=alsaaudio.PCM_NORMAL):
        self.out = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK, mode=mode)
        self.out.setformat(alsaaudio.PCM_FORMAT_S16_LE) # actually native endian
        self.__rate = None
        self.__periodsize = None
        self.__channels = None
        self.periodsize = 2048
        self.channels = 2
        self.rate = 44100

    def music_delivery(self, session, frames, frame_size, num_frames,
            sample_type, sample_rate, channels):
        try:
            self.channels = channels
            self.periodsize = num_frames
            self.rate = sample_rate
            written = self.playsamples(frames)
            return written
        except:
            traceback.print_exc()

    def playsamples(self, samples):
        return self.out.write(samples)

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
