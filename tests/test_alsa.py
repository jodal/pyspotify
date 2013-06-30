# encoding: utf-8

import unittest

try:
    import alsaaudio
except ImportError:
    alsaaudio = False

if alsaaudio:
    from spotify.audiosink.alsa import AlsaSink


@unittest.skipUnless(alsaaudio, 'requires alsaaudio')
class TestAlsaSink(unittest.TestCase):

    def fake_music_delivery(self, audio, num_frames):
        sample_type = None
        sample_rate = 44100
        channels = 2
        frame_size = channels * 2 # 16bit audio
        frames = '\0' * frame_size * num_frames
        audio.music_delivery(None, frames, frame_size, num_frames,
                            sample_type, 44100, 2)

    def fake_play(self, audio, num_audio_deliveries, num_frames):
        audio.start()
        for _ in xrange(num_audio_deliveries):
            self.fake_music_delivery(audio, num_frames)

    def test_create(self):
        audio = AlsaSink()

    def test_paused_property(self):
        """tests the bug fixed in commit 0303477"""
        audio = AlsaSink()
        self.assertEqual(audio._paused, False)
        self.fake_play(audio, 2, 8192)
        audio.pause()
        self.assertEqual(audio._paused, True)
        self.fake_music_delivery(audio, 0) # simulates seek
        self.assertEqual(audio._paused, False)
        self.fake_play(audio, 2, 8192)
        audio.pause()
        self.fake_play(audio, 2, 8192)
