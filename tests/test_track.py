from __future__ import unicode_literals

import mock
import unittest

import spotify
import tests


@mock.patch('spotify.track.lib', spec=spotify.lib)
class TrackTest(unittest.TestCase):

    def tearDown(self):
        spotify.session_instance = None

    def assert_fails_if_no_session(self, lib_mock, func):
        spotify.session_instance = None
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track=sp_track)

        with self.assertRaises(RuntimeError):
            func(track)

    def assert_fails_if_error(self, lib_mock, func):
        tests.create_session()
        lib_mock.sp_track_error.return_value = (
            spotify.ErrorType.BAD_API_VERSION)
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track=sp_track)

        with self.assertRaises(spotify.Error):
            func(track)

    def test_create_without_uri_or_sp_track_fails(self, lib_mock):
        with self.assertRaises(AssertionError):
            spotify.Track()

    @mock.patch('spotify.Link', spec=spotify.Link)
    def test_create_from_uri(self, link_mock, lib_mock):
        sp_track = spotify.ffi.new('int *')
        link_instance_mock = link_mock.return_value
        link_instance_mock.as_track.return_value = spotify.Track(
            sp_track=sp_track)
        uri = 'spotify:track:foo'

        result = spotify.Track(uri)

        link_mock.assert_called_with(uri)
        link_instance_mock.as_track.assert_called_with()
        lib_mock.sp_track_add_ref.assert_called_with(sp_track)
        self.assertEqual(result._sp_track, sp_track)

    @mock.patch('spotify.Link', spec=spotify.Link)
    def test_create_from_uri_fail_raises_error(self, link_mock, lib_mock):
        link_instance_mock = link_mock.return_value
        link_instance_mock.as_track.return_value = None
        uri = 'spotify:track:foo'

        with self.assertRaises(ValueError):
            spotify.Track(uri)

    def test_adds_ref_to_sp_track_when_created(self, lib_mock):
        sp_track = spotify.ffi.new('int *')

        spotify.Track(sp_track=sp_track)

        lib_mock.sp_track_add_ref.assert_called_with(sp_track)

    def test_releases_sp_track_when_track_dies(self, lib_mock):
        sp_track = spotify.ffi.new('int *')

        track = spotify.Track(sp_track=sp_track)
        track = None  # noqa
        tests.gc_collect()

        lib_mock.sp_track_release.assert_called_with(sp_track)

    @mock.patch('spotify.Link', spec=spotify.Link)
    def test_repr(self, link_mock, lib_mock):
        link_instance_mock = link_mock.return_value
        link_instance_mock.uri = 'foo'
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track=sp_track)

        result = repr(track)

        self.assertEqual(result, 'Track(%r)' % 'foo')

    def test_is_loaded(self, lib_mock):
        lib_mock.sp_track_is_loaded.return_value = 1
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track=sp_track)

        result = track.is_loaded

        lib_mock.sp_track_is_loaded.assert_called_once_with(sp_track)
        self.assertTrue(result)

    def test_error(self, lib_mock):
        lib_mock.sp_track_error.return_value = int(
            spotify.ErrorType.IS_LOADING)
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track=sp_track)

        result = track.error

        lib_mock.sp_track_error.assert_called_once_with(sp_track)
        self.assertIs(result, spotify.ErrorType.IS_LOADING)

    @mock.patch('spotify.utils.load')
    def test_load(self, load_mock, lib_mock):
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track=sp_track)

        track.load(10)

        load_mock.assert_called_with(track, timeout=10)

    def test_offline_status(self, lib_mock):
        lib_mock.sp_track_error.return_value = spotify.ErrorType.OK
        lib_mock.sp_track_offline_get_status.return_value = 2
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track=sp_track)

        result = track.offline_status

        lib_mock.sp_track_offline_get_status.assert_called_with(sp_track)
        self.assertIs(result, spotify.TrackOfflineStatus.DOWNLOADING)

    def test_offline_status_is_none_if_unloaded(self, lib_mock):
        lib_mock.sp_track_error.return_value = spotify.ErrorType.IS_LOADING
        lib_mock.sp_track_is_loaded.return_value = 0
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track=sp_track)

        result = track.offline_status

        lib_mock.sp_track_is_loaded.assert_called_with(sp_track)
        self.assertIsNone(result)

    def test_offline_status_fails_if_error(self, lib_mock):
        lib_mock.sp_track_error.return_value = (
            spotify.ErrorType.BAD_API_VERSION)
        lib_mock.sp_track_offline_get_status.return_value = 2
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track=sp_track)

        with self.assertRaises(spotify.Error):
            track.offline_status

    def test_availability(self, lib_mock):
        session = tests.create_session()
        lib_mock.sp_track_error.return_value = spotify.ErrorType.OK
        lib_mock.sp_track_get_availability.return_value = 1
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track=sp_track)

        result = track.availability

        lib_mock.sp_track_get_availability.assert_called_with(
            session._sp_session, sp_track)
        self.assertIs(result, spotify.TrackAvailability.AVAILABLE)

    def test_availability_is_none_if_unloaded(self, lib_mock):
        tests.create_session()
        lib_mock.sp_track_error.return_value = spotify.ErrorType.IS_LOADING
        lib_mock.sp_track_is_loaded.return_value = 0
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track=sp_track)

        result = track.availability

        lib_mock.sp_track_is_loaded.assert_called_with(sp_track)
        self.assertIsNone(result)

    def test_availability_fails_if_no_session(self, lib_mock):
        self.assert_fails_if_no_session(lib_mock, lambda t: t.availability)

    def test_availability_fails_if_error(self, lib_mock):
        self.assert_fails_if_error(lib_mock, lambda t: t.availability)

    def test_is_local(self, lib_mock):
        session = tests.create_session()
        lib_mock.sp_track_error.return_value = spotify.ErrorType.OK
        lib_mock.sp_track_is_local.return_value = 1
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track=sp_track)

        result = track.is_local

        lib_mock.sp_track_is_local.assert_called_with(
            session._sp_session, sp_track)
        self.assertTrue(result)

    def test_is_local_is_none_if_unloaded(self, lib_mock):
        tests.create_session()
        lib_mock.sp_track_error.return_value = spotify.ErrorType.OK
        lib_mock.sp_track_is_loaded.return_value = 0
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track=sp_track)

        result = track.is_local

        lib_mock.sp_track_is_loaded.assert_called_with(sp_track)
        self.assertIsNone(result)

    def test_is_local_fails_if_no_session(self, lib_mock):
        self.assert_fails_if_no_session(lib_mock, lambda t: t.is_local)

    def test_is_local_fails_if_error(self, lib_mock):
        self.assert_fails_if_error(lib_mock, lambda t: t.is_local)

    def test_is_autolinked(self, lib_mock):
        session = tests.create_session()
        lib_mock.sp_track_error.return_value = spotify.ErrorType.OK
        lib_mock.sp_track_is_autolinked.return_value = 1
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track=sp_track)

        result = track.is_autolinked

        lib_mock.sp_track_is_autolinked.assert_called_with(
            session._sp_session, sp_track)
        self.assertTrue(result)

    def test_is_autolinked_is_none_if_unloaded(self, lib_mock):
        tests.create_session()
        lib_mock.sp_track_error.return_value = spotify.ErrorType.OK
        lib_mock.sp_track_is_loaded.return_value = 0
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track=sp_track)

        result = track.is_autolinked

        lib_mock.sp_track_is_loaded.assert_called_with(sp_track)
        self.assertIsNone(result)

    def test_is_autolinked_fails_if_no_session(self, lib_mock):
        self.assert_fails_if_no_session(lib_mock, lambda t: t.is_autolinked)

    def test_is_autolinked_fails_if_error(self, lib_mock):
        self.assert_fails_if_error(lib_mock, lambda t: t.is_autolinked)

    def test_playable(self, lib_mock):
        session = tests.create_session()
        lib_mock.sp_track_error.return_value = spotify.ErrorType.OK
        sp_track_playable = spotify.ffi.new('int *')
        lib_mock.sp_track_get_playable.return_value = sp_track_playable
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track=sp_track)

        result = track.playable

        lib_mock.sp_track_get_playable.assert_called_with(
            session._sp_session, sp_track)
        lib_mock.sp_track_add_ref.assert_called_with(sp_track_playable)
        self.assertIsInstance(result, spotify.Track)
        self.assertEqual(result._sp_track, sp_track_playable)

    def test_playable_is_none_if_unloaded(self, lib_mock):
        tests.create_session()
        lib_mock.sp_track_error.return_value = spotify.ErrorType.IS_LOADING
        lib_mock.sp_track_is_loaded.return_value = 0
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track=sp_track)

        result = track.playable

        lib_mock.sp_track_is_loaded.assert_called_with(sp_track)
        self.assertIsNone(result)

    def test_playable_fails_if_no_session(self, lib_mock):
        self.assert_fails_if_no_session(lib_mock, lambda t: t.playable)

    def test_playable_fails_if_error(self, lib_mock):
        self.assert_fails_if_error(lib_mock, lambda t: t.playable)

    def test_is_placeholder(self, lib_mock):
        lib_mock.sp_track_error.return_value = spotify.ErrorType.OK
        lib_mock.sp_track_is_placeholder.return_value = 1
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track=sp_track)

        result = track.is_placeholder

        lib_mock.sp_track_is_placeholder.assert_called_with(sp_track)
        self.assertTrue(result)

    def test_is_placeholder_is_none_if_unloaded(self, lib_mock):
        lib_mock.sp_track_error.return_value = spotify.ErrorType.IS_LOADING
        lib_mock.sp_track_is_loaded.return_value = 0
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track=sp_track)

        result = track.is_placeholder

        lib_mock.sp_track_is_loaded.assert_called_with(sp_track)
        self.assertIsNone(result)

    def test_is_placeholder_fails_if_error(self, lib_mock):
        self.assert_fails_if_error(lib_mock, lambda t: t.is_placeholder)

    def test_is_starred(self, lib_mock):
        session = tests.create_session()
        lib_mock.sp_track_error.return_value = spotify.ErrorType.OK
        lib_mock.sp_track_is_starred.return_value = 1
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track=sp_track)

        result = track.starred

        lib_mock.sp_track_is_starred.assert_called_with(
            session._sp_session, sp_track)
        self.assertTrue(result)

    def test_is_starred_is_none_if_unloaded(self, lib_mock):
        tests.create_session()
        lib_mock.sp_track_error.return_value = spotify.ErrorType.OK
        lib_mock.sp_track_is_loaded.return_value = 0
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track=sp_track)

        result = track.starred

        lib_mock.sp_track_is_loaded.assert_called_with(sp_track)
        self.assertIsNone(result)

    def test_is_starred_fails_if_no_session(self, lib_mock):
        self.assert_fails_if_no_session(lib_mock, lambda t: t.starred)

    def test_is_starred_fails_if_error(self, lib_mock):
        self.assert_fails_if_error(lib_mock, lambda t: t.starred)

    def test_set_starred(self, lib_mock):
        session = tests.create_session()
        lib_mock.sp_track_set_starred.return_value = spotify.ErrorType.OK
        sp_track = spotify.ffi.cast('sp_track *', spotify.ffi.new('int *'))
        track = spotify.Track(sp_track=sp_track)

        track.starred = True

        lib_mock.sp_track_set_starred.assert_called_with(
            session._sp_session, mock.ANY, 1, 1)

    def test_set_starred_fails_if_error(self, lib_mock):
        tests.create_session()
        lib_mock.sp_track_set_starred.return_value = (
            spotify.ErrorType.BAD_API_VERSION)
        sp_track = spotify.ffi.cast('sp_track *', spotify.ffi.new('int *'))
        track = spotify.Track(sp_track=sp_track)

        with self.assertRaises(spotify.Error):
            track.starred = True

    def test_set_starred_fails_if_no_session(self, lib_mock):
        def func(track):
            track.starred = True
        self.assert_fails_if_no_session(lib_mock, func)

    @mock.patch('spotify.artist.lib', spec=spotify.lib)
    def test_artists(self, artist_lib_mock, lib_mock):
        lib_mock.sp_track_error.return_value = spotify.ErrorType.OK
        sp_artist = spotify.ffi.cast('sp_artist *', spotify.ffi.new('int *'))
        lib_mock.sp_track_num_artists.return_value = 1
        lib_mock.sp_track_artist.return_value = sp_artist
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track=sp_track)

        result = track.artists

        self.assertEqual(len(result), 1)
        lib_mock.sp_track_num_artists.assert_called_with(sp_track)

        item = result[0]
        self.assertIsInstance(item, spotify.Artist)
        self.assertEqual(item._sp_artist, sp_artist)
        self.assertEqual(lib_mock.sp_track_artist.call_count, 1)
        lib_mock.sp_track_artist.assert_called_with(sp_track, 0)
        artist_lib_mock.sp_artist_add_ref.assert_called_with(sp_artist)

    def test_artists_if_no_artists(self, lib_mock):
        lib_mock.sp_track_error.return_value = spotify.ErrorType.OK
        lib_mock.sp_track_num_artists.return_value = 0
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track=sp_track)

        result = track.artists

        self.assertEqual(len(result), 0)
        lib_mock.sp_track_num_artists.assert_called_with(sp_track)
        self.assertEqual(lib_mock.sp_track_artist.call_count, 0)

    def test_artists_if_unloaded(self, lib_mock):
        lib_mock.sp_track_error.return_value = spotify.ErrorType.OK
        lib_mock.sp_track_is_loaded.return_value = 0
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track=sp_track)

        result = track.artists

        lib_mock.sp_track_is_loaded.assert_called_with(sp_track)
        self.assertEqual(len(result), 0)

    def test_artists_fails_if_error(self, lib_mock):
        self.assert_fails_if_error(lib_mock, lambda t: t.artists)

    @mock.patch('spotify.album.lib', spec=spotify.lib)
    def test_album(self, album_lib_mock, lib_mock):
        lib_mock.sp_track_error.return_value = spotify.ErrorType.OK
        sp_album = spotify.ffi.new('int *')
        lib_mock.sp_track_album.return_value = sp_album
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track=sp_track)

        result = track.album

        lib_mock.sp_track_album.assert_called_with(sp_track)
        self.assertEqual(album_lib_mock.sp_album_add_ref.call_count, 1)
        self.assertIsInstance(result, spotify.Album)
        self.assertEqual(result._sp_album, sp_album)

    @mock.patch('spotify.album.lib', spec=spotify.lib)
    def test_album_if_unloaded(self, album_lib_mock, lib_mock):
        lib_mock.sp_track_error.return_value = spotify.ErrorType.OK
        lib_mock.sp_track_album.return_value = 0
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track=sp_track)

        result = track.album

        lib_mock.sp_track_album.assert_called_with(sp_track)
        self.assertIsNone(result)

    def test_album_fails_if_error(self, lib_mock):
        self.assert_fails_if_error(lib_mock, lambda t: t.album)

    def test_name(self, lib_mock):
        lib_mock.sp_track_error.return_value = spotify.ErrorType.OK
        lib_mock.sp_track_name.return_value = spotify.ffi.new(
            'char[]', b'Foo Bar Baz')
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track=sp_track)

        result = track.name

        lib_mock.sp_track_name.assert_called_once_with(sp_track)
        self.assertEqual(result, 'Foo Bar Baz')

    def test_name_is_none_if_unloaded(self, lib_mock):
        lib_mock.sp_track_error.return_value = spotify.ErrorType.OK
        lib_mock.sp_track_name.return_value = spotify.ffi.new('char[]', b'')
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track=sp_track)

        result = track.name

        lib_mock.sp_track_name.assert_called_once_with(sp_track)
        self.assertIsNone(result)

    def test_name_fails_if_error(self, lib_mock):
        self.assert_fails_if_error(lib_mock, lambda t: t.name)

    def test_duration(self, lib_mock):
        lib_mock.sp_track_error.return_value = spotify.ErrorType.OK
        lib_mock.sp_track_duration.return_value = 60000
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track=sp_track)

        result = track.duration

        lib_mock.sp_track_duration.assert_called_with(sp_track)
        self.assertEqual(result, 60000)

    def test_duration_is_none_if_unloaded(self, lib_mock):
        lib_mock.sp_track_error.return_value = spotify.ErrorType.OK
        lib_mock.sp_track_duration.return_value = 0
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track=sp_track)

        result = track.duration

        lib_mock.sp_track_duration.assert_called_with(sp_track)
        self.assertIsNone(result)

    def test_duration_fails_if_error(self, lib_mock):
        self.assert_fails_if_error(lib_mock, lambda t: t.duration)

    def test_popularity(self, lib_mock):
        lib_mock.sp_track_error.return_value = spotify.ErrorType.OK
        lib_mock.sp_track_popularity.return_value = 90
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track=sp_track)

        result = track.popularity

        lib_mock.sp_track_popularity.assert_called_with(sp_track)
        self.assertEqual(result, 90)

    def test_popularity_is_none_if_unloaded(self, lib_mock):
        lib_mock.sp_track_error.return_value = spotify.ErrorType.OK
        lib_mock.sp_track_is_loaded.return_value = 0
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track=sp_track)

        result = track.popularity

        lib_mock.sp_track_is_loaded.assert_called_with(sp_track)
        self.assertIsNone(result)

    def test_popularity_fails_if_error(self, lib_mock):
        self.assert_fails_if_error(lib_mock, lambda t: t.popularity)

    def test_disc(self, lib_mock):
        lib_mock.sp_track_error.return_value = spotify.ErrorType.OK
        lib_mock.sp_track_disc.return_value = 2
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track=sp_track)

        result = track.disc

        lib_mock.sp_track_disc.assert_called_with(sp_track)
        self.assertEqual(result, 2)

    def test_disc_is_none_if_unloaded(self, lib_mock):
        lib_mock.sp_track_error.return_value = spotify.ErrorType.OK
        lib_mock.sp_track_disc.return_value = 0
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track=sp_track)

        result = track.disc

        lib_mock.sp_track_disc.assert_called_with(sp_track)
        self.assertIsNone(result)

    def test_disc_fails_if_error(self, lib_mock):
        self.assert_fails_if_error(lib_mock, lambda t: t.disc)

    def test_index(self, lib_mock):
        lib_mock.sp_track_error.return_value = spotify.ErrorType.OK
        lib_mock.sp_track_index.return_value = 7
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track=sp_track)

        result = track.index

        lib_mock.sp_track_index.assert_called_with(sp_track)
        self.assertEqual(result, 7)

    def test_index_is_none_if_unloaded(self, lib_mock):
        lib_mock.sp_track_error.return_value = spotify.ErrorType.OK
        lib_mock.sp_track_index.return_value = 0
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track=sp_track)

        result = track.index

        lib_mock.sp_track_index.assert_called_with(sp_track)
        self.assertIsNone(result)

    def test_index_fails_if_error(self, lib_mock):
        self.assert_fails_if_error(lib_mock, lambda t: t.index)

    @mock.patch('spotify.Link', spec=spotify.Link)
    def test_link_creates_link_to_track(self, link_mock, lib_mock):
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track=sp_track)
        sp_link = spotify.ffi.new('int *')
        lib_mock.sp_link_create_from_track.return_value = sp_link
        link_mock.return_value = mock.sentinel.link

        result = track.link

        lib_mock.sp_link_create_from_track.asssert_called_once_with(
            sp_track, 0)
        link_mock.assert_called_once_with(sp_link=sp_link)
        self.assertEqual(result, mock.sentinel.link)

    @mock.patch('spotify.Link', spec=spotify.Link)
    def test_link_with_offset(self, link_mock, lib_mock):
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track=sp_track)
        sp_link = spotify.ffi.new('int *')
        lib_mock.sp_link_create_from_track.return_value = sp_link
        link_mock.return_value = mock.sentinel.link

        result = track.link_with_offset(90)

        lib_mock.sp_link_create_from_track.asssert_called_once_with(
            sp_track, 90)
        link_mock.assert_called_once_with(sp_link=sp_link)
        self.assertEqual(result, mock.sentinel.link)


@mock.patch('spotify.track.lib', spec=spotify.lib)
class LocalTrackTest(unittest.TestCase):

    def test_create(self, lib_mock):
        sp_track = spotify.ffi.new('int *')
        lib_mock.sp_localtrack_create.return_value = sp_track

        track = spotify.LocalTrack(
            artist='foo', title='bar', album='baz', length=210)

        self.assertEqual(track._sp_track, sp_track)
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

        self.assertEqual(track._sp_track, sp_track)
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
