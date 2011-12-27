import ossaudiodev

from spotify.audiosink import BaseAudioSink

class OssSink(BaseAudioSink):
    """Audio sink wrapper for systems with OSS, e.g. older Linux systems"""

    def __init__(self):
        self.out = None
        self.__rate = None
        self.__periodsize = 2048 # unused for OSS
        self.__channels = None

    def music_delivery(self, session, frames, frame_size, num_frames,
            sample_type, sample_rate, channels):
        if num_frames == 0:
            if self.out is not None:
                self.out.close()
                self.out = None
            return 0
        if self.out is None:
            self.out = ossaudiodev.open("w")
            self.out.setfmt(ossaudiodev.AFMT_S16_LE) # actually native endian
            self.__channels = self.out.channels(channels)
            self.out.speed(sample_rate)
        return self.playsamples(frames)

    def playsamples(self, samples):
        written = self.out.write(samples)
        return written/(2*self.__channels)

    def getperiodsize(self):
        return self.__periodsize

    def setperiodsize(self, siz):
        self.__periodsize = siz

    periodsize = property(getperiodsize, setperiodsize)

    def getrate(self):
        return self.__rate

    def setrate(self, rate):
        if self.__rate != rate:
            self.__rate = self.out.speed(rate)

    rate = property(getrate, setrate)

    def getchannels(self):
        return self.__channels

    def setchannels(self, channels):
        if self.__channels != channels:
            self.__channels = self.out.channels(channels)

    channels = property(getchannels, setchannels)
