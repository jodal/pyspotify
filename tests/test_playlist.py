# encoding: utf-8

from __future__ import unicode_literals

import unittest

import spotify
import tests
from spotify import compat
from spotify.playlist import _PlaylistCallbacks
from tests import mock


@mock.patch("spotify.playlist.lib", spec=spotify.lib)
class PlaylistTest(unittest.TestCase):
    def setUp(self):
        self.session = tests.create_session_mock()

    def test_create_without_uri_or_sp_playlist_fails(self, lib_mock):
        with self.assertRaises(AssertionError):
            spotify.Playlist(self.session)

    @mock.patch("spotify.Link", spec=spotify.Link)
    def test_create_from_uri(self, link_mock, lib_mock):
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        link_instance_mock = link_mock.return_value
        link_instance_mock._as_sp_playlist.return_value = sp_playlist
        uri = "spotify:playlist:foo"

        result = spotify.Playlist(self.session, uri=uri)

        link_mock.assert_called_once_with(self.session, uri)
        link_instance_mock._as_sp_playlist.assert_called_once_with()
        self.assertEqual(link_instance_mock.as_playlist.call_count, 0)
        self.assertEqual(lib_mock.sp_playlist_add_ref.call_count, 0)
        self.assertEqual(result._sp_playlist, sp_playlist)

    @mock.patch("spotify.Link", spec=spotify.Link)
    def test_create_from_uri_is_cached(self, link_mock, lib_mock):
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        link_instance_mock = link_mock.return_value
        link_instance_mock._as_sp_playlist.return_value = sp_playlist
        uri = "spotify:playlist:foo"

        result = spotify.Playlist(self.session, uri=uri)

        self.assertEqual(self.session._cache[sp_playlist], result)

    @mock.patch("spotify.Link", spec=spotify.Link)
    def test_create_from_uri_fail_raises_error(self, link_mock, lib_mock):
        link_instance_mock = link_mock.return_value
        link_instance_mock._as_sp_playlist.return_value = None
        uri = "spotify:playlist:foo"

        with self.assertRaises(spotify.Error):
            spotify.Playlist(self.session, uri=uri)

    def test_life_cycle(self, lib_mock):
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)

        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)
        sp_playlist = playlist._sp_playlist

        lib_mock.sp_playlist_add_ref.assert_called_with(sp_playlist)

        # Callbacks are only added when someone registers a Python event
        # handler on the playlist:
        lib_mock.sp_playlist_add_callbacks.assert_not_called()
        playlist.on(spotify.PlaylistEvent.TRACKS_ADDED, lambda *args: None)
        lib_mock.sp_playlist_add_callbacks.assert_called_with(
            sp_playlist, mock.ANY, mock.ANY
        )

        playlist = None  # noqa
        tests.gc_collect()

        # Callbacks are removed when the playlist is GC-ed:
        lib_mock.sp_playlist_remove_callbacks.assert_called_with(
            sp_playlist, mock.ANY, mock.ANY
        )

        # FIXME Won't be called because lib_mock has references to the
        # sp_playlist object, and it thus won't be GC-ed.
        # lib_mock.sp_playlist_release.assert_called_with(sp_playlist)

    def test_cached_playlist(self, lib_mock):
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)

        result1 = spotify.Playlist._cached(self.session, sp_playlist)
        result2 = spotify.Playlist._cached(self.session, sp_playlist)

        self.assertIsInstance(result1, spotify.Playlist)
        self.assertIs(result1, result2)

    @mock.patch("spotify.Link", spec=spotify.Link)
    def test_repr(self, link_mock, lib_mock):
        lib_mock.sp_playlist_is_loaded.return_value = 1
        link_instance_mock = link_mock.return_value
        link_instance_mock.uri = "foo"
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)

        result = repr(playlist)

        self.assertEqual(result, "Playlist(%r)" % "foo")

    @mock.patch("spotify.Link", spec=spotify.Link)
    def test_repr_if_unloaded(self, link_mock, lib_mock):
        lib_mock.sp_playlist_is_loaded.return_value = 0
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)

        result = repr(playlist)

        self.assertEqual(result, "Playlist(<not loaded>)")

    @mock.patch("spotify.Link", spec=spotify.Link)
    def test_repr_if_link_creation_fails(self, link_mock, lib_mock):
        lib_mock.sp_playlist_is_loaded.return_value = 1
        link_mock.side_effect = spotify.Error("error message")
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)

        result = repr(playlist)

        self.assertEqual(result, "Playlist(<error: error message>)")

    def test_eq(self, lib_mock):
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist1 = spotify.Playlist(self.session, sp_playlist=sp_playlist)
        playlist2 = spotify.Playlist(self.session, sp_playlist=sp_playlist)

        self.assertTrue(playlist1 == playlist2)
        self.assertFalse(playlist1 == "foo")

    def test_ne(self, lib_mock):
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist1 = spotify.Playlist(self.session, sp_playlist=sp_playlist)
        playlist2 = spotify.Playlist(self.session, sp_playlist=sp_playlist)

        self.assertFalse(playlist1 != playlist2)

    def test_hash(self, lib_mock):
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist1 = spotify.Playlist(self.session, sp_playlist=sp_playlist)
        playlist2 = spotify.Playlist(self.session, sp_playlist=sp_playlist)

        self.assertEqual(hash(playlist1), hash(playlist2))

    def test_is_loaded(self, lib_mock):
        lib_mock.sp_playlist_is_loaded.return_value = 1
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)

        result = playlist.is_loaded

        lib_mock.sp_playlist_is_loaded.assert_called_once_with(sp_playlist)
        self.assertTrue(result)

    @mock.patch("spotify.utils.load")
    def test_load(self, load_mock, lib_mock):
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)

        playlist.load(10)

        load_mock.assert_called_with(self.session, playlist, timeout=10)

    @mock.patch("spotify.track.lib", spec=spotify.lib)
    def test_tracks(self, track_lib_mock, lib_mock):
        sp_track = spotify.ffi.cast("sp_track *", 43)
        lib_mock.sp_playlist_num_tracks.return_value = 1
        lib_mock.sp_playlist_track.return_value = sp_track
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)

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
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)

        result = playlist.tracks

        self.assertEqual(len(result), 0)
        lib_mock.sp_playlist_num_tracks.assert_called_with(sp_playlist)
        self.assertEqual(lib_mock.sp_playlist_track.call_count, 0)

    def test_tracks_if_unloaded(self, lib_mock):
        lib_mock.sp_playlist_is_loaded.return_value = 0
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)

        result = playlist.tracks

        lib_mock.sp_playlist_is_loaded.assert_called_with(sp_playlist)
        self.assertEqual(len(result), 0)

    def test_tracks_is_a_mutable_sequence(self, lib_mock):
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)

        self.assertIsInstance(playlist.tracks, compat.MutableSequence)

    def test_tracks_setitem(self, lib_mock):
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)
        tracks = playlist.tracks
        tracks.__len__ = mock.Mock(return_value=5)
        playlist.remove_tracks = mock.Mock()
        playlist.add_tracks = mock.Mock()

        tracks[0] = mock.sentinel.track

        playlist.add_tracks.assert_called_with(mock.sentinel.track, index=0)
        playlist.remove_tracks.assert_called_with(1)

    def test_tracks_setitem_with_slice(self, lib_mock):
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)
        tracks = playlist.tracks
        tracks.__len__ = mock.Mock(return_value=5)
        playlist.remove_tracks = mock.Mock()
        playlist.add_tracks = mock.Mock()

        tracks[0:2] = [mock.sentinel.track1, mock.sentinel.track2]

        playlist.add_tracks.assert_has_calls(
            [
                mock.call(mock.sentinel.track1, index=0),
                mock.call(mock.sentinel.track2, index=1),
            ],
            any_order=False,
        )
        playlist.remove_tracks.assert_has_calls(
            [mock.call(3), mock.call(2)], any_order=False
        )

    def test_tracks_setittem_with_slice_and_noniterable_value_fails(self, lib_mock):
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)
        tracks = playlist.tracks
        tracks.__len__ = mock.Mock(return_value=5)

        with self.assertRaises(TypeError):
            tracks[0:2] = mock.sentinel.track

    def test_tracks_setitem_raises_index_error_on_negative_index(self, lib_mock):
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)
        tracks = playlist.tracks
        tracks.__len__ = mock.Mock(return_value=5)

        with self.assertRaises(IndexError):
            tracks[-1] = None

    def test_tracks_setitem_raises_index_error_on_too_high_index(self, lib_mock):
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)
        tracks = playlist.tracks
        tracks.__len__ = mock.Mock(return_value=1)

        with self.assertRaises(IndexError):
            tracks[1] = None

    def test_tracks_setitem_raises_type_error_on_non_integral_index(self, lib_mock):
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)
        tracks = playlist.tracks
        tracks.__len__ = mock.Mock(return_value=1)

        with self.assertRaises(TypeError):
            tracks["abc"] = None

    def test_tracks_delitem(self, lib_mock):
        lib_mock.sp_playlist_remove_tracks.return_value = int(spotify.ErrorType.OK)
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)
        tracks = playlist.tracks
        tracks.__len__ = mock.Mock(return_value=4)

        del tracks[3]

        lib_mock.sp_playlist_remove_tracks.assert_called_with(sp_playlist, [3], 1)

    def test_tracks_delitem_with_slice(self, lib_mock):
        lib_mock.sp_playlist_remove_tracks.return_value = int(spotify.ErrorType.OK)
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)
        tracks = playlist.tracks
        tracks.__len__ = mock.Mock(return_value=3)

        del tracks[0:2]

        # Delete items in reverse order, so the indexes doesn't change
        lib_mock.sp_playlist_remove_tracks.assert_has_calls(
            [mock.call(sp_playlist, [1], 1), mock.call(sp_playlist, [0], 1)],
            any_order=False,
        )

    def test_tracks_delitem_raises_index_error_on_negative_index(self, lib_mock):
        lib_mock.sp_playlist_remove_tracks.return_value = int(spotify.ErrorType.OK)
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)
        tracks = playlist.tracks
        tracks.__len__ = mock.Mock(return_value=1)

        with self.assertRaises(IndexError):
            del tracks[-1]

    def test_tracks_delitem_raises_index_error_on_too_high_index(self, lib_mock):
        lib_mock.sp_playlist_remove_tracks.return_value = int(spotify.ErrorType.OK)
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)
        tracks = playlist.tracks
        tracks.__len__ = mock.Mock(return_value=1)

        with self.assertRaises(IndexError):
            del tracks[1]

    def test_tracks_delitem_raises_type_error_on_non_integral_index(self, lib_mock):
        lib_mock.sp_playlist_remove_tracks.return_value = int(spotify.ErrorType.OK)
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)
        tracks = playlist.tracks
        tracks.__len__ = mock.Mock(return_value=1)

        with self.assertRaises(TypeError):
            del tracks["abc"]

    def test_tracks_insert(self, lib_mock):
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)
        tracks = playlist.tracks
        tracks.__len__ = mock.Mock(return_value=5)
        playlist.add_tracks = mock.Mock()

        tracks.insert(3, mock.sentinel.track)

        playlist.add_tracks.assert_called_with(mock.sentinel.track, index=3)

    @mock.patch("spotify.playlist_track.lib", spec=spotify.lib)
    def test_tracks_with_metadata(self, playlist_track_lib_mock, lib_mock):
        lib_mock.sp_playlist_num_tracks.return_value = 1
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)

        # Created a Playlist with a ref to sp_playlist
        self.assertEqual(lib_mock.sp_playlist_add_ref.call_count, 1)
        self.assertEqual(playlist_track_lib_mock.sp_playlist_add_ref.call_count, 0)

        result = playlist.tracks_with_metadata

        # Created a Sequence with a ref to sp_playlist
        self.assertEqual(lib_mock.sp_playlist_add_ref.call_count, 2)
        self.assertEqual(playlist_track_lib_mock.sp_playlist_add_ref.call_count, 0)

        self.assertEqual(len(result), 1)
        lib_mock.sp_playlist_num_tracks.assert_called_with(sp_playlist)

        item = result[0]
        self.assertIsInstance(item, spotify.PlaylistTrack)

        # Created a PlaylistTrack with a ref to sp_playlist
        self.assertEqual(lib_mock.sp_playlist_add_ref.call_count, 2)
        self.assertEqual(playlist_track_lib_mock.sp_playlist_add_ref.call_count, 1)

    def test_tracks_with_metadata_if_no_tracks(self, lib_mock):
        lib_mock.sp_playlist_num_tracks.return_value = 0
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)

        result = playlist.tracks_with_metadata

        self.assertEqual(len(result), 0)
        lib_mock.sp_playlist_num_tracks.assert_called_with(sp_playlist)
        self.assertEqual(lib_mock.sp_playlist_track.call_count, 0)

    def test_tracks_with_metadata_if_unloaded(self, lib_mock):
        lib_mock.sp_playlist_is_loaded.return_value = 0
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)

        result = playlist.tracks_with_metadata

        lib_mock.sp_playlist_is_loaded.assert_called_with(sp_playlist)
        self.assertEqual(len(result), 0)

    def test_name(self, lib_mock):
        lib_mock.sp_playlist_name.return_value = spotify.ffi.new(
            "char[]", b"Foo Bar Baz"
        )
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)

        result = playlist.name

        lib_mock.sp_playlist_name.assert_called_once_with(sp_playlist)
        self.assertEqual(result, "Foo Bar Baz")

    def test_name_is_none_if_unloaded(self, lib_mock):
        lib_mock.sp_playlist_name.return_value = spotify.ffi.new("char[]", b"")
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)

        result = playlist.name

        lib_mock.sp_playlist_name.assert_called_once_with(sp_playlist)
        self.assertIsNone(result)

    def test_rename(self, lib_mock):
        lib_mock.sp_playlist_rename.return_value = int(spotify.ErrorType.OK)
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)

        playlist.rename("Quux")

        lib_mock.sp_playlist_rename.assert_called_with(sp_playlist, mock.ANY)
        self.assertEqual(
            spotify.ffi.string(lib_mock.sp_playlist_rename.call_args[0][1]),
            b"Quux",
        )

    def test_rename_fails_if_error(self, lib_mock):
        lib_mock.sp_playlist_rename.return_value = int(
            spotify.ErrorType.BAD_API_VERSION
        )
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)

        with self.assertRaises(spotify.Error):
            playlist.rename("Quux")

    def test_name_setter(self, lib_mock):
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)
        playlist.rename = mock.Mock()

        playlist.name = "Quux"

        playlist.rename.assert_called_with("Quux")

    @mock.patch("spotify.user.lib", spec=spotify.lib)
    def test_owner(self, user_lib_mock, lib_mock):
        sp_user = spotify.ffi.cast("sp_user *", 43)
        lib_mock.sp_playlist_owner.return_value = sp_user
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)

        result = playlist.owner

        lib_mock.sp_playlist_owner.assert_called_with(sp_playlist)
        self.assertIsInstance(result, spotify.User)
        self.assertEqual(result._sp_user, sp_user)
        user_lib_mock.sp_user_add_ref.assert_called_with(sp_user)

    def test_is_collaborative(self, lib_mock):
        lib_mock.sp_playlist_is_collaborative.return_value = 1
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)

        result = playlist.collaborative

        lib_mock.sp_playlist_is_collaborative.assert_called_with(sp_playlist)
        self.assertTrue(result)

    def test_set_collaborative(self, lib_mock):
        lib_mock.sp_playlist_set_collaborative.return_value = int(spotify.ErrorType.OK)
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)

        playlist.collaborative = False

        lib_mock.sp_playlist_set_collaborative.assert_called_with(sp_playlist, 0)

    def test_set_collaborative_fails_if_error(self, lib_mock):
        lib_mock.sp_playlist_set_collaborative.return_value = int(
            spotify.ErrorType.BAD_API_VERSION
        )
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)

        with self.assertRaises(spotify.Error):
            playlist.collaborative = False

    def test_set_autolink_tracks(self, lib_mock):
        lib_mock.sp_playlist_set_autolink_tracks.return_value = int(
            spotify.ErrorType.OK
        )
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)

        playlist.set_autolink_tracks(True)

        lib_mock.sp_playlist_set_autolink_tracks.assert_called_with(sp_playlist, 1)

    def test_set_autolink_tracks_fails_if_error(self, lib_mock):
        lib_mock.sp_playlist_set_autolink_tracks.return_value = int(
            spotify.ErrorType.BAD_API_VERSION
        )
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)

        with self.assertRaises(spotify.Error):
            playlist.set_autolink_tracks(True)

    def test_description(self, lib_mock):
        lib_mock.sp_playlist_get_description.return_value = spotify.ffi.new(
            "char[]", b"Lorem ipsum"
        )
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)

        result = playlist.description

        lib_mock.sp_playlist_get_description.assert_called_with(sp_playlist)
        self.assertEqual(result, "Lorem ipsum")

    def test_description_is_none_if_unset(self, lib_mock):
        lib_mock.sp_playlist_get_description.return_value = spotify.ffi.NULL
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)

        result = playlist.description

        lib_mock.sp_playlist_get_description.assert_called_with(sp_playlist)
        self.assertIsNone(result)

    @mock.patch("spotify.Image", spec=spotify.Image)
    def test_image(self, image_mock, lib_mock):
        image_id = b"image-id"

        def func(sp_playlist, sp_image_id):
            buf = spotify.ffi.buffer(sp_image_id)
            buf[: len(image_id)] = image_id
            return 1

        lib_mock.sp_playlist_get_image.side_effect = func
        sp_image = spotify.ffi.cast("sp_image *", 43)
        lib_mock.sp_image_create.return_value = sp_image
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)
        image_mock.return_value = mock.sentinel.image
        callback = mock.Mock()

        result = playlist.image(callback=callback)

        self.assertIs(result, mock.sentinel.image)
        lib_mock.sp_playlist_get_image.assert_called_with(sp_playlist, mock.ANY)
        lib_mock.sp_image_create.assert_called_with(self.session._sp_session, mock.ANY)
        self.assertEqual(
            spotify.ffi.string(lib_mock.sp_image_create.call_args[0][1]),
            b"image-id",
        )

        # Since we *created* the sp_image, we already have a refcount of 1 and
        # shouldn't increase the refcount when wrapping this sp_image in an
        # Image object
        image_mock.assert_called_with(
            self.session, sp_image=sp_image, add_ref=False, callback=callback
        )

    def test_image_is_none_if_no_image(self, lib_mock):
        lib_mock.sp_playlist_get_image.return_value = 0
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)

        result = playlist.image()

        lib_mock.sp_playlist_get_image.assert_called_with(sp_playlist, mock.ANY)
        self.assertIsNone(result)

    def test_has_pending_changes(self, lib_mock):
        lib_mock.sp_playlist_has_pending_changes.return_value = 1
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)

        result = playlist.has_pending_changes

        lib_mock.sp_playlist_has_pending_changes.assert_called_with(sp_playlist)
        self.assertTrue(result)

    @mock.patch("spotify.track.lib", spec=spotify.lib)
    def test_add_tracks(self, track_lib_mock, lib_mock):
        lib_mock.sp_playlist_add_tracks.return_value = int(spotify.ErrorType.OK)
        sp_track1 = spotify.ffi.new("int * ")
        track1 = spotify.Track(self.session, sp_track=sp_track1)
        sp_track2 = spotify.ffi.new("int * ")
        track2 = spotify.Track(self.session, sp_track=sp_track2)
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)

        playlist.add_tracks([track1, track2], index=4)

        lib_mock.sp_playlist_add_tracks.assert_called_with(
            sp_playlist, [sp_track1, sp_track2], 2, 4, self.session._sp_session
        )

    @mock.patch("spotify.track.lib", spec=spotify.lib)
    def test_add_tracks_without_index(self, track_lib_mock, lib_mock):
        lib_mock.sp_playlist_add_tracks.return_value = int(spotify.ErrorType.OK)
        lib_mock.sp_playlist_num_tracks.return_value = 10
        sp_track1 = spotify.ffi.new("int * ")
        track1 = spotify.Track(self.session, sp_track=sp_track1)
        sp_track2 = spotify.ffi.new("int * ")
        track2 = spotify.Track(self.session, sp_track=sp_track2)
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)

        playlist.add_tracks([track1, track2])

        lib_mock.sp_playlist_add_tracks.assert_called_with(
            sp_playlist, [sp_track1, sp_track2], 2, 10, self.session._sp_session
        )

    @mock.patch("spotify.track.lib", spec=spotify.lib)
    def test_add_tracks_with_a_single_track(self, track_lib_mock, lib_mock):
        lib_mock.sp_playlist_add_tracks.return_value = int(spotify.ErrorType.OK)
        sp_track = spotify.ffi.new("int * ")
        track = spotify.Track(self.session, sp_track=sp_track)
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)

        playlist.add_tracks(track, index=7)

        lib_mock.sp_playlist_add_tracks.assert_called_with(
            sp_playlist, [sp_track], 1, 7, self.session._sp_session
        )

    def test_add_tracks_fails_if_error(self, lib_mock):
        lib_mock.sp_playlist_add_tracks.return_value = int(
            spotify.ErrorType.PERMISSION_DENIED
        )
        lib_mock.sp_playlist_num_tracks.return_value = 0
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)

        with self.assertRaises(spotify.Error):
            playlist.add_tracks([])

    @mock.patch("spotify.track.lib", spec=spotify.lib)
    def test_remove_tracks(self, track_lib_mock, lib_mock):
        lib_mock.sp_playlist_remove_tracks.return_value = int(spotify.ErrorType.OK)
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)
        index1 = 13
        index2 = 17

        playlist.remove_tracks([index1, index2])

        lib_mock.sp_playlist_remove_tracks.assert_called_with(sp_playlist, mock.ANY, 2)
        self.assertIn(index1, lib_mock.sp_playlist_remove_tracks.call_args[0][1])
        self.assertIn(index2, lib_mock.sp_playlist_remove_tracks.call_args[0][1])

    @mock.patch("spotify.track.lib", spec=spotify.lib)
    def test_remove_tracks_with_a_single_track(self, track_lib_mock, lib_mock):
        lib_mock.sp_playlist_remove_tracks.return_value = int(spotify.ErrorType.OK)
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)
        index = 17

        playlist.remove_tracks(index)

        lib_mock.sp_playlist_remove_tracks.assert_called_with(sp_playlist, [index], 1)

    @mock.patch("spotify.track.lib", spec=spotify.lib)
    def test_remove_tracks_with_duplicates(self, track_lib_mock, lib_mock):
        lib_mock.sp_playlist_remove_tracks.return_value = int(spotify.ErrorType.OK)
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)
        index = 17

        playlist.remove_tracks([index, index])

        lib_mock.sp_playlist_remove_tracks.assert_called_with(sp_playlist, [index], 1)

    @mock.patch("spotify.track.lib", spec=spotify.lib)
    def test_remove_tracks_fails_if_error(self, track_lib_mock, lib_mock):
        lib_mock.sp_playlist_remove_tracks.return_value = int(
            spotify.ErrorType.PERMISSION_DENIED
        )
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)
        index = 17

        with self.assertRaises(spotify.Error):
            playlist.remove_tracks(index)

    @mock.patch("spotify.track.lib", spec=spotify.lib)
    def test_reorder_tracks(self, track_lib_mock, lib_mock):
        lib_mock.sp_playlist_reorder_tracks.return_value = int(spotify.ErrorType.OK)
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)
        position1 = 13
        position2 = 17

        playlist.reorder_tracks([position1, position2], 17)

        lib_mock.sp_playlist_reorder_tracks.assert_called_with(
            sp_playlist, mock.ANY, 2, 17
        )
        self.assertIn(position1, lib_mock.sp_playlist_reorder_tracks.call_args[0][1])
        self.assertIn(position2, lib_mock.sp_playlist_reorder_tracks.call_args[0][1])

    @mock.patch("spotify.track.lib", spec=spotify.lib)
    def test_reorder_tracks_with_a_single_track(self, track_lib_mock, lib_mock):
        lib_mock.sp_playlist_reorder_tracks.return_value = int(spotify.ErrorType.OK)
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)
        position = 13

        playlist.reorder_tracks(position, 17)

        lib_mock.sp_playlist_reorder_tracks.assert_called_with(
            sp_playlist, [position], 1, 17
        )

    @mock.patch("spotify.track.lib", spec=spotify.lib)
    def test_reorder_tracks_with_duplicates(self, track_lib_mock, lib_mock):
        lib_mock.sp_playlist_reorder_tracks.return_value = int(spotify.ErrorType.OK)
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)
        position = 13

        playlist.reorder_tracks([position, position], 17)

        lib_mock.sp_playlist_reorder_tracks.assert_called_with(
            sp_playlist, [position], 1, 17
        )

    @mock.patch("spotify.track.lib", spec=spotify.lib)
    def test_reorder_tracks_fails_if_error(self, track_lib_mock, lib_mock):
        lib_mock.sp_playlist_reorder_tracks.return_value = int(
            spotify.ErrorType.PERMISSION_DENIED
        )
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)
        position = 13

        with self.assertRaises(spotify.Error):
            playlist.reorder_tracks(position, 17)

    def test_num_subscribers(self, lib_mock):
        lib_mock.sp_playlist_num_subscribers.return_value = 7
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)

        result = playlist.num_subscribers

        lib_mock.sp_playlist_num_subscribers.assert_called_with(sp_playlist)
        self.assertEqual(result, 7)

    def test_subscribers(self, lib_mock):
        sp_subscribers = spotify.ffi.new("sp_subscribers *")
        sp_subscribers.count = 1
        user_alice = spotify.ffi.new("char[]", b"alice")
        sp_subscribers.subscribers = [user_alice]
        lib_mock.sp_playlist_subscribers.return_value = sp_subscribers
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)

        result = playlist.subscribers

        lib_mock.sp_playlist_subscribers.assert_called_with(sp_playlist)
        tests.gc_collect()
        lib_mock.sp_playlist_subscribers_free.assert_called_with(sp_subscribers)
        self.assertEqual(result, ["alice"])

    def test_update_subscribers(self, lib_mock):
        lib_mock.sp_playlist_update_subscribers.return_value = int(spotify.ErrorType.OK)
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)

        playlist.update_subscribers()

        lib_mock.sp_playlist_update_subscribers.assert_called_with(
            self.session._sp_session, sp_playlist
        )

    def test_update_subscribers_fails_if_error(self, lib_mock):
        lib_mock.sp_playlist_update_subscribers.return_value = int(
            spotify.ErrorType.BAD_API_VERSION
        )
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)

        with self.assertRaises(spotify.Error):
            playlist.update_subscribers()

    def test_is_in_ram(self, lib_mock):
        lib_mock.sp_playlist_is_in_ram.return_value = 1
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)

        result = playlist.is_in_ram

        lib_mock.sp_playlist_is_in_ram.assert_called_with(
            self.session._sp_session, sp_playlist
        )
        self.assertTrue(result)

    def test_set_in_ram(self, lib_mock):
        lib_mock.sp_playlist_set_in_ram.return_value = int(spotify.ErrorType.OK)
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)

        playlist.set_in_ram(False)

        lib_mock.sp_playlist_set_in_ram.assert_called_with(
            self.session._sp_session, sp_playlist, 0
        )

    def test_set_in_ram_fails_if_error(self, lib_mock):
        lib_mock.sp_playlist_set_in_ram.return_value = int(
            spotify.ErrorType.BAD_API_VERSION
        )
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)

        with self.assertRaises(spotify.Error):
            playlist.set_in_ram(False)

    def test_set_offline_mode(self, lib_mock):
        lib_mock.sp_playlist_set_offline_mode.return_value = int(spotify.ErrorType.OK)
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)

        playlist.set_offline_mode(False)

        lib_mock.sp_playlist_set_offline_mode.assert_called_with(
            self.session._sp_session, sp_playlist, 0
        )

    def test_set_offline_mode_fails_if_error(self, lib_mock):
        lib_mock.sp_playlist_set_offline_mode.return_value = int(
            spotify.ErrorType.BAD_API_VERSION
        )
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)

        with self.assertRaises(spotify.Error):
            playlist.set_offline_mode(False)

    def test_offline_status(self, lib_mock):
        lib_mock.sp_playlist_get_offline_status.return_value = 2
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)

        result = playlist.offline_status

        lib_mock.sp_playlist_get_offline_status.assert_called_with(
            self.session._sp_session, sp_playlist
        )
        self.assertIs(result, spotify.PlaylistOfflineStatus.DOWNLOADING)

    def test_offline_download_completed(self, lib_mock):
        lib_mock.sp_playlist_get_offline_status.return_value = 2
        lib_mock.sp_playlist_get_offline_download_completed.return_value = 73
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)

        result = playlist.offline_download_completed

        lib_mock.sp_playlist_get_offline_download_completed.assert_called_with(
            self.session._sp_session, sp_playlist
        )
        self.assertEqual(result, 73)

    def test_offline_download_completed_when_not_downloading(self, lib_mock):
        lib_mock.sp_playlist_get_offline_status.return_value = 0
        lib_mock.sp_playlist_get_offline_download_completed.return_value = 0
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)

        result = playlist.offline_download_completed

        self.assertEqual(
            lib_mock.sp_playlist_get_offline_download_completed.call_count, 0
        )
        self.assertIsNone(result)

    @mock.patch("spotify.Link", spec=spotify.Link)
    def test_link_creates_link_to_playlist(self, link_mock, lib_mock):
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)
        sp_link = spotify.ffi.cast("sp_link *", 43)
        lib_mock.sp_link_create_from_playlist.return_value = sp_link
        link_mock.return_value = mock.sentinel.link

        result = playlist.link

        link_mock.assert_called_once_with(self.session, sp_link=sp_link, add_ref=False)
        self.assertEqual(result, mock.sentinel.link)

    @mock.patch("spotify.Link", spec=spotify.Link)
    def test_link_fails_if_playlist_not_loaded(self, lik_mock, lib_mock):
        lib_mock.sp_playlist_is_loaded.return_value = 0
        lib_mock.sp_link_create_from_playlist.return_value = spotify.ffi.NULL
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)

        with self.assertRaises(spotify.Error):
            playlist.link

        # Condition is checked before link creation is tried
        self.assertEqual(lib_mock.sp_link_create_from_playlist.call_count, 0)

    @mock.patch("spotify.Link", spec=spotify.Link)
    def test_link_may_fail_if_playlist_has_not_been_in_ram(self, link_mock, lib_mock):
        lib_mock.sp_playlist_is_loaded.return_value = 1
        lib_mock.sp_link_create_from_playlist.return_value = spotify.ffi.NULL
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)

        with self.assertRaises(spotify.Error):
            playlist.link

        # Condition is checked only if link creation returns NULL
        lib_mock.sp_link_create_from_playlist.assert_called_with(sp_playlist)
        lib_mock.sp_playlist_is_in_ram.assert_called_with(
            self.session._sp_session, sp_playlist
        )

    def test_first_on_call_adds_ref_to_obj_on_session(self, lib_mock):
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)

        playlist.on(spotify.PlaylistEvent.TRACKS_ADDED, lambda *args: None)

        self.assertIn(playlist, self.session._emitters)

    def test_last_off_call_removes_ref_to_obj_from_session(self, lib_mock):
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)

        playlist.on(spotify.PlaylistEvent.TRACKS_ADDED, lambda *args: None)
        playlist.off(spotify.PlaylistEvent.TRACKS_ADDED)

        self.assertNotIn(playlist, self.session._emitters)

    def test_other_off_calls_keeps_ref_to_obj_on_session(self, lib_mock):
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)

        playlist.on(spotify.PlaylistEvent.TRACKS_ADDED, lambda *args: None)
        playlist.on(spotify.PlaylistEvent.TRACKS_MOVED, lambda *args: None)
        playlist.off(spotify.PlaylistEvent.TRACKS_ADDED)

        self.assertIn(playlist, self.session._emitters)

        playlist.off(spotify.PlaylistEvent.TRACKS_MOVED)

        self.assertNotIn(playlist, self.session._emitters)


@mock.patch("spotify.playlist.lib", spec=spotify.lib)
class PlaylistCallbacksTest(unittest.TestCase):
    def setUp(self):
        self.session = tests.create_session_mock()
        spotify._session_instance = self.session

    def tearDown(self):
        spotify._session_instance = None

    @mock.patch("spotify.track.lib", spec=spotify.lib)
    def test_tracks_added_callback(self, track_lib_mock, lib_mock):
        callback = mock.Mock()
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist._cached(self.session, sp_playlist=sp_playlist)
        playlist.on(spotify.PlaylistEvent.TRACKS_ADDED, callback)
        sp_tracks = [
            spotify.ffi.cast("sp_track *", 43),
            spotify.ffi.cast("sp_track *", 44),
            spotify.ffi.cast("sp_track *", 45),
        ]
        index = 7

        _PlaylistCallbacks.tracks_added(
            sp_playlist, sp_tracks, len(sp_tracks), index, spotify.ffi.NULL
        )

        callback.assert_called_once_with(playlist, mock.ANY, index)
        tracks = callback.call_args[0][1]
        self.assertEqual(len(tracks), len(sp_tracks))
        self.assertIsInstance(tracks[0], spotify.Track)
        self.assertEqual(tracks[0]._sp_track, sp_tracks[0])
        track_lib_mock.sp_track_add_ref.assert_has_calls(
            [
                mock.call(sp_tracks[0]),
                mock.call(sp_tracks[1]),
                mock.call(sp_tracks[2]),
            ]
        )

    def test_tracks_removed_callback(self, lib_mock):
        callback = mock.Mock()
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist._cached(self.session, sp_playlist=sp_playlist)
        playlist.on(spotify.PlaylistEvent.TRACKS_REMOVED, callback)
        track_numbers = [43, 44, 45]

        _PlaylistCallbacks.tracks_removed(
            sp_playlist, track_numbers, len(track_numbers), spotify.ffi.NULL
        )

        callback.assert_called_once_with(playlist, mock.ANY)
        tracks = callback.call_args[0][1]
        self.assertEqual(len(tracks), len(track_numbers))
        self.assertEqual(tracks[0], 43)

    def test_tracks_moved_callback(self, lib_mock):
        callback = mock.Mock()
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist._cached(self.session, sp_playlist=sp_playlist)
        playlist.on(spotify.PlaylistEvent.TRACKS_MOVED, callback)
        track_numbers = [43, 44, 45]
        index = 7

        _PlaylistCallbacks.tracks_moved(
            sp_playlist,
            track_numbers,
            len(track_numbers),
            index,
            spotify.ffi.NULL,
        )

        callback.assert_called_once_with(playlist, mock.ANY, index)
        tracks = callback.call_args[0][1]
        self.assertEqual(len(tracks), len(track_numbers))
        self.assertEqual(tracks[0], 43)

    def test_playlist_renamed_callback(self, lib_mock):
        callback = mock.Mock()
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist._cached(self.session, sp_playlist=sp_playlist)
        playlist.on(spotify.PlaylistEvent.PLAYLIST_RENAMED, callback)

        _PlaylistCallbacks.playlist_renamed(sp_playlist, spotify.ffi.NULL)

        callback.assert_called_once_with(playlist)

    def test_playlist_state_changed_callback(self, lib_mock):
        callback = mock.Mock()
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist._cached(self.session, sp_playlist=sp_playlist)
        playlist.on(spotify.PlaylistEvent.PLAYLIST_STATE_CHANGED, callback)

        _PlaylistCallbacks.playlist_state_changed(sp_playlist, spotify.ffi.NULL)

        callback.assert_called_once_with(playlist)

    def test_playlist_update_in_progress_callback(self, lib_mock):
        callback = mock.Mock()
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist._cached(self.session, sp_playlist=sp_playlist)
        playlist.on(spotify.PlaylistEvent.PLAYLIST_UPDATE_IN_PROGRESS, callback)
        done = True

        _PlaylistCallbacks.playlist_update_in_progress(
            sp_playlist, int(done), spotify.ffi.NULL
        )

        callback.assert_called_once_with(playlist, done)

    def test_playlist_metadata_updated_callback(self, lib_mock):
        callback = mock.Mock()
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist._cached(self.session, sp_playlist=sp_playlist)
        playlist.on(spotify.PlaylistEvent.PLAYLIST_METADATA_UPDATED, callback)

        _PlaylistCallbacks.playlist_metadata_updated(sp_playlist, spotify.ffi.NULL)

        callback.assert_called_once_with(playlist)

    @mock.patch("spotify.user.lib", spec=spotify.lib)
    def test_track_created_changed_callback(self, user_lib_mock, lib_mock):
        callback = mock.Mock()
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist._cached(self.session, sp_playlist=sp_playlist)
        playlist.on(spotify.PlaylistEvent.TRACK_CREATED_CHANGED, callback)
        index = 7
        sp_user = spotify.ffi.cast("sp_user *", 43)
        time = 123456789

        _PlaylistCallbacks.track_created_changed(
            sp_playlist, index, sp_user, time, spotify.ffi.NULL
        )

        callback.assert_called_once_with(playlist, index, mock.ANY, time)
        user = callback.call_args[0][2]
        self.assertIsInstance(user, spotify.User)
        self.assertEqual(user._sp_user, sp_user)
        user_lib_mock.sp_user_add_ref.assert_called_with(sp_user)

    def test_track_seen_changed_callback(self, lib_mock):
        callback = mock.Mock()
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist._cached(self.session, sp_playlist=sp_playlist)
        playlist.on(spotify.PlaylistEvent.TRACK_SEEN_CHANGED, callback)
        index = 7
        seen = True

        _PlaylistCallbacks.track_seen_changed(
            sp_playlist, index, int(seen), spotify.ffi.NULL
        )

        callback.assert_called_once_with(playlist, index, seen)

    def test_description_changed_callback(self, lib_mock):
        callback = mock.Mock()
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist._cached(self.session, sp_playlist=sp_playlist)
        playlist.on(spotify.PlaylistEvent.DESCRIPTION_CHANGED, callback)
        description = "foo bar æøå"
        desc = spotify.ffi.new("char[]", description.encode("utf-8"))

        _PlaylistCallbacks.description_changed(sp_playlist, desc, spotify.ffi.NULL)

        callback.assert_called_once_with(playlist, description)

    @mock.patch("spotify.image.lib", spec=spotify.lib)
    def test_image_changed_callback(self, image_lib_mock, lib_mock):
        callback = mock.Mock()
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist._cached(self.session, sp_playlist=sp_playlist)
        playlist.on(spotify.PlaylistEvent.IMAGE_CHANGED, callback)
        image_id = spotify.ffi.new("char[]", b"image-id")
        sp_image = spotify.ffi.cast("sp_image *", 43)
        lib_mock.sp_image_create.return_value = sp_image
        image_lib_mock.sp_image_add_load_callback.return_value = int(
            spotify.ErrorType.OK
        )

        _PlaylistCallbacks.image_changed(sp_playlist, image_id, spotify.ffi.NULL)

        callback.assert_called_once_with(playlist, mock.ANY)
        image = callback.call_args[0][1]
        self.assertIsInstance(image, spotify.Image)
        self.assertEqual(image._sp_image, sp_image)
        lib_mock.sp_image_create.assert_called_once_with(
            self.session._sp_session, image_id
        )
        self.assertEqual(image_lib_mock.sp_image_add_ref.call_count, 0)

    def test_track_message_changed_callback(self, lib_mock):
        callback = mock.Mock()
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist._cached(self.session, sp_playlist=sp_playlist)
        playlist.on(spotify.PlaylistEvent.TRACK_MESSAGE_CHANGED, callback)
        index = 7
        message = "foo bar æøå"
        msg = spotify.ffi.new("char[]", message.encode("utf-8"))

        _PlaylistCallbacks.track_message_changed(
            sp_playlist, index, msg, spotify.ffi.NULL
        )

        callback.assert_called_once_with(playlist, index, message)

    def test_subscribers_changed_callback(self, lib_mock):
        callback = mock.Mock()
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        playlist = spotify.Playlist._cached(self.session, sp_playlist=sp_playlist)
        playlist.on(spotify.PlaylistEvent.SUBSCRIBERS_CHANGED, callback)

        _PlaylistCallbacks.subscribers_changed(sp_playlist, spotify.ffi.NULL)

        callback.assert_called_once_with(playlist)


class PlaylistOfflineStatusTest(unittest.TestCase):
    def test_has_constants(self):
        self.assertEqual(spotify.PlaylistOfflineStatus.NO, 0)
        self.assertEqual(spotify.PlaylistOfflineStatus.DOWNLOADING, 2)
