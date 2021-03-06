from __future__ import unicode_literals

import unittest

import spotify
from tests import mock


class BaseSinkTest(object):
    def test_init_connects_to_music_delivery_event(self):
        self.session.on.assert_called_with(
            spotify.SessionEvent.MUSIC_DELIVERY, self.sink._on_music_delivery
        )

    def test_off_disconnects_from_music_delivery_event(self):
        self.assertEqual(self.session.off.call_count, 0)

        self.sink.off()

        self.session.off.assert_called_with(
            spotify.SessionEvent.MUSIC_DELIVERY, mock.ANY
        )

    def test_on_connects_to_music_delivery_event(self):
        self.assertEqual(self.session.on.call_count, 1)

        self.sink.off()
        self.sink.on()

        self.assertEqual(self.session.on.call_count, 2)


class AlsaSinkTest(unittest.TestCase, BaseSinkTest):
    def setUp(self):
        self.session = mock.Mock()
        self.session.num_listeners.return_value = 0
        self.alsaaudio = mock.Mock()
        self.alsaaudio.pcms = mock.Mock()
        with mock.patch.dict("sys.modules", {"alsaaudio": self.alsaaudio}):
            self.sink = spotify.AlsaSink(self.session)

    def test_off_closes_audio_device(self):
        device_mock = mock.Mock()
        self.sink._device = device_mock

        self.sink.off()

        device_mock.close.assert_called_with()
        self.assertIsNone(self.sink._device)

    def test_music_delivery_creates_device_if_needed(self):
        device = mock.Mock()
        self.alsaaudio.PCM.return_value = device
        audio_format = mock.Mock()
        audio_format.frame_size.return_value = 4
        audio_format.sample_type = spotify.SampleType.INT16_NATIVE_ENDIAN
        num_frames = 2048

        self.sink._on_music_delivery(
            mock.sentinel.session,
            audio_format,
            mock.sentinel.frames,
            num_frames,
        )

        # The ``device`` kwarg was added in pyalsaaudio 0.8
        self.alsaaudio.PCM.assert_called_with(
            mode=self.alsaaudio.PCM_NONBLOCK, device="default"
        )

        device.setformat.assert_called_with(mock.ANY)
        device.setrate.assert_called_with(audio_format.sample_rate)
        device.setchannels.assert_called_with(audio_format.channels)
        device.setperiodsize.assert_called_with(2048 * 4)

    def test_music_delivery_creates_device_with_alsaaudio_0_7(self):
        del self.alsaaudio.pcms  # Remove pyalsaudio 0.8 version marker
        device = mock.Mock()
        self.alsaaudio.PCM.return_value = device
        audio_format = mock.Mock()
        audio_format.frame_size.return_value = 4
        audio_format.sample_type = spotify.SampleType.INT16_NATIVE_ENDIAN
        num_frames = 2048

        self.sink._on_music_delivery(
            mock.sentinel.session,
            audio_format,
            mock.sentinel.frames,
            num_frames,
        )

        # The ``card`` kwarg was deprecated in pyalsaaudio 0.8
        self.alsaaudio.PCM.assert_called_with(
            mode=self.alsaaudio.PCM_NONBLOCK, card="default"
        )

    def test_sets_little_endian_format_if_little_endian_system(self):
        device = mock.Mock()
        self.alsaaudio.PCM.return_value = device
        audio_format = mock.Mock()
        audio_format.frame_size.return_value = 4
        audio_format.sample_type = spotify.SampleType.INT16_NATIVE_ENDIAN
        num_frames = 2048

        with mock.patch("spotify.sink.sys") as sys_mock:
            sys_mock.byteorder = "little"

            self.sink._on_music_delivery(
                mock.sentinel.session,
                audio_format,
                mock.sentinel.frames,
                num_frames,
            )

        device.setformat.assert_called_with(self.alsaaudio.PCM_FORMAT_S16_LE)

    def test_sets_big_endian_format_if_big_endian_system(self):
        device = mock.Mock()
        self.alsaaudio.PCM.return_value = device
        audio_format = mock.Mock()
        audio_format.frame_size.return_value = 4
        audio_format.sample_type = spotify.SampleType.INT16_NATIVE_ENDIAN
        num_frames = 2048

        with mock.patch("spotify.sink.sys") as sys_mock:
            sys_mock.byteorder = "big"

            self.sink._on_music_delivery(
                mock.sentinel.session,
                audio_format,
                mock.sentinel.frames,
                num_frames,
            )

        device.setformat.assert_called_with(self.alsaaudio.PCM_FORMAT_S16_BE)

    def test_music_delivery_writes_frames_to_stream(self):
        self.sink._device = mock.Mock()
        audio_format = mock.Mock()
        audio_format.sample_type = spotify.SampleType.INT16_NATIVE_ENDIAN

        num_consumed_frames = self.sink._on_music_delivery(
            mock.sentinel.session,
            audio_format,
            mock.sentinel.frames,
            mock.sentinel.num_frames,
        )

        self.sink._device.write.assert_called_with(mock.sentinel.frames)
        self.assertEqual(num_consumed_frames, self.sink._device.write.return_value)


class PortAudioSinkTest(unittest.TestCase, BaseSinkTest):
    def setUp(self):
        self.session = mock.Mock()
        self.session.num_listeners.return_value = 0
        self.pyaudio = mock.Mock()
        with mock.patch.dict("sys.modules", {"pyaudio": self.pyaudio}):
            self.sink = spotify.PortAudioSink(self.session)

    def test_init_creates_device(self):
        self.pyaudio.PyAudio.assert_called_with()
        self.assertEqual(self.sink._device, self.pyaudio.PyAudio.return_value)

    def test_off_closes_audio_stream(self):
        stream_mock = mock.Mock()
        self.sink._stream = stream_mock

        self.sink.off()

        stream_mock.close.assert_called_with()
        self.assertIsNone(self.sink._stream)

    def test_music_delivery_creates_stream_if_needed(self):
        audio_format = mock.Mock()
        audio_format.sample_type = spotify.SampleType.INT16_NATIVE_ENDIAN

        self.sink._on_music_delivery(
            mock.sentinel.session,
            audio_format,
            mock.sentinel.frames,
            mock.sentinel.num_frames,
        )

        self.sink._device.open.assert_called_with(
            format=self.pyaudio.paInt16,
            channels=audio_format.channels,
            rate=audio_format.sample_rate,
            output=True,
        )
        self.assertEqual(self.sink._stream, self.sink._device.open.return_value)

    def test_music_delivery_writes_frames_to_stream(self):
        self.sink._stream = mock.Mock()
        audio_format = mock.Mock()
        audio_format.sample_type = spotify.SampleType.INT16_NATIVE_ENDIAN

        num_consumed_frames = self.sink._on_music_delivery(
            mock.sentinel.session,
            audio_format,
            mock.sentinel.frames,
            mock.sentinel.num_frames,
        )

        self.sink._stream.write.assert_called_with(
            mock.sentinel.frames, num_frames=mock.sentinel.num_frames
        )
        self.assertEqual(num_consumed_frames, mock.sentinel.num_frames)
