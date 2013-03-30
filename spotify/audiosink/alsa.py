import alsaaudio
import sys

from spotify.audiosink import BaseAudioSink


class AlsaSink(BaseAudioSink):
    """Audio sink wrapper for systems with ALSA, e.g. most Linux systems"""

    def __init__(self, **kwargs):
        super(AlsaSink, self).__init__(**kwargs)
        self._mode = kwargs.get('mode', alsaaudio.PCM_NONBLOCK)
        self._device = None
        self._period_size = kwargs.get('period_size', 8192)
        if sys.byteorder == 'little':
            self._format = alsaaudio.PCM_FORMAT_S16_LE
        elif sys.byteorder == 'big':
            self._format = alsaaudio.PCM_FORMAT_S16_BE
        self._paused = False

    def _close_device(self):
        if self._device:
            self._device.close()
            self._device = None
            self._paused = False
        # clear _call_cache to avoid memory leaks, because references to
        # bound methods of old Alsa devices would be stored there
        self._call_cache = {}

    def music_delivery(
            self, session, frames, frame_size, num_frames,
            sample_type, sample_rate, channels):
        if self._device is None:
            self._device = alsaaudio.PCM(mode=self._mode)
            self._device.setperiodsize(self._period_size)
            self._device.setformat(self._format)
        if num_frames == 0:
            # flush audio buffers on seek
            self._close_device()
            return 0
        self._call_if_needed(self._device.setrate, sample_rate)
        self._call_if_needed(self._device.setchannels, channels)
        return self._device.write(frames)

    def start(self):
        if self._device and self._paused:
            self._device.pause(0)
            self._paused = False

    def stop(self):
        if self._device:
            self._close_device()

    def pause(self):
        # We have to check if the device is paused, because Alsa raises
        # an error if it's paused again.
        if self._device and not self._paused:
            self._device.pause(1)
            self._paused = True
