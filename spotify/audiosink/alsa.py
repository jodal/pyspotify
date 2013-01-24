import alsaaudio
import sys

from spotify.audiosink import BaseAudioSink

class AlsaSink(BaseAudioSink):
    """Audio sink wrapper for systems with ALSA, e.g. most Linux systems"""

    def __init__(self, **kwargs):
        super(AlsaSink, self).__init__(**kwargs)
        self._mode = alsaaudio.PCM_NONBLOCK
        self._device = None
        self._periodesize = 8192
        if sys.byteorder == 'little':
            self._format = alsaaudio.PCM_FORMAT_S16_LE
        elif sys.byteorder == 'big':
            self._format = alsaaudio.PCM_FORMAT_S16_BE

    def _stop_device(self):
        if self._device:
            if hasattr(self._device, 'stop'):
                self._device.stop()
            else:
                self._device.close()
                self._device = None

    def music_delivery(self, session, frames, frame_size, num_frames,
            sample_type, sample_rate, channels):
        if self._device is None:
            self._device = alsaaudio.PCM(mode=self._mode)
            self._device.setperiodsize(self._periodesize)
            self._device.setformat(self._format)
        if num_frames == 0:
            # flush audio buffers on seek
            self._stop_device()
            return 0
        self._call_if_needed(self._device.setrate, sample_rate)
        self._call_if_needed(self._device.setchannels, channels)
        return self._device.write(frames)

    def stop(self):
        if self._device:
            self._stop_device()
