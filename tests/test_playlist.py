# encoding: utf-8

from __future__ import unicode_literals

import collections
import mock
import unittest

import spotify
from spotify.playlist import _PlaylistCallbacks, _PlaylistContainerCallbacks
import tests


@mock.patch('spotify.playlist.lib', spec=spotify.lib)
class PlaylistTest(unittest.TestCase):

    def tearDown(self):
        spotify.session_instance = None

    def test_create_without_uri_or_sp_playlist_fails(self, lib_mock):
        with self.assertRaises(AssertionError):
            spotify.Playlist()

    @mock.patch('spotify.Link', spec=spotify.Link)
    def test_create_from_uri(self, link_mock, lib_mock):
        sp_playlist = spotify.ffi.new('int *')
        link_instance_mock = link_mock.return_value
        link_instance_mock.as_playlist.return_value = spotify.Playlist(
            sp_playlist=sp_playlist)
        uri = 'spotify:playlist:foo'

        result = spotify.Playlist(uri)

        link_mock.assert_called_with(uri)
        link_instance_mock.as_playlist.assert_called_with()
        lib_mock.sp_playlist_add_ref.assert_called_with(sp_playlist)
        self.assertEqual(result._sp_playlist, sp_playlist)

    @mock.patch('spotify.Link', spec=spotify.Link)
    def test_create_from_uri_fail_raises_error(self, link_mock, lib_mock):
        link_instance_mock = link_mock.return_value
        link_instance_mock.as_playlist.return_value = None
        uri = 'spotify:playlist:foo'

        with self.assertRaises(spotify.Error):
            spotify.Playlist(uri)

    def test_life_cycle(self, lib_mock):
        sp_playlist = spotify.ffi.new('int *')

        playlist = spotify.Playlist(sp_playlist=sp_playlist)
        sp_playlist = playlist._sp_playlist

        lib_mock.sp_playlist_add_ref.assert_called_with(sp_playlist)
        lib_mock.sp_playlist_add_callbacks.assert_called_with(
            sp_playlist, mock.ANY, mock.ANY)

        playlist = None  # noqa
        tests.gc_collect()

        # TODO Fails on CPython 2.7 and PyPy, but not Python 3.x. I can't
        # really understand why.
        #lib_mock.sp_playlist_remove_callbacks.assert_called_with(
        #    sp_playlist, mock.ANY, mock.ANY)
        # FIXME Won't be called because lib_mock has references to the
        # sp_playlist object, and it thus won't be GC-ed.
        #lib_mock.sp_playlist_release.assert_called_with(sp_playlist)

    def test_cached_playlist(self, lib_mock):
        tests.create_session()
        sp_playlist = spotify.ffi.new('int *')

        result1 = spotify.Playlist._cached(sp_playlist)
        result2 = spotify.Playlist._cached(sp_playlist)

        self.assertIsInstance(result1, spotify.Playlist)
        self.assertIs(result1, result2)

    @mock.patch('spotify.Link', spec=spotify.Link)
    def test_repr(self, link_mock, lib_mock):
        lib_mock.sp_playlist_is_loaded.return_value = 1
        link_instance_mock = link_mock.return_value
        link_instance_mock.uri = 'foo'
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        result = repr(playlist)

        self.assertEqual(result, 'Playlist(%r)' % 'foo')

    @mock.patch('spotify.Link', spec=spotify.Link)
    def test_repr_if_unloaded(self, link_mock, lib_mock):
        lib_mock.sp_playlist_is_loaded.return_value = 0
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        result = repr(playlist)

        self.assertEqual(result, 'Playlist(<not loaded>)')

    @mock.patch('spotify.Link', spec=spotify.Link)
    def test_repr_if_link_creation_fails(self, link_mock, lib_mock):
        lib_mock.sp_playlist_is_loaded.return_value = 1
        link_mock.side_effect = spotify.Error('error message')
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        result = repr(playlist)

        self.assertEqual(result, 'Playlist(<error: error message>)')

    def test_is_loaded(self, lib_mock):
        lib_mock.sp_playlist_is_loaded.return_value = 1
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        result = playlist.is_loaded

        lib_mock.sp_playlist_is_loaded.assert_called_once_with(sp_playlist)
        self.assertTrue(result)

    @mock.patch('spotify.utils.load')
    def test_load(self, load_mock, lib_mock):
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        playlist.load(10)

        load_mock.assert_called_with(playlist, timeout=10)

    @mock.patch('spotify.track.lib', spec=spotify.lib)
    def test_tracks(self, track_lib_mock, lib_mock):
        sp_track = spotify.ffi.cast('sp_track *', spotify.ffi.new('int *'))
        lib_mock.sp_playlist_num_tracks.return_value = 1
        lib_mock.sp_playlist_track.return_value = sp_track
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        self.assertEqual(lib_mock.sp_playlist_add_ref.call_count, 1)
        result = playlist.tracks
        self.assertEqual(lib_mock.sp_playlist_add_ref.call_count, 2)

        self.assertEqual(len(result), 1)
        lib_mock.sp_playlist_num_tracks.assert_called_with(sp_playlist)

        item = result[0]
        self.assertIsInstance(item, spotify.Track)
        self.assertEqual(item._sp_track, sp_track)
        self.assertEqual(lib_mock.sp_playlist_track.call_count, 1)
        lib_mock.sp_playlist_track.assert_called_with(sp_playlist, 0)
        track_lib_mock.sp_track_add_ref.assert_called_with(sp_track)

    def test_tracks_if_no_tracks(self, lib_mock):
        lib_mock.sp_playlist_num_tracks.return_value = 0
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        result = playlist.tracks

        self.assertEqual(len(result), 0)
        lib_mock.sp_playlist_num_tracks.assert_called_with(sp_playlist)
        self.assertEqual(lib_mock.sp_playlist_track.call_count, 0)

    def test_tracks_if_unloaded(self, lib_mock):
        lib_mock.sp_playlist_is_loaded.return_value = 0
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        result = playlist.tracks

        lib_mock.sp_playlist_is_loaded.assert_called_with(sp_playlist)
        self.assertEqual(len(result), 0)

    def test_tracks_with_metadata(self, lib_mock):
        lib_mock.sp_playlist_num_tracks.return_value = 1
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        # Created a Playlist with a ref to sp_playlist
        self.assertEqual(lib_mock.sp_playlist_add_ref.call_count, 1)

        result = playlist.tracks_with_metadata

        # Created a Sequence with a ref to sp_playlist
        self.assertEqual(lib_mock.sp_playlist_add_ref.call_count, 2)

        self.assertEqual(len(result), 1)
        lib_mock.sp_playlist_num_tracks.assert_called_with(sp_playlist)

        item = result[0]
        self.assertIsInstance(item, spotify.PlaylistTrack)

        # Created a PlaylistTrack with a ref to sp_playlist
        self.assertEqual(lib_mock.sp_playlist_add_ref.call_count, 3)

    def test_tracks_with_metadata_if_no_tracks(self, lib_mock):
        lib_mock.sp_playlist_num_tracks.return_value = 0
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        result = playlist.tracks_with_metadata

        self.assertEqual(len(result), 0)
        lib_mock.sp_playlist_num_tracks.assert_called_with(sp_playlist)
        self.assertEqual(lib_mock.sp_playlist_track.call_count, 0)

    def test_tracks_with_metadata_if_unloaded(self, lib_mock):
        lib_mock.sp_playlist_is_loaded.return_value = 0
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        result = playlist.tracks_with_metadata

        lib_mock.sp_playlist_is_loaded.assert_called_with(sp_playlist)
        self.assertEqual(len(result), 0)

    def test_name(self, lib_mock):
        lib_mock.sp_playlist_name.return_value = spotify.ffi.new(
            'char[]', b'Foo Bar Baz')
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        result = playlist.name

        lib_mock.sp_playlist_name.assert_called_once_with(sp_playlist)
        self.assertEqual(result, 'Foo Bar Baz')

    def test_name_is_none_if_unloaded(self, lib_mock):
        lib_mock.sp_playlist_name.return_value = spotify.ffi.new('char[]', b'')
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        result = playlist.name

        lib_mock.sp_playlist_name.assert_called_once_with(sp_playlist)
        self.assertIsNone(result)

    def test_rename(self, lib_mock):
        lib_mock.sp_playlist_rename.return_value = int(spotify.ErrorType.OK)
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        playlist.rename('Quux')

        lib_mock.sp_playlist_rename.assert_called_with(sp_playlist, mock.ANY)
        self.assertEqual(
            spotify.ffi.string(lib_mock.sp_playlist_rename.call_args[0][1]),
            b'Quux')

    def test_rename_fails_if_error(self, lib_mock):
        lib_mock.sp_playlist_rename.return_value = int(
            spotify.ErrorType.BAD_API_VERSION)
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        with self.assertRaises(spotify.Error):
            playlist.rename('Quux')

    def test_name_setter(self, lib_mock):
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)
        playlist.rename = mock.Mock()

        playlist.name = 'Quux'

        playlist.rename.assert_called_with('Quux')

    @mock.patch('spotify.user.lib', spec=spotify.lib)
    def test_owner(self, user_lib_mock, lib_mock):
        sp_user = spotify.ffi.new('int *')
        lib_mock.sp_playlist_owner.return_value = sp_user
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        result = playlist.owner

        lib_mock.sp_playlist_owner.assert_called_with(sp_playlist)
        self.assertIsInstance(result, spotify.User)
        self.assertEqual(result._sp_user, sp_user)
        user_lib_mock.sp_user_add_ref.assert_called_with(sp_user)

    def test_is_collaborative(self, lib_mock):
        lib_mock.sp_playlist_is_collaborative.return_value = 1
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        result = playlist.collaborative

        lib_mock.sp_playlist_is_collaborative.assert_called_with(sp_playlist)
        self.assertTrue(result)

    def test_set_collaborative(self, lib_mock):
        lib_mock.sp_playlist_set_collaborative.return_value = int(
            spotify.ErrorType.OK)
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        playlist.collaborative = False

        lib_mock.sp_playlist_set_collaborative.assert_called_with(
            sp_playlist, 0)

    def test_set_collaborative_fails_if_error(self, lib_mock):
        lib_mock.sp_playlist_set_collaborative.return_value = int(
            spotify.ErrorType.BAD_API_VERSION)
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        with self.assertRaises(spotify.Error):
            playlist.collaborative = False

    def test_set_autolink_tracks(self, lib_mock):
        lib_mock.sp_playlist_set_autolink_tracks.return_value = int(
            spotify.ErrorType.OK)
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        playlist.set_autolink_tracks(True)

        lib_mock.sp_playlist_set_autolink_tracks.assert_called_with(
            sp_playlist, 1)

    def test_set_autolink_tracks_fails_if_error(self, lib_mock):
        lib_mock.sp_playlist_set_autolink_tracks.return_value = int(
            spotify.ErrorType.BAD_API_VERSION)
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        with self.assertRaises(spotify.Error):
            playlist.set_autolink_tracks(True)

    def test_description(self, lib_mock):
        lib_mock.sp_playlist_get_description.return_value = spotify.ffi.new(
            'char[]', b'Lorem ipsum')
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        result = playlist.description

        lib_mock.sp_playlist_get_description.assert_called_with(sp_playlist)
        self.assertEqual(result, 'Lorem ipsum')

    def test_description_is_none_if_unset(self, lib_mock):
        lib_mock.sp_playlist_get_description.return_value = spotify.ffi.NULL
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        result = playlist.description

        lib_mock.sp_playlist_get_description.assert_called_with(sp_playlist)
        self.assertIsNone(result)

    @mock.patch('spotify.image.lib', spec=spotify.lib)
    def test_image(self, image_lib_mock, lib_mock):
        session = tests.create_session()
        image_id = b'image-id'

        def func(sp_playlist, sp_image_id):
            buf = spotify.ffi.buffer(sp_image_id)
            buf[:len(image_id)] = image_id
            return 1

        lib_mock.sp_playlist_get_image.side_effect = func
        sp_image = spotify.ffi.new('int *')
        lib_mock.sp_image_create.return_value = sp_image
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        result = playlist.image

        lib_mock.sp_playlist_get_image.assert_called_with(
            sp_playlist, mock.ANY)
        lib_mock.sp_image_create.assert_called_with(
            session._sp_session, mock.ANY)
        self.assertEqual(
            spotify.ffi.string(lib_mock.sp_image_create.call_args[0][1]),
            b'image-id')

        self.assertIsInstance(result, spotify.Image)
        self.assertEqual(result._sp_image, sp_image)

        # Since we *created* the sp_image, we already have a refcount of 1 and
        # shouldn't increase the refcount when wrapping this sp_image in an
        # Image object
        self.assertEqual(image_lib_mock.sp_image_add_ref.call_count, 0)

    def test_image_is_none_if_no_image(self, lib_mock):
        lib_mock.sp_playlist_get_image.return_value = 0
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        result = playlist.image

        lib_mock.sp_playlist_get_image.assert_called_with(
            sp_playlist, mock.ANY)
        self.assertIsNone(result)

    def test_has_pending_changes(self, lib_mock):
        lib_mock.sp_playlist_has_pending_changes.return_value = 1
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        result = playlist.has_pending_changes

        lib_mock.sp_playlist_has_pending_changes.assert_called_with(
            sp_playlist)
        self.assertTrue(result)

    @mock.patch('spotify.track.lib', spec=spotify.lib)
    def test_add_tracks(self, track_lib_mock, lib_mock):
        session = tests.create_session()
        sp_track1 = spotify.ffi.new('int * ')
        track1 = spotify.Track(sp_track=sp_track1)
        sp_track2 = spotify.ffi.new('int * ')
        track2 = spotify.Track(sp_track=sp_track2)
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        playlist.add_tracks([track1, track2], position=4)

        lib_mock.sp_playlist_add_tracks.assert_called_with(
            sp_playlist, [sp_track1, sp_track2], 2, 4, session._sp_session)

    @mock.patch('spotify.track.lib', spec=spotify.lib)
    def test_add_tracks_without_position(self, track_lib_mock, lib_mock):
        session = tests.create_session()
        lib_mock.sp_playlist_num_tracks.return_value = 10
        sp_track1 = spotify.ffi.new('int * ')
        track1 = spotify.Track(sp_track=sp_track1)
        sp_track2 = spotify.ffi.new('int * ')
        track2 = spotify.Track(sp_track=sp_track2)
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        playlist.add_tracks([track1, track2])

        lib_mock.sp_playlist_add_tracks.assert_called_with(
            sp_playlist, [sp_track1, sp_track2], 2, 10, session._sp_session)

    @mock.patch('spotify.track.lib', spec=spotify.lib)
    def test_add_tracks_with_a_single_track(self, track_lib_mock, lib_mock):
        session = tests.create_session()
        sp_track = spotify.ffi.new('int * ')
        track = spotify.Track(sp_track=sp_track)
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        playlist.add_tracks(track, position=7)

        lib_mock.sp_playlist_add_tracks.assert_called_with(
            sp_playlist, [sp_track], 1, 7, session._sp_session)

    @mock.patch('spotify.track.lib', spec=spotify.lib)
    def test_remove_tracks(self, track_lib_mock, lib_mock):
        lib_mock.sp_playlist_remove_tracks.return_value = int(
            spotify.ErrorType.OK)
        sp_track1 = spotify.ffi.new('int *')
        track1 = spotify.Track(sp_track=sp_track1)
        sp_track2 = spotify.ffi.new('int *')
        track2 = spotify.Track(sp_track=sp_track2)
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        playlist.remove_tracks([track1, track2])

        lib_mock.sp_playlist_remove_tracks.assert_called_with(
            sp_playlist, mock.ANY, 2)
        self.assertIn(
            sp_track1, lib_mock.sp_playlist_remove_tracks.call_args[0][1])
        self.assertIn(
            sp_track2, lib_mock.sp_playlist_remove_tracks.call_args[0][1])

    @mock.patch('spotify.track.lib', spec=spotify.lib)
    def test_remove_tracks_with_a_single_track(self, track_lib_mock, lib_mock):
        lib_mock.sp_playlist_remove_tracks.return_value = int(
            spotify.ErrorType.OK)
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track=sp_track)
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        playlist.remove_tracks(track)

        lib_mock.sp_playlist_remove_tracks.assert_called_with(
            sp_playlist, [sp_track], 1)

    @mock.patch('spotify.track.lib', spec=spotify.lib)
    def test_remove_tracks_with_duplicates(self, track_lib_mock, lib_mock):
        lib_mock.sp_playlist_remove_tracks.return_value = int(
            spotify.ErrorType.OK)
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track=sp_track)
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        playlist.remove_tracks([track, track])

        lib_mock.sp_playlist_remove_tracks.assert_called_with(
            sp_playlist, [sp_track], 1)

    @mock.patch('spotify.track.lib', spec=spotify.lib)
    def test_remove_tracks_fails_if_error(self, track_lib_mock, lib_mock):
        lib_mock.sp_playlist_remove_tracks.return_value = int(
            spotify.ErrorType.PERMISSION_DENIED)
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track=sp_track)
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        with self.assertRaises(spotify.Error):
            playlist.remove_tracks(track)

    @mock.patch('spotify.track.lib', spec=spotify.lib)
    def test_reorder_tracks(self, track_lib_mock, lib_mock):
        lib_mock.sp_playlist_reorder_tracks.return_value = int(
            spotify.ErrorType.OK)
        sp_track1 = spotify.ffi.new('int *')
        track1 = spotify.Track(sp_track=sp_track1)
        sp_track2 = spotify.ffi.new('int *')
        track2 = spotify.Track(sp_track=sp_track2)
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        playlist.reorder_tracks([track1, track2], 17)

        lib_mock.sp_playlist_reorder_tracks.assert_called_with(
            sp_playlist, mock.ANY, 2, 17)
        self.assertIn(
            sp_track1, lib_mock.sp_playlist_reorder_tracks.call_args[0][1])
        self.assertIn(
            sp_track2, lib_mock.sp_playlist_reorder_tracks.call_args[0][1])

    @mock.patch('spotify.track.lib', spec=spotify.lib)
    def test_reorder_tracks_with_a_single_track(
            self, track_lib_mock, lib_mock):
        lib_mock.sp_playlist_reorder_tracks.return_value = int(
            spotify.ErrorType.OK)
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track=sp_track)
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        playlist.reorder_tracks(track, 17)

        lib_mock.sp_playlist_reorder_tracks.assert_called_with(
            sp_playlist, [sp_track], 1, 17)

    @mock.patch('spotify.track.lib', spec=spotify.lib)
    def test_reorder_tracks_with_duplicates(self, track_lib_mock, lib_mock):
        lib_mock.sp_playlist_reorder_tracks.return_value = int(
            spotify.ErrorType.OK)
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track=sp_track)
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        playlist.reorder_tracks([track, track], 17)

        lib_mock.sp_playlist_reorder_tracks.assert_called_with(
            sp_playlist, [sp_track], 1, 17)

    @mock.patch('spotify.track.lib', spec=spotify.lib)
    def test_reorder_tracks_fails_if_error(self, track_lib_mock, lib_mock):
        lib_mock.sp_playlist_reorder_tracks.return_value = int(
            spotify.ErrorType.PERMISSION_DENIED)
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track=sp_track)
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        with self.assertRaises(spotify.Error):
            playlist.reorder_tracks(track, 17)

    def test_num_subscribers(self, lib_mock):
        lib_mock.sp_playlist_num_subscribers.return_value = 7
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        result = playlist.num_subscribers

        lib_mock.sp_playlist_num_subscribers.assert_called_with(sp_playlist)
        self.assertEqual(result, 7)

    def test_subscribers(self, lib_mock):
        sp_subscribers = spotify.ffi.new('sp_subscribers *')
        sp_subscribers.count = 1
        user_alice = spotify.ffi.new('char[]', b'alice')
        sp_subscribers.subscribers = [user_alice]
        lib_mock.sp_playlist_subscribers.return_value = sp_subscribers
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        result = playlist.subscribers

        lib_mock.sp_playlist_subscribers.assert_called_with(sp_playlist)
        tests.gc_collect()
        lib_mock.sp_playlist_subscribers_free.assert_called_with(
            sp_subscribers)
        self.assertEqual(result, ['alice'])

    def test_update_subscribers(self, lib_mock):
        session = tests.create_session()
        lib_mock.sp_playlist_update_subscribers.return_value = int(
            spotify.ErrorType.OK)
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        playlist.update_subscribers()

        lib_mock.sp_playlist_update_subscribers.assert_called_with(
            session._sp_session, sp_playlist)

    def test_update_subscribers_fails_if_error(self, lib_mock):
        tests.create_session()
        lib_mock.sp_playlist_update_subscribers.return_value = int(
            spotify.ErrorType.BAD_API_VERSION)
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        with self.assertRaises(spotify.Error):
            playlist.update_subscribers()

    def test_is_in_ram(self, lib_mock):
        session = tests.create_session()
        lib_mock.sp_playlist_is_in_ram.return_value = 1
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        result = playlist.is_in_ram

        lib_mock.sp_playlist_is_in_ram.assert_called_with(
            session._sp_session, sp_playlist)
        self.assertTrue(result)

    def test_set_in_ram(self, lib_mock):
        session = tests.create_session()
        lib_mock.sp_playlist_set_in_ram.return_value = int(
            spotify.ErrorType.OK)
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        playlist.set_in_ram(False)

        lib_mock.sp_playlist_set_in_ram.assert_called_with(
            session._sp_session, sp_playlist, 0)

    def test_set_in_ram_fails_if_error(self, lib_mock):
        tests.create_session()
        lib_mock.sp_playlist_set_in_ram.return_value = int(
            spotify.ErrorType.BAD_API_VERSION)
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        with self.assertRaises(spotify.Error):
            playlist.set_in_ram(False)

    def test_set_offline_mode(self, lib_mock):
        session = tests.create_session()
        lib_mock.sp_playlist_set_offline_mode.return_value = int(
            spotify.ErrorType.OK)
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        playlist.set_offline_mode(False)

        lib_mock.sp_playlist_set_offline_mode.assert_called_with(
            session._sp_session, sp_playlist, 0)

    def test_set_offline_mode_fails_if_error(self, lib_mock):
        tests.create_session()
        lib_mock.sp_playlist_set_offline_mode.return_value = int(
            spotify.ErrorType.BAD_API_VERSION)
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        with self.assertRaises(spotify.Error):
            playlist.set_offline_mode(False)

    def test_offline_status(self, lib_mock):
        session = tests.create_session()
        lib_mock.sp_playlist_get_offline_status.return_value = 2
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        result = playlist.offline_status

        lib_mock.sp_playlist_get_offline_status.assert_called_with(
            session._sp_session, sp_playlist)
        self.assertIs(result, spotify.PlaylistOfflineStatus.DOWNLOADING)

    def test_offline_download_completed(self, lib_mock):
        session = tests.create_session()
        lib_mock.sp_playlist_get_offline_status.return_value = 2
        lib_mock.sp_playlist_get_offline_download_completed.return_value = 73
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        result = playlist.offline_download_completed

        lib_mock.sp_playlist_get_offline_download_completed.assert_called_with(
            session._sp_session, sp_playlist)
        self.assertEqual(result, 73)

    def test_offline_download_completed_when_not_downloading(self, lib_mock):
        tests.create_session()
        lib_mock.sp_playlist_get_offline_status.return_value = 0
        lib_mock.sp_playlist_get_offline_download_completed.return_value = 0
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        result = playlist.offline_download_completed

        self.assertEqual(
            lib_mock.sp_playlist_get_offline_download_completed.call_count, 0)
        self.assertIsNone(result)

    @mock.patch('spotify.Link', spec=spotify.Link)
    def test_link_creates_link_to_playlist(self, link_mock, lib_mock):
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)
        sp_link = spotify.ffi.new('int *')
        lib_mock.sp_link_create_from_playlist.return_value = sp_link
        link_mock.return_value = mock.sentinel.link

        result = playlist.link

        link_mock.assert_called_once_with(sp_link=sp_link, add_ref=False)
        self.assertEqual(result, mock.sentinel.link)

    @mock.patch('spotify.Link', spec=spotify.Link)
    def test_link_fails_if_playlist_not_loaded(
            self, lik_mock, lib_mock):
        lib_mock.sp_playlist_is_loaded.return_value = 0
        lib_mock.sp_link_create_from_playlist.return_value = spotify.ffi.NULL
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        with self.assertRaises(spotify.Error):
            playlist.link

        # Condition is checked before link creation is tried
        self.assertEqual(lib_mock.sp_link_create_from_playlist.call_count, 0)

    @mock.patch('spotify.Link', spec=spotify.Link)
    def test_link_may_fail_if_playlist_has_not_been_in_ram(
            self, link_mock, lib_mock):
        session = tests.create_session()
        lib_mock.sp_playlist_is_loaded.return_value = 1
        lib_mock.sp_link_create_from_playlist.return_value = spotify.ffi.NULL
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        with self.assertRaises(spotify.Error):
            playlist.link

        # Condition is checked only if link creation returns NULL
        lib_mock.sp_link_create_from_playlist.assert_called_with(sp_playlist)
        lib_mock.sp_playlist_is_in_ram.assert_called_with(
            session._sp_session, sp_playlist)

    def test_first_on_call_adds_ref_to_obj_on_session(self, lib_mock):
        session = tests.create_session()
        sp_playlist = spotify.ffi.cast('sp_playlist *', 42)
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        playlist.on(spotify.PlaylistEvent.TRACKS_ADDED, lambda *args: None)

        self.assertIn(playlist, session._emitters)

    def test_last_off_call_removes_ref_to_obj_from_session(self, lib_mock):
        session = tests.create_session()
        sp_playlist = spotify.ffi.cast('sp_playlist *', 42)
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        playlist.on(spotify.PlaylistEvent.TRACKS_ADDED, lambda *args: None)
        playlist.off(spotify.PlaylistEvent.TRACKS_ADDED)

        self.assertNotIn(playlist, session._emitters)

    def test_other_off_calls_keeps_ref_to_obj_on_session(self, lib_mock):
        session = tests.create_session()
        sp_playlist = spotify.ffi.cast('sp_playlist *', 42)
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        playlist.on(spotify.PlaylistEvent.TRACKS_ADDED, lambda *args: None)
        playlist.on(spotify.PlaylistEvent.TRACKS_MOVED, lambda *args: None)
        playlist.off(spotify.PlaylistEvent.TRACKS_ADDED)

        self.assertIn(playlist, session._emitters)

        playlist.off(spotify.PlaylistEvent.TRACKS_MOVED)

        self.assertNotIn(playlist, session._emitters)


@mock.patch('spotify.playlist.lib', spec=spotify.lib)
class PlaylistCallbacksTest(unittest.TestCase):

    def tearDown(self):
        spotify.session_instance = None

    @mock.patch('spotify.track.lib', spec=spotify.lib)
    def test_tracks_added_callback(self, track_lib_mock, lib_mock):
        tests.create_session()
        callback = mock.Mock()
        sp_playlist = spotify.ffi.cast('sp_playlist *', 42)
        playlist = spotify.Playlist._cached(sp_playlist=sp_playlist)
        playlist.on(spotify.PlaylistEvent.TRACKS_ADDED, callback)
        sp_tracks = [
            spotify.ffi.cast('sp_track *', 43),
            spotify.ffi.cast('sp_track *', 44),
            spotify.ffi.cast('sp_track *', 45),
        ]
        position = 7

        _PlaylistCallbacks.tracks_added(
            sp_playlist, sp_tracks, len(sp_tracks), position, spotify.ffi.NULL)

        callback.assert_called_once_with(playlist, mock.ANY, position)
        tracks = callback.call_args[0][1]
        self.assertEqual(len(tracks), len(sp_tracks))
        self.assertIsInstance(tracks[0], spotify.Track)
        self.assertEqual(tracks[0]._sp_track, sp_tracks[0])
        track_lib_mock.sp_track_add_ref.assert_has_calls([
            mock.call(sp_tracks[0]),
            mock.call(sp_tracks[1]),
            mock.call(sp_tracks[2]),
        ])

    def test_tracks_removed_callback(self, lib_mock):
        tests.create_session()
        callback = mock.Mock()
        sp_playlist = spotify.ffi.cast('sp_playlist *', 42)
        playlist = spotify.Playlist._cached(sp_playlist=sp_playlist)
        playlist.on(spotify.PlaylistEvent.TRACKS_REMOVED, callback)
        track_numbers = [43, 44, 45]

        _PlaylistCallbacks.tracks_removed(
            sp_playlist, track_numbers, len(track_numbers), spotify.ffi.NULL)

        callback.assert_called_once_with(playlist, mock.ANY)
        tracks = callback.call_args[0][1]
        self.assertEqual(len(tracks), len(track_numbers))
        self.assertEqual(tracks[0], 43)

    def test_tracks_moved_callback(self, lib_mock):
        tests.create_session()
        callback = mock.Mock()
        sp_playlist = spotify.ffi.cast('sp_playlist *', 42)
        playlist = spotify.Playlist._cached(sp_playlist=sp_playlist)
        playlist.on(spotify.PlaylistEvent.TRACKS_MOVED, callback)
        track_numbers = [43, 44, 45]
        position = 7

        _PlaylistCallbacks.tracks_moved(
            sp_playlist, track_numbers, len(track_numbers), position,
            spotify.ffi.NULL)

        callback.assert_called_once_with(playlist, mock.ANY, position)
        tracks = callback.call_args[0][1]
        self.assertEqual(len(tracks), len(track_numbers))
        self.assertEqual(tracks[0], 43)

    def test_playlist_renamed_callback(self, lib_mock):
        tests.create_session()
        callback = mock.Mock()
        sp_playlist = spotify.ffi.cast('sp_playlist *', 42)
        playlist = spotify.Playlist._cached(sp_playlist=sp_playlist)
        playlist.on(spotify.PlaylistEvent.PLAYLIST_RENAMED, callback)

        _PlaylistCallbacks.playlist_renamed(sp_playlist, spotify.ffi.NULL)

        callback.assert_called_once_with(playlist)

    def test_playlist_state_changed_callback(self, lib_mock):
        tests.create_session()
        callback = mock.Mock()
        sp_playlist = spotify.ffi.cast('sp_playlist *', 42)
        playlist = spotify.Playlist._cached(sp_playlist=sp_playlist)
        playlist.on(spotify.PlaylistEvent.PLAYLIST_STATE_CHANGED, callback)

        _PlaylistCallbacks.playlist_state_changed(
            sp_playlist, spotify.ffi.NULL)

        callback.assert_called_once_with(playlist)

    def test_playlist_update_in_progress_callback(self, lib_mock):
        tests.create_session()
        callback = mock.Mock()
        sp_playlist = spotify.ffi.cast('sp_playlist *', 42)
        playlist = spotify.Playlist._cached(sp_playlist=sp_playlist)
        playlist.on(
            spotify.PlaylistEvent.PLAYLIST_UPDATE_IN_PROGRESS, callback)
        done = True

        _PlaylistCallbacks.playlist_update_in_progress(
            sp_playlist, int(done), spotify.ffi.NULL)

        callback.assert_called_once_with(playlist, done)

    def test_playlist_metadata_updated_callback(self, lib_mock):
        tests.create_session()
        callback = mock.Mock()
        sp_playlist = spotify.ffi.cast('sp_playlist *', 42)
        playlist = spotify.Playlist._cached(sp_playlist=sp_playlist)
        playlist.on(spotify.PlaylistEvent.PLAYLIST_METADATA_UPDATED, callback)

        _PlaylistCallbacks.playlist_metadata_updated(
            sp_playlist, spotify.ffi.NULL)

        callback.assert_called_once_with(playlist)

    @mock.patch('spotify.user.lib', spec=spotify.lib)
    def test_track_created_changed_callback(self, user_lib_mock, lib_mock):
        tests.create_session()
        callback = mock.Mock()
        sp_playlist = spotify.ffi.cast('sp_playlist *', 42)
        playlist = spotify.Playlist._cached(sp_playlist=sp_playlist)
        playlist.on(spotify.PlaylistEvent.TRACK_CREATED_CHANGED, callback)
        position = 7
        sp_user = spotify.ffi.cast('sp_user *', 43)
        time = 123456789

        _PlaylistCallbacks.track_created_changed(
            sp_playlist, position, sp_user, time, spotify.ffi.NULL)

        callback.assert_called_once_with(playlist, position, mock.ANY, time)
        user = callback.call_args[0][2]
        self.assertIsInstance(user, spotify.User)
        self.assertEqual(user._sp_user, sp_user)
        user_lib_mock.sp_user_add_ref.assert_called_with(sp_user)

    def test_track_seen_changed_callback(self, lib_mock):
        tests.create_session()
        callback = mock.Mock()
        sp_playlist = spotify.ffi.cast('sp_playlist *', 42)
        playlist = spotify.Playlist._cached(sp_playlist=sp_playlist)
        playlist.on(spotify.PlaylistEvent.TRACK_SEEN_CHANGED, callback)
        position = 7
        seen = True

        _PlaylistCallbacks.track_seen_changed(
            sp_playlist, position, int(seen), spotify.ffi.NULL)

        callback.assert_called_once_with(playlist, position, seen)

    def test_description_changed_callback(self, lib_mock):
        tests.create_session()
        callback = mock.Mock()
        sp_playlist = spotify.ffi.cast('sp_playlist *', 42)
        playlist = spotify.Playlist._cached(sp_playlist=sp_playlist)
        playlist.on(spotify.PlaylistEvent.DESCRIPTION_CHANGED, callback)
        description = 'foo bar æøå'
        desc = spotify.ffi.new('char[]', description.encode('utf-8'))

        _PlaylistCallbacks.description_changed(
            sp_playlist, desc, spotify.ffi.NULL)

        callback.assert_called_once_with(playlist, description)

    @mock.patch('spotify.image.lib', spec=spotify.lib)
    def test_image_changed_callback(self, image_lib_mock, lib_mock):
        session = tests.create_session()
        callback = mock.Mock()
        sp_playlist = spotify.ffi.cast('sp_playlist *', 42)
        playlist = spotify.Playlist._cached(sp_playlist=sp_playlist)
        playlist.on(spotify.PlaylistEvent.IMAGE_CHANGED, callback)
        image_id = spotify.ffi.new('char[]', b'image-id')
        sp_image = spotify.ffi.cast('sp_image *', 43)
        lib_mock.sp_image_create.return_value = sp_image

        _PlaylistCallbacks.image_changed(
            sp_playlist, image_id, spotify.ffi.NULL)

        callback.assert_called_once_with(playlist, mock.ANY)
        image = callback.call_args[0][1]
        self.assertIsInstance(image, spotify.Image)
        self.assertEqual(image._sp_image, sp_image)
        lib_mock.sp_image_create.assert_called_once_with(
            session._sp_session, image_id)
        self.assertEqual(image_lib_mock.sp_image_add_ref.call_count, 0)

    def test_track_message_changed_callback(self, lib_mock):
        tests.create_session()
        callback = mock.Mock()
        sp_playlist = spotify.ffi.cast('sp_playlist *', 42)
        playlist = spotify.Playlist._cached(sp_playlist=sp_playlist)
        playlist.on(spotify.PlaylistEvent.TRACK_MESSAGE_CHANGED, callback)
        position = 7
        message = 'foo bar æøå'
        msg = spotify.ffi.new('char[]', message.encode('utf-8'))

        _PlaylistCallbacks.track_message_changed(
            sp_playlist, position, msg, spotify.ffi.NULL)

        callback.assert_called_once_with(playlist, position, message)

    def test_subscribers_changed_callback(self, lib_mock):
        tests.create_session()
        callback = mock.Mock()
        sp_playlist = spotify.ffi.cast('sp_playlist *', 42)
        playlist = spotify.Playlist._cached(sp_playlist=sp_playlist)
        playlist.on(spotify.PlaylistEvent.SUBSCRIBERS_CHANGED, callback)

        _PlaylistCallbacks.subscribers_changed(sp_playlist, spotify.ffi.NULL)

        callback.assert_called_once_with(playlist)


@mock.patch('spotify.playlist.lib', spec=spotify.lib)
class PlaylistContainerTest(unittest.TestCase):

    def tearDown(self):
        spotify.session_instance = None

    def test_life_cycle(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.new('int *')

        playlist_container = spotify.PlaylistContainer(sp_playlistcontainer)

        lib_mock.sp_playlistcontainer_add_ref.assert_called_with(
            sp_playlistcontainer)
        lib_mock.sp_playlistcontainer_add_callbacks.assert_called_with(
            sp_playlistcontainer, mock.ANY, mock.ANY)

        playlist_container = None  # noqa
        tests.gc_collect()

        lib_mock.sp_playlistcontainer_remove_callbacks.assert_called_with(
            sp_playlistcontainer, mock.ANY, mock.ANY)
        # FIXME Won't be called because lib_mock has references to the
        # sp_playlistcontainer object, and it thus won't be GC-ed.
        #lib_mock.sp_playlistcontainer_release.assert_called_with(
        #    sp_playlistcontainer)

    def test_cached_container(self, lib_mock):
        tests.create_session()
        sp_playlistcontainer = spotify.ffi.new('int *')

        result1 = spotify.PlaylistContainer._cached(sp_playlistcontainer)
        result2 = spotify.PlaylistContainer._cached(sp_playlistcontainer)

        self.assertIsInstance(result1, spotify.PlaylistContainer)
        self.assertIs(result1, result2)

    @mock.patch('spotify.User', spec=spotify.User)
    @mock.patch('spotify.Link', spec=spotify.Link)
    def test_repr(self, link_mock, user_mock, lib_mock):
        link_instance_mock = link_mock.return_value
        link_instance_mock.uri = 'foo'
        user_instance_mock = user_mock.return_value
        user_instance_mock.link = link_instance_mock
        lib_mock.sp_playlistcontainer_num_playlists.return_value = 0
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)

        result = repr(playlist_container)

        self.assertEqual(
            result, '<spotify.PlaylistContainer owned by %s: []>' % 'foo')

    def test_is_loaded(self, lib_mock):
        lib_mock.sp_playlistcontainer_is_loaded.return_value = 1
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)

        result = playlist_container.is_loaded

        lib_mock.sp_playlistcontainer_is_loaded.assert_called_once_with(
            sp_playlistcontainer)
        self.assertTrue(result)

    @mock.patch('spotify.utils.load')
    def test_load(self, load_mock, lib_mock):
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)

        playlist_container.load(10)

        load_mock.assert_called_with(playlist_container, timeout=10)

    def test_len(self, lib_mock):
        lib_mock.sp_playlistcontainer_num_playlists.return_value = 8
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)

        result = len(playlist_container)

        lib_mock.sp_playlistcontainer_num_playlists.assert_called_with(
            sp_playlistcontainer)
        self.assertEqual(result, 8)

    def test_len_if_undefined(self, lib_mock):
        lib_mock.sp_playlistcontainer_num_playlists.return_value = -1
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)

        result = len(playlist_container)

        lib_mock.sp_playlistcontainer_num_playlists.assert_called_with(
            sp_playlistcontainer)
        self.assertEqual(result, 0)

    def test_getitem(self, lib_mock):
        tests.create_session()
        lib_mock.sp_playlistcontainer_num_playlists.return_value = 1
        sp_playlist = spotify.ffi.new('int *')
        lib_mock.sp_playlistcontainer_playlist_type.return_value = int(
            spotify.PlaylistType.PLAYLIST)
        lib_mock.sp_playlistcontainer_playlist.return_value = sp_playlist
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)

        result = playlist_container[0]

        lib_mock.sp_playlistcontainer_playlist.assert_called_with(
            sp_playlistcontainer, 0)
        lib_mock.sp_playlist_add_ref.assert_called_with(sp_playlist)
        self.assertIsInstance(result, spotify.Playlist)
        self.assertEqual(result._sp_playlist, sp_playlist)

    def test_getitem_with_slice(self, lib_mock):
        tests.create_session()
        lib_mock.sp_playlistcontainer_num_playlists.return_value = 3
        lib_mock.sp_playlistcontainer_playlist_type.side_effect = [
            int(spotify.PlaylistType.PLAYLIST),
            int(spotify.PlaylistType.PLAYLIST),
            int(spotify.PlaylistType.PLAYLIST)]
        sp_playlist1 = spotify.ffi.new('int *')
        sp_playlist2 = spotify.ffi.new('int *')
        sp_playlist3 = spotify.ffi.new('int *')
        lib_mock.sp_playlistcontainer_playlist.side_effect = [
            sp_playlist1, sp_playlist2, sp_playlist3
        ]
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)

        result = playlist_container[0:2]

        # Entire collection of length 3 is created as a list
        self.assertEqual(lib_mock.sp_playlistcontainer_playlist.call_count, 3)
        self.assertEqual(lib_mock.sp_playlist_add_ref.call_count, 3)

        # Only a subslice of length 2 is returned
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]._sp_playlist, sp_playlist1)
        self.assertEqual(result[1]._sp_playlist, sp_playlist2)

    def test_getitem_with_folder(self, lib_mock):
        folder_name = 'foobar'

        tests.create_session()
        lib_mock.sp_playlistcontainer_num_playlists.return_value = 3
        lib_mock.sp_playlistcontainer_playlist_type.side_effect = [
            int(spotify.PlaylistType.START_FOLDER),
            int(spotify.PlaylistType.PLAYLIST),
            int(spotify.PlaylistType.END_FOLDER)]
        sp_playlist = spotify.ffi.new('int *')
        lib_mock.sp_playlistcontainer_playlist.return_value = sp_playlist
        lib_mock.sp_playlistcontainer_playlist_folder_id.side_effect = [
            1001, 1002]
        lib_mock.sp_playlistcontainer_playlist_folder_name.side_effect = (
            tests.buffer_writer(folder_name))
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)

        result = playlist_container[0]

        lib_mock.sp_playlistcontainer_playlist_type.assert_called_with(
            sp_playlistcontainer, 0)
        lib_mock.sp_playlistcontainer_playlist_folder_id.assert_called_with(
            sp_playlistcontainer, 0)
        self.assertIsInstance(result, spotify.PlaylistFolder)
        self.assertEqual(result.id, 1001)
        self.assertEqual(result.name, 'foobar')
        self.assertEqual(result.type, spotify.PlaylistType.START_FOLDER)

        result = playlist_container[1]

        lib_mock.sp_playlistcontainer_playlist_type.assert_called_with(
            sp_playlistcontainer, 1)
        lib_mock.sp_playlistcontainer_playlist.assert_called_with(
            sp_playlistcontainer, 1)
        lib_mock.sp_playlist_add_ref.assert_called_with(sp_playlist)
        self.assertIsInstance(result, spotify.Playlist)
        self.assertEqual(result._sp_playlist, sp_playlist)

        result = playlist_container[2]

        lib_mock.sp_playlistcontainer_playlist_type.assert_called_with(
            sp_playlistcontainer, 2)
        lib_mock.sp_playlistcontainer_playlist_folder_id.assert_called_with(
            sp_playlistcontainer, 2)
        self.assertIsInstance(result, spotify.PlaylistFolder)
        self.assertEqual(result.id, 1002)
        #self.assertEqual(result.name, '')  # Needs better mock impl
        self.assertEqual(result.type, spotify.PlaylistType.END_FOLDER)

    def test_getitem_raises_error_on_unknown_playlist_type(self, lib_mock):
        lib_mock.sp_playlistcontainer_num_playlists.return_value = 1
        lib_mock.sp_playlistcontainer_playlist_type.return_value = int(
            spotify.PlaylistType.PLACEHOLDER)
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)

        with self.assertRaises(spotify.Error):
            playlist_container[0]

    def test_getitem_raises_index_error_on_negative_index(self, lib_mock):
        lib_mock.sp_playlistcontainer_num_playlists.return_value = 1
        sp_playlist = spotify.ffi.new('int *')
        lib_mock.sp_playlistcontainer_playlist.return_value = sp_playlist
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)

        with self.assertRaises(IndexError):
            playlist_container[-1]

    def test_getitem_raises_index_error_on_too_high_index(self, lib_mock):
        lib_mock.sp_playlistcontainer_num_playlists.return_value = 1
        sp_playlist = spotify.ffi.new('int *')
        lib_mock.sp_playlistcontainer_playlist.return_value = sp_playlist
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)

        with self.assertRaises(IndexError):
            playlist_container[1]

    def test_getitem_raises_type_error_on_non_integral_index(self, lib_mock):
        lib_mock.sp_playlistcontainer_num_playlists.return_value = 1
        sp_playlist = spotify.ffi.new('int *')
        lib_mock.sp_playlistcontainer_playlist.return_value = sp_playlist
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)

        with self.assertRaises(TypeError):
            playlist_container['abc']

    def test_setitem_with_playlist_name(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)
        playlist_container.__len__ = mock.Mock(return_value=5)
        playlist_container.remove_playlist = mock.Mock()
        playlist_container.add_new_playlist = mock.Mock()

        playlist_container[0] = 'New playlist'

        playlist_container.add_new_playlist.assert_called_with(
            'New playlist', index=0)
        playlist_container.remove_playlist.assert_called_with(1)

    def test_setitem_with_existing_playlist(self, lib_mock):
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)
        playlist_container.__len__ = mock.Mock(return_value=5)
        playlist_container.remove_playlist = mock.Mock()
        playlist_container.add_playlist = mock.Mock()

        playlist_container[0] = playlist

        playlist_container.add_playlist.assert_called_with(playlist, index=0)
        playlist_container.remove_playlist.assert_called_with(1)

    def test_setitem_with_slice(self, lib_mock):
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)
        playlist_container.__len__ = mock.Mock(return_value=5)
        playlist_container.remove_playlist = mock.Mock()
        playlist_container.add_new_playlist = mock.Mock()
        playlist_container.add_playlist = mock.Mock()

        playlist_container[0:2] = ['New playlist', playlist]

        playlist_container.add_new_playlist.assert_called_with(
            'New playlist', index=0)
        playlist_container.add_playlist.assert_called_with(playlist, index=1)
        playlist_container.remove_playlist.assert_has_calls(
            [mock.call(3), mock.call(2)], any_order=False)

    def test_setittem_with_slice_and_noniterable_value_fails(self, lib_mock):
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)
        playlist_container.__len__ = mock.Mock(return_value=3)
        playlist_container.remove_playlist = mock.Mock()
        playlist_container.add_new_playlist = mock.Mock()

        with self.assertRaises(TypeError):
            playlist_container[0:2] = playlist

    def test_setitem_raises_error_on_unknown_playlist_type(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)
        playlist_container.__len__ = mock.Mock(return_value=1)
        playlist_container.remove_playlist = mock.Mock()
        playlist_container.add_new_playlist = mock.Mock(side_effect=ValueError)

        with self.assertRaises(ValueError):
            playlist_container[0] = False

        playlist_container.add_new_playlist.assert_called_with(False, index=0)
        self.assertEqual(playlist_container.remove_playlist.call_count, 0)

    def test_setitem_raises_index_error_on_negative_index(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)
        playlist_container.__len__ = mock.Mock(return_value=1)

        with self.assertRaises(IndexError):
            playlist_container[-1] = None

    def test_setitem_raises_index_error_on_too_high_index(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)
        playlist_container.__len__ = mock.Mock(return_value=1)

        with self.assertRaises(IndexError):
            playlist_container[1] = None

    def test_setitem_raises_type_error_on_non_integral_index(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)
        playlist_container.__len__ = mock.Mock(return_value=1)

        with self.assertRaises(TypeError):
            playlist_container['abc'] = None

    def test_delitem(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)
        playlist_container.__len__ = mock.Mock(return_value=1)
        playlist_container.remove_playlist = mock.Mock()

        del playlist_container[0]

        playlist_container.remove_playlist.assert_called_with(0)

    def test_delitem_with_slice(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)
        playlist_container.__len__ = mock.Mock(return_value=3)
        playlist_container.remove_playlist = mock.Mock()

        del playlist_container[0:2]

        # Delete items in reverse order, so the indexes doesn't change
        playlist_container.remove_playlist.assert_has_calls(
            [mock.call(1), mock.call(0)], any_order=False)

    def test_delitem_raises_index_error_on_negative_index(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)
        playlist_container.__len__ = mock.Mock(return_value=1)

        with self.assertRaises(IndexError):
            del playlist_container[-1]

    def test_delitem_raises_index_error_on_too_high_index(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)
        playlist_container.__len__ = mock.Mock(return_value=1)

        with self.assertRaises(IndexError):
            del playlist_container[1]

    def test_delitem_raises_type_error_on_non_integral_index(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)
        playlist_container.__len__ = mock.Mock(return_value=1)

        with self.assertRaises(TypeError):
            del playlist_container['abc']

    def test_insert_with_playlist_name(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)
        playlist_container.__len__ = mock.Mock(return_value=5)
        playlist_container.remove_playlist = mock.Mock()
        playlist_container.add_new_playlist = mock.Mock()

        playlist_container.insert(3, 'New playlist')

        playlist_container.add_new_playlist.assert_called_with(
            'New playlist', index=3)

    def test_insert_with_existing_playlist(self, lib_mock):
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)
        playlist_container.__len__ = mock.Mock(return_value=5)
        playlist_container.remove_playlist = mock.Mock()
        playlist_container.add_playlist = mock.Mock()

        playlist_container.insert(3, playlist)

        playlist_container.add_playlist.assert_called_with(playlist, index=3)

    def test_is_a_sequence(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)

        self.assertIsInstance(playlist_container, collections.Sequence)

    def test_is_a_mutable_sequence(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)

        self.assertIsInstance(playlist_container, collections.MutableSequence)

    def test_add_new_playlist_to_end_of_container(self, lib_mock):
        tests.create_session()
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)
        sp_playlist = spotify.ffi.new('int *')
        lib_mock.sp_playlistcontainer_add_new_playlist.return_value = (
            sp_playlist)

        result = playlist_container.add_new_playlist('foo bar')

        lib_mock.sp_playlistcontainer_add_new_playlist.assert_called_with(
            sp_playlistcontainer, mock.ANY)
        self.assertEqual(
            spotify.ffi.string(
                lib_mock.sp_playlistcontainer_add_new_playlist
                .call_args[0][1]),
            b'foo bar')
        self.assertIsInstance(result, spotify.Playlist)
        self.assertEqual(result._sp_playlist, sp_playlist)
        lib_mock.sp_playlist_add_ref.assert_called_with(sp_playlist)
        self.assertEqual(
            lib_mock.sp_playlistcontainer_move_playlist.call_count, 0)

    def test_add_new_playlist_at_given_index(self, lib_mock):
        tests.create_session()
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)
        sp_playlist = spotify.ffi.new('int *')
        lib_mock.sp_playlistcontainer_add_new_playlist.return_value = (
            sp_playlist)
        lib_mock.sp_playlistcontainer_num_playlists.return_value = 100
        lib_mock.sp_playlistcontainer_move_playlist.return_value = int(
            spotify.ErrorType.OK)

        result = playlist_container.add_new_playlist('foo bar', index=7)

        lib_mock.sp_playlistcontainer_add_new_playlist.assert_called_with(
            sp_playlistcontainer, mock.ANY)
        self.assertEqual(
            spotify.ffi.string(
                lib_mock.sp_playlistcontainer_add_new_playlist
                .call_args[0][1]),
            b'foo bar')
        self.assertIsInstance(result, spotify.Playlist)
        self.assertEqual(result._sp_playlist, sp_playlist)
        lib_mock.sp_playlist_add_ref.assert_called_with(sp_playlist)
        lib_mock.sp_playlistcontainer_move_playlist.assert_called_with(
            sp_playlistcontainer, 99, 7, 0)

    def test_add_new_playlist_fails_if_name_is_space_only(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)

        with self.assertRaises(ValueError):
            playlist_container.add_new_playlist('   ')

        # Spotify seems to accept e.g. tab-only names, but it doesn't make any
        # sense to allow it, so we disallow names with all combinations of just
        # whitespace.
        with self.assertRaises(ValueError):
            playlist_container.add_new_playlist('\t\t')
        with self.assertRaises(ValueError):
            playlist_container.add_new_playlist('\r\r')
        with self.assertRaises(ValueError):
            playlist_container.add_new_playlist('\n\n')
        with self.assertRaises(ValueError):
            playlist_container.add_new_playlist(' \t\r\n')

    def test_add_new_playlist_fails_if_name_is_too_long(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)

        with self.assertRaises(ValueError):
            playlist_container.add_new_playlist('x' * 300)

    def test_add_new_playlist_fails_if_operation_fails(self, lib_mock):
        lib_mock.sp_playlistcontainer_add_new_playlist.return_value = (
            spotify.ffi.NULL)
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)

        with self.assertRaises(spotify.Error):
            playlist_container.add_new_playlist('foo bar')

    def test_add_playlist_from_link(self, lib_mock):
        tests.create_session()
        sp_link = spotify.ffi.new('int *')
        link = spotify.Link(sp_link=sp_link, add_ref=False)
        sp_playlist = spotify.ffi.new('int *')
        lib_mock.sp_playlistcontainer_add_playlist.return_value = sp_playlist
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)

        result = playlist_container.add_playlist(link)

        lib_mock.sp_playlistcontainer_add_playlist.assert_called_with(
            sp_playlistcontainer, sp_link)
        self.assertIsInstance(result, spotify.Playlist)
        self.assertEqual(result._sp_playlist, sp_playlist)
        lib_mock.sp_playlist_add_ref.assert_called_with(sp_playlist)
        self.assertEqual(
            lib_mock.sp_playlistcontainer_move_playlist.call_count, 0)

    def test_add_playlist_from_playlist(self, lib_mock):
        tests.create_session()
        sp_link = spotify.ffi.new('int *')
        link = spotify.Link(sp_link=sp_link, add_ref=False)
        existing_playlist = mock.Mock(spec=spotify.Playlist)
        existing_playlist.link = link
        added_sp_playlist = spotify.ffi.new('int *')
        lib_mock.sp_playlistcontainer_add_playlist.return_value = (
            added_sp_playlist)
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)

        result = playlist_container.add_playlist(existing_playlist)

        lib_mock.sp_playlistcontainer_add_playlist.assert_called_with(
            sp_playlistcontainer, sp_link)
        self.assertIsInstance(result, spotify.Playlist)
        self.assertEqual(result._sp_playlist, added_sp_playlist)
        lib_mock.sp_playlist_add_ref.assert_called_with(added_sp_playlist)
        self.assertEqual(
            lib_mock.sp_playlistcontainer_move_playlist.call_count, 0)

    def test_add_playlist_at_given_index(self, lib_mock):
        tests.create_session()
        sp_link = spotify.ffi.new('int *')
        link = spotify.Link(sp_link=sp_link, add_ref=False)
        sp_playlist = spotify.ffi.new('int *')
        lib_mock.sp_playlistcontainer_add_playlist.return_value = sp_playlist
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)
        lib_mock.sp_playlistcontainer_num_playlists.return_value = 100
        lib_mock.sp_playlistcontainer_move_playlist.return_value = int(
            spotify.ErrorType.OK)

        result = playlist_container.add_playlist(link, index=7)

        lib_mock.sp_playlistcontainer_add_playlist.assert_called_with(
            sp_playlistcontainer, sp_link)
        self.assertIsInstance(result, spotify.Playlist)
        self.assertEqual(result._sp_playlist, sp_playlist)
        lib_mock.sp_playlist_add_ref.assert_called_with(sp_playlist)
        lib_mock.sp_playlistcontainer_move_playlist.assert_called_with(
            sp_playlistcontainer, 99, 7, 0)

    def test_add_playlist_already_in_the_container(self, lib_mock):
        tests.create_session()
        sp_link = spotify.ffi.new('int *')
        link = spotify.Link(sp_link=sp_link, add_ref=False)
        lib_mock.sp_playlistcontainer_add_playlist.return_value = (
            spotify.ffi.NULL)
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)

        result = playlist_container.add_playlist(link)

        lib_mock.sp_playlistcontainer_add_playlist.assert_called_with(
            sp_playlistcontainer, sp_link)
        self.assertIsNone(result)
        self.assertEqual(
            lib_mock.sp_playlistcontainer_move_playlist.call_count, 0)

    def test_add_playlist_from_unknown_type_fails(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)

        with self.assertRaises(TypeError):
            playlist_container.add_playlist(None)

    def test_add_folder(self, lib_mock):
        lib_mock.sp_playlistcontainer_add_folder.return_value = int(
            spotify.ErrorType.OK)
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)

        playlist_container.add_folder('foo bar', index=3)

        lib_mock.sp_playlistcontainer_add_folder.assert_called_with(
            sp_playlistcontainer, 3, mock.ANY)
        self.assertEqual(
            spotify.ffi.string(
                lib_mock.sp_playlistcontainer_add_folder.call_args[0][2]),
            b'foo bar')

    def test_add_folder_without_index_adds_to_end(self, lib_mock):
        lib_mock.sp_playlistcontainer_num_playlists.return_value = 7
        lib_mock.sp_playlistcontainer_add_folder.return_value = int(
            spotify.ErrorType.OK)
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)

        playlist_container.add_folder('foo bar')

        lib_mock.sp_playlistcontainer_add_folder.assert_called_with(
            sp_playlistcontainer, 7, mock.ANY)
        self.assertEqual(
            spotify.ffi.string(
                lib_mock.sp_playlistcontainer_add_folder.call_args[0][2]),
            b'foo bar')

    def test_add_folder_out_of_range_fails(self, lib_mock):
        lib_mock.sp_playlistcontainer_add_folder.return_value = int(
            spotify.ErrorType.INDEX_OUT_OF_RANGE)

        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)

        with self.assertRaises(spotify.Error):
            playlist_container.add_folder('foo bar', index=3)

    def test_add_folder_fails_if_name_is_space_only(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)

        with self.assertRaises(ValueError):
            playlist_container.add_folder('   ')

        # Spotify seems to accept e.g. tab-only names, but it doesn't make any
        # sense to allow it, so we disallow names with all combinations of just
        # whitespace.
        with self.assertRaises(ValueError):
            playlist_container.add_folder('\t\t')
        with self.assertRaises(ValueError):
            playlist_container.add_folder('\r\r')
        with self.assertRaises(ValueError):
            playlist_container.add_folder('\n\n')
        with self.assertRaises(ValueError):
            playlist_container.add_folder(' \t\r\n')

    def test_add_folder_fails_if_name_is_too_long(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)

        with self.assertRaises(ValueError):
            playlist_container.add_folder('x' * 300)

    def test_remove_playlist(self, lib_mock):
        tests.create_session()
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)
        lib_mock.sp_playlistcontainer_num_playlists.return_value = 9
        sp_playlist = spotify.ffi.new('int *')
        lib_mock.sp_playlistcontainer_playlist.return_value = sp_playlist
        lib_mock.sp_playlistcontainer_playlist_type.return_value = int(
            spotify.PlaylistType.PLAYLIST)
        lib_mock.sp_playlistcontainer_remove_playlist.return_value = int(
            spotify.ErrorType.OK)

        playlist_container.remove_playlist(5)

        lib_mock.sp_playlistcontainer_remove_playlist.assert_called_with(
            sp_playlistcontainer, 5)

    def test_remove_playlist_out_of_range_fails(self, lib_mock):
        tests.create_session()
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)
        lib_mock.sp_playlistcontainer_num_playlists.return_value = 9
        sp_playlist = spotify.ffi.new('int *')
        lib_mock.sp_playlistcontainer_playlist.return_value = sp_playlist
        lib_mock.sp_playlistcontainer_playlist_type.return_value = int(
            spotify.PlaylistType.PLAYLIST)
        lib_mock.sp_playlistcontainer_remove_playlist.return_value = int(
            spotify.ErrorType.INDEX_OUT_OF_RANGE)

        with self.assertRaises(spotify.Error):
            playlist_container.remove_playlist(3)

    def test_remove_start_folder_removes_end_folder_too(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)
        lib_mock.sp_playlistcontainer_num_playlists.return_value = 3
        sp_playlist = spotify.ffi.new('int *')
        lib_mock.sp_playlistcontainer_playlist.return_value = sp_playlist
        lib_mock.sp_playlistcontainer_playlist_type.side_effect = [
            int(spotify.PlaylistType.START_FOLDER),
            int(spotify.PlaylistType.PLAYLIST),
            int(spotify.PlaylistType.END_FOLDER),
        ]
        lib_mock.sp_playlistcontainer_playlist_folder_id.side_effect = [
            173, 173]
        playlist_container._find_folder_indexes = lambda *a: [0, 2]
        lib_mock.sp_playlistcontainer_remove_playlist.return_value = int(
            spotify.ErrorType.OK)

        playlist_container.remove_playlist(0)

        lib_mock.sp_playlistcontainer_playlist_type.assert_called_with(
            sp_playlistcontainer, 0)
        lib_mock.sp_playlistcontainer_playlist_folder_id.assert_called_with(
            sp_playlistcontainer, 0)
        lib_mock.sp_playlistcontainer_remove_playlist.assert_has_calls([
            mock.call(sp_playlistcontainer, 2),
            mock.call(sp_playlistcontainer, 0),
        ], any_order=False)

    def test_remove_end_folder_removes_start_folder_too(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)
        lib_mock.sp_playlistcontainer_num_playlists.return_value = 3
        sp_playlist = spotify.ffi.new('int *')
        lib_mock.sp_playlistcontainer_playlist.return_value = sp_playlist
        lib_mock.sp_playlistcontainer_playlist_type.side_effect = [
            int(spotify.PlaylistType.START_FOLDER),
            int(spotify.PlaylistType.PLAYLIST),
            int(spotify.PlaylistType.END_FOLDER),
        ]
        lib_mock.sp_playlistcontainer_playlist_folder_id.side_effect = [
            173, 173]
        playlist_container._find_folder_indexes = lambda *a: [0, 2]
        lib_mock.sp_playlistcontainer_remove_playlist.return_value = int(
            spotify.ErrorType.OK)

        playlist_container.remove_playlist(2)

        lib_mock.sp_playlistcontainer_playlist_type.assert_called_with(
            sp_playlistcontainer, 2)
        lib_mock.sp_playlistcontainer_playlist_folder_id.assert_called_with(
            sp_playlistcontainer, 2)
        lib_mock.sp_playlistcontainer_remove_playlist.assert_has_calls([
            mock.call(sp_playlistcontainer, 2),
            mock.call(sp_playlistcontainer, 0),
        ], any_order=False)

    def test_remove_folder_with_everything_in_it(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)
        lib_mock.sp_playlistcontainer_num_playlists.return_value = 3
        sp_playlist = spotify.ffi.new('int *')
        lib_mock.sp_playlistcontainer_playlist.return_value = sp_playlist
        lib_mock.sp_playlistcontainer_playlist_type.side_effect = [
            int(spotify.PlaylistType.START_FOLDER),
            int(spotify.PlaylistType.PLAYLIST),
            int(spotify.PlaylistType.END_FOLDER),
        ]
        lib_mock.sp_playlistcontainer_playlist_folder_id.side_effect = [
            173, 173]
        playlist_container._find_folder_indexes = lambda *a: [0, 1, 2]
        lib_mock.sp_playlistcontainer_remove_playlist.return_value = int(
            spotify.ErrorType.OK)

        playlist_container.remove_playlist(0, recursive=True)

        lib_mock.sp_playlistcontainer_playlist_type.assert_called_with(
            sp_playlistcontainer, 0)
        lib_mock.sp_playlistcontainer_playlist_folder_id.assert_called_with(
            sp_playlistcontainer, 0)
        lib_mock.sp_playlistcontainer_remove_playlist.assert_has_calls([
            mock.call(sp_playlistcontainer, 2),
            mock.call(sp_playlistcontainer, 1),
            mock.call(sp_playlistcontainer, 0),
        ], any_order=False)

    def test_find_folder_indexes(self, lib_mock):
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)
        playlists = [
            spotify.PlaylistFolder(
                173, 'foo', spotify.PlaylistType.START_FOLDER),
            playlist,
            spotify.PlaylistFolder(
                173, '', spotify.PlaylistType.END_FOLDER),
        ]

        result = spotify.PlaylistContainer._find_folder_indexes(
            playlists, 173, recursive=False)

        self.assertEqual(result, [0, 2])

    def test_find_folder_indexes_with_unknown_id(self, lib_mock):
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)
        playlists = [
            spotify.PlaylistFolder(
                173, 'foo', spotify.PlaylistType.START_FOLDER),
            playlist,
            spotify.PlaylistFolder(
                173, '', spotify.PlaylistType.END_FOLDER),
        ]

        result = spotify.PlaylistContainer._find_folder_indexes(
            playlists, 174, recursive=False)

        self.assertEqual(result, [])

    def test_find_folder_indexes_recursive(self, lib_mock):
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)
        playlists = [
            spotify.PlaylistFolder(
                173, 'foo', spotify.PlaylistType.START_FOLDER),
            playlist,
            spotify.PlaylistFolder(
                173, '', spotify.PlaylistType.END_FOLDER),
        ]

        result = spotify.PlaylistContainer._find_folder_indexes(
            playlists, 173, recursive=True)

        self.assertEqual(result, [0, 1, 2])

    def test_find_folder_indexes_without_end(self, lib_mock):
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)
        playlists = [
            spotify.PlaylistFolder(
                173, 'foo', spotify.PlaylistType.START_FOLDER),
            playlist,
        ]

        result = spotify.PlaylistContainer._find_folder_indexes(
            playlists, 173, recursive=True)

        self.assertEqual(result, [0])

    def test_find_folder_indexes_without_start(self, lib_mock):
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)
        playlists = [
            playlist,
            spotify.PlaylistFolder(
                173, '', spotify.PlaylistType.END_FOLDER),
        ]

        result = spotify.PlaylistContainer._find_folder_indexes(
            playlists, 173, recursive=True)

        self.assertEqual(result, [1])

    def test_move_playlist(self, lib_mock):
        lib_mock.sp_playlistcontainer_move_playlist.return_value = int(
            spotify.ErrorType.OK)
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)

        playlist_container.move_playlist(5, 7)

        lib_mock.sp_playlistcontainer_move_playlist.assert_called_with(
            sp_playlistcontainer, 5, 7, 0)

    def test_move_playlist_dry_run(self, lib_mock):
        lib_mock.sp_playlistcontainer_move_playlist.return_value = int(
            spotify.ErrorType.OK)
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)

        playlist_container.move_playlist(5, 7, dry_run=True)

        lib_mock.sp_playlistcontainer_move_playlist.assert_called_with(
            sp_playlistcontainer, 5, 7, 1)

    def test_move_playlist_out_of_range_fails(self, lib_mock):
        lib_mock.sp_playlistcontainer_move_playlist.return_value = int(
            spotify.ErrorType.INDEX_OUT_OF_RANGE)
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)

        with self.assertRaises(spotify.Error):
            playlist_container.move_playlist(5, 7)

    @mock.patch('spotify.User', spec=spotify.User)
    def test_owner(self, user_mock, lib_mock):
        user_mock.return_value = mock.sentinel.user
        sp_user = spotify.ffi.new('int *')
        lib_mock.sp_playlistcontainer_owner.return_value = sp_user
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)

        result = playlist_container.owner

        lib_mock.sp_playlistcontainer_owner.assert_called_with(
            sp_playlistcontainer)
        user_mock.assert_called_with(sp_user=sp_user)
        self.assertEqual(result, mock.sentinel.user)

    def test_get_unseen_tracks(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)
        lib_mock.sp_playlistcontainer_get_unseen_tracks.return_value = 0

        result = playlist_container.get_unseen_tracks(playlist)

        self.assertIsInstance(result, spotify.PlaylistUnseenTracks)
        self.assertEqual(len(result), 0)

    def test_clear_unseen_tracks(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)
        lib_mock.sp_playlistcontainer_clear_unseen_tracks.return_value = 0

        playlist_container.clear_unseen_tracks(playlist)

        lib_mock.sp_playlistcontainer_clear_unseen_tracks.assert_called_with(
            sp_playlistcontainer, sp_playlist)

    def test_clear_unseen_tracks_raises_error_on_failure(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)
        lib_mock.sp_playlistcontainer_clear_unseen_tracks.return_value = -1

        with self.assertRaises(spotify.Error):
            playlist_container.clear_unseen_tracks(playlist)

    def test_first_on_call_adds_obj_emitters_list(self, lib_mock):
        session = tests.create_session()
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)

        playlist_container.on(
            spotify.PlaylistContainerEvent.PLAYLIST_ADDED, lambda *args: None)

        self.assertIn(playlist_container, session._emitters)

        playlist_container.off()

    def test_last_off_call_removes_obj_from_emitters_list(self, lib_mock):
        session = tests.create_session()
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)

        playlist_container.on(
            spotify.PlaylistContainerEvent.PLAYLIST_ADDED, lambda *args: None)
        playlist_container.off(
            spotify.PlaylistContainerEvent.PLAYLIST_ADDED)

        self.assertNotIn(playlist_container, session._emitters)

    def test_other_off_calls_keeps_obj_in_emitters_list(self, lib_mock):
        session = tests.create_session()
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)

        playlist_container.on(
            spotify.PlaylistContainerEvent.PLAYLIST_ADDED, lambda *args: None)
        playlist_container.on(
            spotify.PlaylistContainerEvent.PLAYLIST_MOVED, lambda *args: None)
        playlist_container.off(
            spotify.PlaylistContainerEvent.PLAYLIST_ADDED)

        self.assertIn(playlist_container, session._emitters)

        playlist_container.off(
            spotify.PlaylistContainerEvent.PLAYLIST_MOVED)

        self.assertNotIn(playlist_container, session._emitters)


@mock.patch('spotify.playlist.lib', spec=spotify.lib)
class PlaylistContainerCallbacksTest(unittest.TestCase):

    def tearDown(self):
        spotify.session_instance = None

    def test_playlist_added_callback(self, lib_mock):
        tests.create_session()
        callback = mock.Mock()
        sp_playlist = spotify.ffi.cast('sp_playlist *', 42)
        sp_playlistcontainer = spotify.ffi.cast('sp_playlistcontainer *', 43)
        playlist_container = spotify.PlaylistContainer._cached(
            sp_playlistcontainer=sp_playlistcontainer)
        playlist_container.on(
            spotify.PlaylistContainerEvent.PLAYLIST_ADDED, callback)

        _PlaylistContainerCallbacks.playlist_added(
            sp_playlistcontainer, sp_playlist, 7, spotify.ffi.NULL)

        callback.assert_called_once_with(playlist_container, mock.ANY, 7)
        playlist = callback.call_args[0][1]
        self.assertIsInstance(playlist, spotify.Playlist)
        self.assertEqual(playlist._sp_playlist, sp_playlist)

    def test_playlist_removed_callback(self, lib_mock):
        tests.create_session()
        callback = mock.Mock()
        sp_playlist = spotify.ffi.cast('sp_playlist *', 42)
        sp_playlistcontainer = spotify.ffi.cast('sp_playlistcontainer *', 43)
        playlist_container = spotify.PlaylistContainer._cached(
            sp_playlistcontainer=sp_playlistcontainer)
        playlist_container.on(
            spotify.PlaylistContainerEvent.PLAYLIST_REMOVED, callback)

        _PlaylistContainerCallbacks.playlist_removed(
            sp_playlistcontainer, sp_playlist, 7, spotify.ffi.NULL)

        callback.assert_called_once_with(playlist_container, mock.ANY, 7)
        playlist = callback.call_args[0][1]
        self.assertIsInstance(playlist, spotify.Playlist)
        self.assertEqual(playlist._sp_playlist, sp_playlist)

    def test_playlist_moved_callback(self, lib_mock):
        tests.create_session()
        callback = mock.Mock()
        sp_playlist = spotify.ffi.cast('sp_playlist *', 42)
        sp_playlistcontainer = spotify.ffi.cast('sp_playlistcontainer *', 43)
        playlist_container = spotify.PlaylistContainer._cached(
            sp_playlistcontainer=sp_playlistcontainer)
        playlist_container.on(
            spotify.PlaylistContainerEvent.PLAYLIST_MOVED, callback)

        _PlaylistContainerCallbacks.playlist_moved(
            sp_playlistcontainer, sp_playlist, 7, 13, spotify.ffi.NULL)

        callback.assert_called_once_with(playlist_container, mock.ANY, 7, 13)
        playlist = callback.call_args[0][1]
        self.assertIsInstance(playlist, spotify.Playlist)
        self.assertEqual(playlist._sp_playlist, sp_playlist)

    def test_container_loaded_callback(self, lib_mock):
        tests.create_session()
        callback = mock.Mock()
        sp_playlistcontainer = spotify.ffi.cast('sp_playlistcontainer *', 43)
        playlist_container = spotify.PlaylistContainer._cached(
            sp_playlistcontainer=sp_playlistcontainer)
        playlist_container.on(
            spotify.PlaylistContainerEvent.CONTAINER_LOADED, callback)

        _PlaylistContainerCallbacks.container_loaded(
            sp_playlistcontainer, spotify.ffi.NULL)

        callback.assert_called_once_with(playlist_container)


class PlaylistFolderTest(unittest.TestCase):

    def test_id(self):
        folder = spotify.PlaylistFolder(
            id=123, name='foo', type=spotify.PlaylistType.START_FOLDER)

        self.assertEqual(folder.id, 123)

    def test_image(self):
        folder = spotify.PlaylistFolder(
            id=123, name='foo', type=spotify.PlaylistType.START_FOLDER)

        self.assertEqual(folder.name, 'foo')

    def test_type(self):
        folder = spotify.PlaylistFolder(
            id=123, name='foo', type=spotify.PlaylistType.START_FOLDER)

        self.assertEqual(folder.type, spotify.PlaylistType.START_FOLDER)


class PlaylistOfflineStatusTest(unittest.TestCase):

    def test_has_constants(self):
        self.assertEqual(spotify.PlaylistOfflineStatus.NO, 0)
        self.assertEqual(spotify.PlaylistOfflineStatus.DOWNLOADING, 2)


@mock.patch('spotify.playlist.lib', spec=spotify.lib)
class PlaylistTrackTest(unittest.TestCase):

    @mock.patch('spotify.track.lib', spec=spotify.lib)
    def test_track(self, track_lib_mock, lib_mock):
        sp_track = spotify.ffi.cast('sp_track *', spotify.ffi.new('int *'))
        lib_mock.sp_playlist_track.return_value = sp_track
        sp_playlist = spotify.ffi.new('int *')
        playlist_track = spotify.PlaylistTrack(sp_playlist, 0)

        result = playlist_track.track

        lib_mock.sp_playlist_track.assert_called_with(sp_playlist, 0)
        track_lib_mock.sp_track_add_ref.assert_called_with(sp_track)
        self.assertIsInstance(result, spotify.Track)
        self.assertEqual(result._sp_track, sp_track)

    def test_create_time(self, lib_mock):
        lib_mock.sp_playlist_track_create_time.return_value = 1234567890
        sp_playlist = spotify.ffi.new('int *')
        playlist_track = spotify.PlaylistTrack(sp_playlist, 0)

        result = playlist_track.create_time

        lib_mock.sp_playlist_track_create_time.assert_called_with(
            sp_playlist, 0)
        self.assertEqual(result, 1234567890)

    @mock.patch('spotify.user.lib', spec=spotify.lib)
    def test_creator(self, user_lib_mock, lib_mock):
        sp_user = spotify.ffi.cast('sp_user *', spotify.ffi.new('int *'))
        lib_mock.sp_playlist_track_creator.return_value = sp_user
        sp_playlist = spotify.ffi.new('int *')
        playlist_track = spotify.PlaylistTrack(sp_playlist, 0)

        result = playlist_track.creator

        lib_mock.sp_playlist_track_creator.assert_called_with(sp_playlist, 0)
        user_lib_mock.sp_user_add_ref.assert_called_with(sp_user)
        self.assertIsInstance(result, spotify.User)
        self.assertEqual(result._sp_user, sp_user)

    def test_is_seen(self, lib_mock):
        lib_mock.sp_playlist_track_seen.return_value = 0
        sp_playlist = spotify.ffi.new('int *')
        playlist_track = spotify.PlaylistTrack(sp_playlist, 0)

        result = playlist_track.seen

        lib_mock.sp_playlist_track_seen.assert_called_with(sp_playlist, 0)
        self.assertEqual(result, False)

    def test_set_seen(self, lib_mock):
        lib_mock.sp_playlist_track_set_seen.return_value = int(
            spotify.ErrorType.OK)
        sp_playlist = spotify.ffi.new('int *')
        playlist_track = spotify.PlaylistTrack(sp_playlist, 0)

        playlist_track.seen = True

        lib_mock.sp_playlist_track_set_seen.assert_called_with(
            sp_playlist, 0, 1)

    def test_set_seen_fails_if_error(self, lib_mock):
        lib_mock.sp_playlist_track_set_seen.return_value = int(
            spotify.ErrorType.BAD_API_VERSION)
        sp_playlist = spotify.ffi.new('int *')
        playlist_track = spotify.PlaylistTrack(sp_playlist, 0)

        with self.assertRaises(spotify.Error):
            playlist_track.seen = True

    def test_message(self, lib_mock):
        lib_mock.sp_playlist_track_message.return_value = spotify.ffi.new(
            'char[]', b'foo bar')
        sp_playlist = spotify.ffi.new('int *')
        playlist_track = spotify.PlaylistTrack(sp_playlist, 0)

        result = playlist_track.message

        lib_mock.sp_playlist_track_message.assert_called_with(sp_playlist, 0)
        self.assertEqual(result, 'foo bar')

    def test_message_is_none_when_null(self, lib_mock):
        lib_mock.sp_playlist_track_message.return_value = spotify.ffi.NULL
        sp_playlist = spotify.ffi.new('int *')
        playlist_track = spotify.PlaylistTrack(sp_playlist, 0)

        result = playlist_track.message

        lib_mock.sp_playlist_track_message.assert_called_with(sp_playlist, 0)
        self.assertIsNone(result)


class PlaylistTypeTest(unittest.TestCase):

    def test_has_constants(self):
        self.assertEqual(spotify.PlaylistType.PLAYLIST, 0)
        self.assertEqual(spotify.PlaylistType.START_FOLDER, 1)
        self.assertEqual(spotify.PlaylistType.END_FOLDER, 2)


@mock.patch('spotify.playlist.lib', spec=spotify.lib)
class PlaylistUnseenTracksTest(unittest.TestCase):

    # TODO Test that the collection releases sp_playlistcontainer and
    # sp_playlist when no longer referenced.

    def tearDown(self):
        spotify.session_instance = None

    @mock.patch('spotify.track.lib', spec=spotify.lib)
    def test_normal_usage(self, track_lib_mock, lib_mock):
        sp_playlistcontainer = spotify.ffi.new('int *')
        sp_playlist = spotify.ffi.new('int *')

        total_num_tracks = 3
        sp_tracks = [
            spotify.ffi.cast('sp_track *', spotify.ffi.new('int *'))
            for i in range(total_num_tracks)]

        def func(sp_pc, sp_p, sp_t, num_t):
            for i in range(min(total_num_tracks, num_t)):
                sp_t[i] = sp_tracks[i]
            return total_num_tracks

        lib_mock.sp_playlistcontainer_get_unseen_tracks.side_effect = func

        tracks = spotify.PlaylistUnseenTracks(
            sp_playlistcontainer, sp_playlist)

        # Collection keeps references to container and playlist:
        lib_mock.sp_playlistcontainer_add_ref.assert_called_with(
            sp_playlistcontainer)
        lib_mock.sp_playlist_add_ref.assert_called_with(sp_playlist)

        # Getting collection and length causes no tracks to be retrieved:
        self.assertEqual(len(tracks), total_num_tracks)
        self.assertEqual(
            lib_mock.sp_playlistcontainer_get_unseen_tracks.call_count, 1)
        lib_mock.sp_playlistcontainer_get_unseen_tracks.assert_called_with(
            sp_playlistcontainer, sp_playlist, mock.ANY, 0)

        # Getting items causes more tracks to be retrieved:
        track0 = tracks[0]
        self.assertEqual(
            lib_mock.sp_playlistcontainer_get_unseen_tracks.call_count, 2)
        lib_mock.sp_playlistcontainer_get_unseen_tracks.assert_called_with(
            sp_playlistcontainer, sp_playlist, mock.ANY, total_num_tracks)
        self.assertIsInstance(track0, spotify.Track)
        self.assertEqual(track0._sp_track, sp_tracks[0])

        # Getting alrady retrieved tracks causes no new retrieval:
        track1 = tracks[1]
        self.assertEqual(
            lib_mock.sp_playlistcontainer_get_unseen_tracks.call_count, 2)
        self.assertIsInstance(track1, spotify.Track)
        self.assertEqual(track1._sp_track, sp_tracks[1])

    def test_raises_error_on_failure(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.new('int *')
        sp_playlist = spotify.ffi.new('int *')
        lib_mock.sp_playlistcontainer_get_unseen_tracks.return_value = -3

        with self.assertRaises(spotify.Error):
            spotify.PlaylistUnseenTracks(sp_playlistcontainer, sp_playlist)

    @mock.patch('spotify.track.lib', spec=spotify.lib)
    def test_getitem_with_slice(self, track_lib_mock, lib_mock):
        tests.create_session()
        sp_playlistcontainer = spotify.ffi.new('int *')
        sp_playlist = spotify.ffi.new('int *')

        total_num_tracks = 3
        sp_tracks = [
            spotify.ffi.cast('sp_track *', spotify.ffi.new('int *'))
            for i in range(total_num_tracks)]

        def func(sp_pc, sp_p, sp_t, num_t):
            for i in range(min(total_num_tracks, num_t)):
                sp_t[i] = sp_tracks[i]
            return total_num_tracks

        lib_mock.sp_playlistcontainer_get_unseen_tracks.side_effect = func

        tracks = spotify.PlaylistUnseenTracks(
            sp_playlistcontainer, sp_playlist)

        result = tracks[0:2]

        # Only a subslice of length 2 is returned
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], spotify.Track)
        self.assertEqual(result[0]._sp_track, sp_tracks[0])
        self.assertIsInstance(result[1], spotify.Track)
        self.assertEqual(result[1]._sp_track, sp_tracks[1])

    def test_getitem_raises_index_error_on_negative_index(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.new('int *')
        sp_playlist = spotify.ffi.new('int *')
        lib_mock.sp_playlistcontainer_get_unseen_tracks.return_value = 0
        tracks = spotify.PlaylistUnseenTracks(
            sp_playlistcontainer, sp_playlist)

        with self.assertRaises(IndexError) as ctx:
            tracks[-1]

        self.assertEqual(str(ctx.exception), 'list index out of range')

    def test_getitem_raises_index_error_on_too_high_index(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.new('int *')
        sp_playlist = spotify.ffi.new('int *')
        lib_mock.sp_playlistcontainer_get_unseen_tracks.return_value = 0
        tracks = spotify.PlaylistUnseenTracks(
            sp_playlistcontainer, sp_playlist)

        with self.assertRaises(IndexError) as ctx:
            tracks[1]

        self.assertEqual(str(ctx.exception), 'list index out of range')

    def test_getitem_raises_type_error_on_non_integral_index(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.new('int *')
        sp_playlist = spotify.ffi.new('int *')
        lib_mock.sp_playlistcontainer_get_unseen_tracks.return_value = 0
        tracks = spotify.PlaylistUnseenTracks(
            sp_playlistcontainer, sp_playlist)

        with self.assertRaises(TypeError):
            tracks['abc']

    def test_repr(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.new('int *')
        sp_playlist = spotify.ffi.new('int *')
        lib_mock.sp_playlistcontainer_get_unseen_tracks.return_value = 0
        tracks = spotify.PlaylistUnseenTracks(
            sp_playlistcontainer, sp_playlist)

        self.assertEqual(repr(tracks), '[]')
