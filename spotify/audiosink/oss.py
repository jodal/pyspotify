import ossaudiodev
import sys

from spotify.audiosink import BaseAudioSink

class OssSink(BaseAudioSink):
    """Audio sink wrapper for systems with OSS, e.g. older Linux systems"""

    def __init__(self, **kwargs):
        super(OssSink, self).__init__(**kwargs)
        self._device = None
        if sys.byteorder == 'little':
            self._format = ossaudiodev.AFMT_S16_LE
        elif sys.byteorder == 'big':
            self._format = ossaudiodev.AFMT_S16_BE

    def music_delivery(self, session, frames, frame_size, num_frames,
            sample_type, sample_rate, channels):
        if num_frames == 0:
            if self._device is not None:
                self._device.close()
                self._device = None
            return 0
        if self._device is None:
            self._device = ossaudiodev.open('w')
            self._device.setparameters(self._format, channels, sample_rate)
        self._device.write(frames)
        return num_frames
