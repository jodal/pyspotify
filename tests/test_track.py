from __future__ import unicode_literals

import gc
import mock
import unittest

import spotify


@mock.patch('spotify.track.lib', spec=spotify.lib)
class TrackTest(unittest.TestCase):

    def test_adds_ref_to_sp_track_when_created(self, lib_mock):
        sp_track = spotify.ffi.new('int *')

        spotify.Track(sp_track)

        lib_mock.sp_track_add_ref.assert_called_with(sp_track)

    def test_releases_sp_track_when_track_dies(self, lib_mock):
        sp_track = spotify.ffi.new('int *')

        track = spotify.Track(sp_track)
        track = None  # noqa
        gc.collect()  # Needed for PyPy

        lib_mock.sp_track_release.assert_called_with(sp_track)

    @mock.patch('spotify.link.Link', spec=spotify.Link)
    def test_as_link_creates_link_to_track(self, link_mock, lib_mock):
        link_mock.return_value = mock.sentinel.link
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track)

        result = track.as_link()

        link_mock.assert_called_once_with(track, offset=0)
        self.assertEqual(result, mock.sentinel.link)

    @mock.patch('spotify.link.Link', spec=spotify.Link)
    def test_as_link_with_offset(self, link_mock, lib_mock):
        link_mock.return_value = mock.sentinel.link
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track)

        result = track.as_link(offset=90)

        link_mock.assert_called_once_with(track, offset=90)
        self.assertEqual(result, mock.sentinel.link)


@mock.patch('spotify.track.lib', spec=spotify.lib)
class LocalTrackTest(unittest.TestCase):

    def test_create(self, lib_mock):
        sp_track = spotify.ffi.new('int *')
        lib_mock.sp_localtrack_create.return_value = sp_track

        track = spotify.LocalTrack(
            artist='foo', title='bar', album='baz', length=210)

        self.assertEqual(track.sp_track, sp_track)
        lib_mock.sp_localtrack_create.assert_called_once_with(
            mock.ANY, mock.ANY, mock.ANY, 210)
        self.assertEqual(
            spotify.ffi.string(lib_mock.sp_localtrack_create.call_args[0][0]),
            b'foo')
        self.assertEqual(
            spotify.ffi.string(lib_mock.sp_localtrack_create.call_args[0][1]),
            b'bar')
        self.assertEqual(
            spotify.ffi.string(lib_mock.sp_localtrack_create.call_args[0][2]),
            b'baz')
        self.assertEqual(
            lib_mock.sp_localtrack_create.call_args[0][3], 210)

        # Since we *created* the sp_track, we already have a refcount of 1 and
        # shouldn't increase the refcount when wrapping this sp_track in a
        # Track object
        self.assertEqual(lib_mock.sp_track_add_ref.call_count, 0)
