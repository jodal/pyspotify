from __future__ import unicode_literals

import gc
import mock
import unittest

import spotify


@mock.patch('spotify.track.lib')
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
