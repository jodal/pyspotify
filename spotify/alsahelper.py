# $Id$
#
# Copyright 2009 Doug Winter
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at 
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import alsaaudio

class AlsaController(object):

    """ Wrapper around alsa to make it simpler to control. Using this in a
    spotify client is very simple, just create one and then call
    music_delivery every time you get packets from spotify. """

    def __init__(self, mode=alsaaudio.PCM_NONBLOCK):
        self.out = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK, mode=mode)
        self.out.setformat(alsaaudio.PCM_FORMAT_S16_LE) # actually native endian
        self.__rate = None
        self.__periodsize = None
        self.__channels = None
        self.periodsize = 2048
        self.channels = 2
        self.rate = 44100

    def music_delivery(self, session, frames, frame_size, num_frames, sample_type, sample_rate, channels):
        """ Interface specifically provided to make it easy to play music from
        spotify. See the examples. """
        try:
            self.channels = 2
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
