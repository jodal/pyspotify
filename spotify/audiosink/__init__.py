class BaseAudioSink(object):
    """
    :class:`BaseAudioSink` is an audio sink wrapper for different audio sinks
    like ALSA, OSS, and PortAudio. The wrapper is a perfect match for the
    :meth:`spotify.manager.SpotifySessionManager.music_delivery` method, making
    it easy to play audio data received from Spotify.

    Implementations of this interface include:

    - :class:`spotify.audiosink.alsa.AlsaController`
    - :class:`spotify.audiosink.oss.OssController`
    - :class:`spotify.audiosink.portaudio.PortAudioController`
    """

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
