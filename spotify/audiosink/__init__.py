"""
The :mod:`spotify.audiosink` module provides audio sink wrappers for different
audio sinks like ALSA, OSS, and PortAudio.
"""

import traceback


AUDIO_SINKS = (
    ('spotify.audiosink.alsa', 'AlsaSink'),
    ('spotify.audiosink.oss', 'OssSink'),
    ('spotify.audiosink.portaudio', 'PortAudioSink'),
    ('spotify.audiosink.gstreamer', 'GstreamerSink'),
)


def import_audio_sink(audio_sinks=None):
    """
    Try to import each audio sink until one is successfully imported.

    The `audio_sinks` parameter specificies what audio sinks to import, in the
    given order. If `audio_sinks` is not provided, the list
    :attr:`spotify.audiosink.AUDIO_SINKS` will be used.

    :param audio_sinks: audio sinks to try to import
    :type audio_sinks: list of two-tuples of (modulename, classname)
    :return: the first audio sink that was successfully imported
    :rtype: class
    :raise: :exc:`ImportError` if no audio sinks can be imported
    """
    if audio_sinks is None:
        audio_sinks = AUDIO_SINKS
    error_messages = []
    for module, cls in audio_sinks:
        try:
            module = __import__(module, fromlist=[cls])
            cls = getattr(module, cls)
            return cls
        except ImportError:
            error_messages.append(
                "Tried to use %s.%s as audio sink, but failed:"
                % (module, cls))
            error_messages.append(traceback.format_exc())
    error_messages.append("Was not able to import any of the audio sinks")
    raise ImportError, "\n".join(error_messages)


class BaseAudioSink(object):
    """
    :class:`BaseAudioSink` provides the interface which is implemented by all
    audio sink wrappers in the :mod:`spotify.audiosink` module.

    The interface is a perfect match for the
    :meth:`spotify.manager.SpotifySessionManager.music_delivery` method, making
    it easy to play audio data received from Spotify.
    """

    def __init__(self, backend=None):
        self._call_cache = {}
        self.backend = backend

    def music_delivery(self, session, frames, frame_size, num_frames,
            sample_type, sample_rate, channels):
        """
        To use one of the bundled audio controllers in a Spotify client you
        develop, just call this method every time you get audio data from
        Spotify, e.g. from your implementation of
        :meth:`spotify.manager.SpotifySessionManager.music_delivery`.

        :param session: the current session
        :type session: :class:`spotify.Session`
        :param frames: the audio data
        :type frames: :class:`buffer`
        :param frame_size: bytes per frame
        :type frame_size: :class:`int`
        :param num_frames: number of frames in this delivery
        :type num_frames: :class:`int`
        :param sample_type: currently this is always 0 which means 16-bit
            signed native endian integer samples
        :type sample_type: :class:`int`
        :param sample_rate: audio sample rate, in samples per second
        :type sample_rate: :class:`int`
        :param channels: number of audio channels. Currently 1 or 2
        :type channels: :class:`int`
        :return: number of frames consumed
        :rtype: :class:`int`
        """
        raise NotImplementedError

    def end_of_track(self):
        self.backend.next()

    def start(self):
        """
        Should be called when audio output starts.

        This is a hook for the audio sink to do work just before the audio
        starts.
        """
        pass

    def stop(self):
        """
        Should be called when audio output stops.

        This is a hook for the audio sink to do work just after the audio
        stops.
        """
        pass

    def pause(self):
        """
        Should be called when audio output is paused.

        This is a hook for the audio sink to do work when the audio is paused.
        """
        pass

    def _call_if_needed(self, func, *args, **kwargs):
        """
        Calls the given function with the given arguments if the arguments have
        changed since the previous call to the function.
        """
        if (func not in self._call_cache
                or self._call_cache[func] != (args, kwargs)):
            self._call_cache[func] = (args, kwargs)
            func(*args, **kwargs)
