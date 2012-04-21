import pyaudio

from spotify.audiosink import BaseAudioSink

class PortAudioSink(BaseAudioSink):
    """
    Audio sink wrapper for systems with PortAudio installed, which may
    include Linux, Mac OS X, and Windows systems.
    """

    def __init__(self, **kwargs):
        super(PortAudioSink, self).__init__(**kwargs)
        self._device = pyaudio.PyAudio()
        self._stream = None

    def _setup_stream(self, sample_rate, channels):
        if self._stream is not None:
            self._stream.close()
            self._stream = None
        self._stream = self._device.open(rate=sample_rate, channels=channels,
                format=pyaudio.paInt16, output=True)

    def music_delivery(self, session, frames, frame_size, num_frames,
            sample_type, sample_rate, channels):
        self._call_if_needed(self._setup_stream, sample_rate, channels)
        self._stream.write(frames, num_frames=num_frames)
        return num_frames
