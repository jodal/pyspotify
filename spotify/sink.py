from __future__ import unicode_literals

import sys

import spotify


class AlsaSink(object):
    """Audio sink for systems using ALSA, e.g. most Linux systems.

    This audio sink requires `pyalsaaudio
    <https://pypi.python.org/pypi/pyalsaaudio>`_. pyalsaaudio is probably
    packaged in your Linux distribution. For example, on Debian/Ubuntu you can
    install the package ``python-alsaaudio``.

    The ``card`` keyword argument is passed on to :class:`alsaaudio.PCM`.
    Please refer to the pyalsaaudio documentation for details.

    Example::

        >>> import spotify.sink
        >>> session = spotify.Session()
        >>> audio = spotify.sink.AlsaSink(session)
        >>> loop = spotify.EventLoop(session)
        >>> loop.start()
        # Login, etc...
        >>> track = session.get_track('spotify:track:3N2UhXZI4Gf64Ku3cCjz2g')
        >>> track.load()
        >>> session.player.load(track)
        >>> session.player.play()
        # Listen to music...
    """

    def __init__(self, session, card='default'):
        self._session = session
        self._card = card

        import alsaaudio  # Crash early if not available
        self._alsaaudio = alsaaudio
        self._device = None

        self.on()

    def on(self):
        """Turn on the audio sink.

        This is done automatically when the sink is instantiated, so you'll
        only need to call this method if you ever call :meth:`off` and want to
        turn the sink back on.
        """
        assert self._session.num_listeners(
            spotify.SessionEvent.MUSIC_DELIVERY) == 0
        self._session.on(
            spotify.SessionEvent.MUSIC_DELIVERY, self._on_music_delivery)

    def off(self):
        """Turn off the audio sink.

        This disconnects the sink from the relevant session events.
        """
        self._session.off(
            spotify.SessionEvent.MUSIC_DELIVERY, self._on_music_delivery)
        self._close_device()

    def _on_music_delivery(self, session, audio_format, frames, num_frames):
        # This method is called from an internal libspotify thread and must
        # not block in any way.

        assert (
            audio_format.sample_type == spotify.SampleType.INT16_NATIVE_ENDIAN)

        if self._device is None:
            self._device = self._alsaaudio.PCM(
                mode=self._alsaaudio.PCM_NONBLOCK, card=self._card)
            if sys.byteorder == 'little':
                self._device.setformat(self._alsaaudio.PCM_FORMAT_S16_LE)
            else:
                self._device.setformat(self._alsaaudio.PCM_FORMAT_S16_BE)
            self._device.setrate(audio_format.sample_rate)
            self._device.setchannels(audio_format.channels)
            self._device.setperiodsize(num_frames * audio_format.frame_size())

        return self._device.write(frames)

    def _close_device(self):
        if self._device is not None:
            self._device.close()
            self._device = None
