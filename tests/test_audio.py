from __future__ import unicode_literals

import unittest

import spotify


class AudioBufferStatsTest(unittest.TestCase):

    def test_samples(self):
        stats = spotify.AudioBufferStats(100, 5)

        self.assertEqual(stats.samples, 100)

    def test_stutter(self):
        stats = spotify.AudioBufferStats(100, 5)

        self.assertEqual(stats.stutter, 5)


class AudioFormatTest(unittest.TestCase):

    def setUp(self):
        self.sp_audioformat = spotify.ffi.new('sp_audioformat *')
        self.sp_audioformat.sample_type = (
            spotify.SampleType.INT16_NATIVE_ENDIAN)
        self.sp_audioformat.sample_rate = 44100
        self.sp_audioformat.channels = 2
        self.audio_format = spotify.AudioFormat(self.sp_audioformat)

    def test_sample_type(self):
        self.assertEqual(
            self.audio_format.sample_type,
            spotify.SampleType.INT16_NATIVE_ENDIAN)

    def test_sample_rate(self):
        self.assertEqual(self.audio_format.sample_rate, 44100)

    def test_channels(self):
        self.assertEqual(self.audio_format.channels, 2)

    def test_frame_size(self):
        # INT16 means 16 bits aka 2 bytes per channel
        self.sp_audioformat.sample_type = (
            spotify.SampleType.INT16_NATIVE_ENDIAN)

        self.sp_audioformat.channels = 1
        self.assertEqual(self.audio_format.frame_size(), 2)

        self.sp_audioformat.channels = 2
        self.assertEqual(self.audio_format.frame_size(), 4)

    def test_frame_size_fails_if_sample_type_is_unknown(self):
        self.sp_audioformat.sample_type = 666

        self.assertRaises(ValueError, self.audio_format.frame_size)


class SampleTypeTest(unittest.TestCase):

    def test_has_constants(self):
        self.assertEqual(spotify.SampleType.INT16_NATIVE_ENDIAN, 0)
