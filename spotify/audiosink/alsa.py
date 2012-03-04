import alsaaudio
import sys

from spotify.audiosink import BaseAudioSink

class AlsaSink(BaseAudioSink):
    """Audio sink wrapper for systems with ALSA, e.g. most Linux systems"""

    def __init__(self, **kwargs):
        super(AlsaSink, self).__init__(**kwargs)
        self._mode = kwargs.get('mode', alsaaudio.PCM_NORMAL)
        self._device = None
        if sys.byteorder == 'little':
            self._format = alsaaudio.PCM_FORMAT_S16_LE
        elif sys.byteorder == 'big':
            self._format = alsaaudio.PCM_FORMAT_S16_BE

    def music_delivery(self, session, frames, frame_size, num_frames,
            sample_type, sample_rate, channels):
        if self._device is None:
            self._device = alsaaudio.PCM(mode=self._mode)
        self._call_if_needed(self._device.setformat, self._format)
        self._call_if_needed(self._device.setperiodsize, num_frames)
        self._call_if_needed(self._device.setrate, sample_rate)
        self._call_if_needed(self._device.setchannels, channels)
        return self._device.write(frames)
