import pyaudio
import traceback

class PortAudioController(object):
    def __init__(self, mode=None):
        self.out = pyaudio.PyAudio()
        self.__rate = None
        self.__periodsize = None
        self.__channels = None
        self.periodsize = 2048
        self.channels = 2
        self.rate = 44100
        self.stream = self.out.open(format=pyaudio.paInt16,
            frames_per_buffer=self.periodsize, channels=self.channels,
            rate=self.rate, output=True)

    def _reconfigure_stream(self):
        """
        reopen the stream with new channel, rate settings
        """
        self.stream.close()
        self.stream = self.out.open(format=pyaudio.paInt16,
            frames_per_buffer=self.periodsize, channels=self.channels,
            rate=self.rate, output=True)

    def music_delivery(self, session, frames, frame_size, num_frames, sample_type, sample_rate, channels):
        """ Interface specifically provided to make it easy to play music from
        spotify. See the examples. """
        try:
            self.channels = channels
            self.periodsize = num_frames
            self.rate = sample_rate
            written = self.playsamples(frames)
            return written
        except:
            traceback.print_exc()

    def playsamples(self, samples):
        self.stream.write(samples, num_frames= self.__periodsize)
        return self.__periodsize

    def getperiodsize(self):
        return self.__periodsize

    def setperiodsize(self, siz):
        if self.__periodsize != siz:
            self.__periodsize = siz

    periodsize = property(getperiodsize, setperiodsize)

    def getrate(self):
        return self.__rate

    def setrate(self, rate):
        if self.__rate != rate:
            self.__rate = rate
            if hasattr(self, 'stream'):
                self._reconfigure_stream

    rate = property(getrate, setrate)

    def getchannels(self):
        return self.__channels

    def setchannels(self, channels):
        if self.__channels != channels:
            self.__channels = channels
            if hasattr(self, 'stream'):
                self._reconfigure_stream

    channels = property(getchannels, setchannels)
