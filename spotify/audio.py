from __future__ import unicode_literals

from spotify.utils import enum


@enum('SP_SAMPLETYPE_')
class SampleType(object):
    pass


class AudioFormat(object):
    """A Spotify audio format."""

    def __init__(self, sp_audioformat):
        self.sp_audioformat = sp_audioformat

    @property
    def sample_type(self):
        """The :class:`SampleType`, currently always
        :attr:`SampleType.INT16_NATIVE_ENDIAN`."""
        return self.sp_audioformat.sample_type

    @property
    def sample_rate(self):
        """The sample rate, typically 44100 Hz."""
        return self.sp_audioformat.sample_rate

    @property
    def channels(self):
        """The number of audio channels, typically 2."""
        return self.sp_audioformat.channels

    def frame_size(self):
        """The byte size of a single frame of this format."""
        if self.sample_type == SampleType.INT16_NATIVE_ENDIAN:
            return 2 * self.channels
        else:
            raise ValueError('Unknown sample type: %d', self.sample_type)
