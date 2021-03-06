from __future__ import unicode_literals

import collections

from spotify import utils

__all__ = ["AudioBufferStats", "AudioFormat", "Bitrate", "SampleType"]


class AudioBufferStats(
    collections.namedtuple("AudioBufferStats", ["samples", "stutter"])
):

    """Stats about the application's audio buffers."""

    pass


@utils.make_enum("SP_BITRATE_", "BITRATE_")
class Bitrate(utils.IntEnum):
    pass


@utils.make_enum("SP_SAMPLETYPE_")
class SampleType(utils.IntEnum):
    pass


class AudioFormat(object):

    """A Spotify audio format object.

    You'll never need to create an instance of this class yourself, but you'll
    get :class:`AudioFormat` objects as the ``audio_format`` argument to the
    :attr:`~spotify.SessionCallbacks.music_delivery` callback.
    """

    def __init__(self, sp_audioformat):
        self._sp_audioformat = sp_audioformat

    @property
    def sample_type(self):
        """The :class:`SampleType`, currently always
        :attr:`SampleType.INT16_NATIVE_ENDIAN`."""
        return SampleType(self._sp_audioformat.sample_type)

    @property
    def sample_rate(self):
        """The sample rate, typically 44100 Hz."""
        return self._sp_audioformat.sample_rate

    @property
    def channels(self):
        """The number of audio channels, typically 2."""
        return self._sp_audioformat.channels

    def frame_size(self):
        """The byte size of a single frame of this format."""
        if self.sample_type == SampleType.INT16_NATIVE_ENDIAN:
            return 2 * self.channels
        else:
            raise ValueError("Unknown sample type: %d", self.sample_type)
