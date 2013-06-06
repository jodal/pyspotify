from __future__ import unicode_literals

import gc
import mock
import unittest

import spotify


@mock.patch('spotify.track.lib', spec=spotify.lib)
class TrackTest(unittest.TestCase):

    def create_session(self, lib_mock):
        session = mock.sentinel.session
        session.sp_session = mock.sentinel.sp_session
        spotify.session_instance = session
        return session

    def tearDown(self):
        spotify.session_instance = None

    def assert_fails_if_no_session(self, lib_mock, func):
        spotify.session_instance = None
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track)

        self.assertRaises(RuntimeError, func, track)

    def assert_fails_if_error(self, lib_mock, func):
        self.create_session(lib_mock)
        lib_mock.sp_track_error.return_value = (
            spotify.ErrorType.BAD_API_VERSION)
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track)

        self.assertRaises(spotify.Error, func, track)

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

    def test_is_loaded(self, lib_mock):
        lib_mock.sp_track_is_loaded.return_value = 1
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track)

        result = track.is_loaded

        lib_mock.sp_track_is_loaded.assert_called_once_with(sp_track)
        self.assertTrue(result)

    def test_error(self, lib_mock):
        lib_mock.sp_track_error.return_value = int(
            spotify.ErrorType.IS_LOADING)
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track)

        result = track.error

        lib_mock.sp_track_error.assert_called_once_with(sp_track)
        self.assertIs(result, spotify.ErrorType.IS_LOADING)

    def test_is_loadable(self, lib_mock):
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track)

        self.assertIsInstance(track, spotify.Loadable)

    def test_offline_status(self, lib_mock):
        lib_mock.sp_track_error.return_value = spotify.ErrorType.OK
        lib_mock.sp_track_offline_get_status.return_value = 2
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track)

        result = track.offline_status

        lib_mock.sp_track_offline_get_status.assert_called_with(sp_track)
        self.assertIs(result, spotify.TrackOfflineStatus.DOWNLOADING)

    def test_offline_status_fails_if_error(self, lib_mock):
        lib_mock.sp_track_error.return_value = (
            spotify.ErrorType.BAD_API_VERSION)
        lib_mock.sp_track_offline_get_status.return_value = 2
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track)

        self.assertRaises(spotify.Error, lambda: track.offline_status)

    def test_availability(self, lib_mock):
        session = self.create_session(lib_mock)
        lib_mock.sp_track_error.return_value = spotify.ErrorType.OK
        lib_mock.sp_track_get_availability.return_value = 1
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track)

        result = track.availability

        lib_mock.sp_track_get_availability.assert_called_with(
            session.sp_session, sp_track)
        self.assertIs(result, spotify.TrackAvailability.AVAILABLE)

    def test_availability_fails_if_no_session(self, lib_mock):
        self.assert_fails_if_no_session(lib_mock, lambda t: t.availability)

    def test_availability_fails_if_error(self, lib_mock):
        self.assert_fails_if_error(lib_mock, lambda t: t.availability)

    def test_is_local(self, lib_mock):
        session = self.create_session(lib_mock)
        lib_mock.sp_track_error.return_value = spotify.ErrorType.OK
        lib_mock.sp_track_is_local.return_value = 1
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track)

        result = track.is_local

        lib_mock.sp_track_is_local.assert_called_with(
            session.sp_session, sp_track)
        self.assertTrue(result)

    def test_is_local_fails_if_no_session(self, lib_mock):
        self.assert_fails_if_no_session(lib_mock, lambda t: t.is_local)

    def test_is_local_fails_if_error(self, lib_mock):
        self.assert_fails_if_error(lib_mock, lambda t: t.is_local)

    def test_is_autolinked(self, lib_mock):
        session = self.create_session(lib_mock)
        lib_mock.sp_track_error.return_value = spotify.ErrorType.OK
        lib_mock.sp_track_is_autolinked.return_value = 1
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track)

        result = track.is_autolinked

        lib_mock.sp_track_is_autolinked.assert_called_with(
            session.sp_session, sp_track)
        self.assertTrue(result)

    def test_is_autolinked_fails_if_no_session(self, lib_mock):
        self.assert_fails_if_no_session(lib_mock, lambda t: t.is_autolinked)

    def test_is_autolinked_fails_if_error(self, lib_mock):
        self.assert_fails_if_error(lib_mock, lambda t: t.is_autolinked)

    def test_playable(self, lib_mock):
        session = self.create_session(lib_mock)
        lib_mock.sp_track_error.return_value = spotify.ErrorType.OK
        sp_track_playable = spotify.ffi.new('int *')
        lib_mock.sp_track_get_playable.return_value = sp_track_playable
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track)

        result = track.playable

        lib_mock.sp_track_get_playable.assert_called_with(
            session.sp_session, sp_track)
        lib_mock.sp_track_add_ref.assert_called_with(sp_track_playable)
        self.assertIsInstance(result, spotify.Track)
        self.assertEqual(result.sp_track, sp_track_playable)

    def test_playable_fails_if_no_session(self, lib_mock):
        self.assert_fails_if_no_session(lib_mock, lambda t: t.playable)

    def test_playable_fails_if_error(self, lib_mock):
        self.assert_fails_if_error(lib_mock, lambda t: t.playable)

    def test_is_placeholder(self, lib_mock):
        lib_mock.sp_track_error.return_value = spotify.ErrorType.OK
        lib_mock.sp_track_is_placeholder.return_value = 1
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track)

        result = track.is_placeholder

        lib_mock.sp_track_is_placeholder.assert_called_with(sp_track)
        self.assertTrue(result)

    def test_is_placeholder_fails_if_error(self, lib_mock):
        self.assert_fails_if_error(lib_mock, lambda t: t.is_placeholder)

    def test_is_starred(self, lib_mock):
        session = self.create_session(lib_mock)
        lib_mock.sp_track_error.return_value = spotify.ErrorType.OK
        lib_mock.sp_track_is_starred.return_value = 1
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track)

        result = track.is_starred

        lib_mock.sp_track_is_starred.assert_called_with(
            session.sp_session, sp_track)
        self.assertTrue(result)

    def test_is_starred_fails_if_no_session(self, lib_mock):
        self.assert_fails_if_no_session(lib_mock, lambda t: t.is_starred)

    def test_is_starred_fails_if_error(self, lib_mock):
        self.assert_fails_if_error(lib_mock, lambda t: t.is_starred)

    def test_name(self, lib_mock):
        lib_mock.sp_track_error.return_value = spotify.ErrorType.OK
        lib_mock.sp_track_name.return_value = spotify.ffi.new(
            'char[]', b'Foo Bar Baz')
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track)

        result = track.name

        lib_mock.sp_track_name.assert_called_once_with(sp_track)
        self.assertEqual(result, 'Foo Bar Baz')

    def test_name_fails_if_error(self, lib_mock):
        self.assert_fails_if_error(lib_mock, lambda t: t.name)

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

    def test_create_with_defaults(self, lib_mock):
        sp_track = spotify.ffi.new('int *')
        lib_mock.sp_localtrack_create.return_value = sp_track

        track = spotify.LocalTrack()

        self.assertEqual(track.sp_track, sp_track)
        lib_mock.sp_localtrack_create.assert_called_once_with(
            mock.ANY, mock.ANY, mock.ANY, -1)
        self.assertEqual(
            lib_mock.sp_localtrack_create.call_args[0][0], spotify.ffi.NULL)
        self.assertEqual(
            lib_mock.sp_localtrack_create.call_args[0][1], spotify.ffi.NULL)
        self.assertEqual(
            lib_mock.sp_localtrack_create.call_args[0][2], spotify.ffi.NULL)
        self.assertEqual(
            lib_mock.sp_localtrack_create.call_args[0][3], -1)


class TrackAvailability(unittest.TestCase):

    def test_has_constants(self):
        self.assertEqual(spotify.TrackAvailability.UNAVAILABLE, 0)
        self.assertEqual(spotify.TrackAvailability.AVAILABLE, 1)


class TrackOfflineStatusTest(unittest.TestCase):

    def test_has_constants(self):
        self.assertEqual(spotify.TrackOfflineStatus.NO, 0)
        self.assertEqual(spotify.TrackOfflineStatus.DOWNLOADING, 2)
