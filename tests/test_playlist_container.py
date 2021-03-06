from __future__ import unicode_literals

import os
import unittest

import spotify
import tests
from spotify import compat
from spotify.playlist_container import _PlaylistContainerCallbacks
from tests import mock


@mock.patch("spotify.playlist_container.lib", spec=spotify.lib)
class PlaylistContainerTest(unittest.TestCase):
    def setUp(self):
        self.session = tests.create_session_mock()
        spotify._session_instance = self.session

    def tearDown(self):
        spotify._session_instance = None

    def test_life_cycle(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)

        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer
        )

        lib_mock.sp_playlistcontainer_add_ref.assert_called_with(sp_playlistcontainer)

        # Callbacks are only added when someone registers a Python event
        # handler on the container:
        lib_mock.sp_playlistcontainer_add_callbacks.assert_not_called()
        playlist_container.on(
            spotify.PlaylistContainerEvent.PLAYLIST_ADDED, lambda *args: None
        )
        lib_mock.sp_playlistcontainer_add_callbacks.assert_called_with(
            sp_playlistcontainer, mock.ANY, mock.ANY
        )

        playlist_container = None  # noqa
        tests.gc_collect()

        # Callbacks are removed when the container is GC-ed:
        lib_mock.sp_playlistcontainer_remove_callbacks.assert_called_with(
            sp_playlistcontainer, mock.ANY, mock.ANY
        )

        # FIXME Won't be called because lib_mock has references to the
        # sp_playlistcontainer object, and it thus won't be GC-ed.
        # lib_mock.sp_playlistcontainer_release.assert_called_with(
        #     sp_playlistcontainer)

    def test_cached_container(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)

        result1 = spotify.PlaylistContainer._cached(self.session, sp_playlistcontainer)
        result2 = spotify.PlaylistContainer._cached(self.session, sp_playlistcontainer)

        self.assertIsInstance(result1, spotify.PlaylistContainer)
        self.assertIs(result1, result2)

    @mock.patch("spotify.User", spec=spotify.User)
    @mock.patch("spotify.Link", spec=spotify.Link)
    def test_repr(self, link_mock, user_mock, lib_mock):
        link_instance_mock = link_mock.return_value
        link_instance_mock.uri = "foo"
        user_instance_mock = user_mock.return_value
        user_instance_mock.link = link_instance_mock
        lib_mock.sp_playlistcontainer_num_playlists.return_value = 0
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )

        result = repr(playlist_container)

        self.assertEqual(result, "PlaylistContainer([])")

    def test_eq(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container1 = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )
        playlist_container2 = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )

        self.assertTrue(playlist_container1 == playlist_container2)
        self.assertFalse(playlist_container1 == "foo")

    def test_ne(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container1 = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )
        playlist_container2 = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )

        self.assertFalse(playlist_container1 != playlist_container2)

    def test_hash(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container1 = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )
        playlist_container2 = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )

        self.assertEqual(hash(playlist_container1), hash(playlist_container2))

    def test_is_loaded(self, lib_mock):
        lib_mock.sp_playlistcontainer_is_loaded.return_value = 1
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )

        result = playlist_container.is_loaded

        lib_mock.sp_playlistcontainer_is_loaded.assert_called_once_with(
            sp_playlistcontainer
        )
        self.assertTrue(result)

    @mock.patch("spotify.utils.load")
    def test_load(self, load_mock, lib_mock):
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )

        playlist_container.load(10)

        load_mock.assert_called_with(self.session, playlist_container, timeout=10)

    def test_len(self, lib_mock):
        lib_mock.sp_playlistcontainer_num_playlists.return_value = 8
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )

        result = len(playlist_container)

        lib_mock.sp_playlistcontainer_num_playlists.assert_called_with(
            sp_playlistcontainer
        )
        self.assertEqual(result, 8)

    def test_len_if_undefined(self, lib_mock):
        lib_mock.sp_playlistcontainer_num_playlists.return_value = -1
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )

        result = len(playlist_container)

        lib_mock.sp_playlistcontainer_num_playlists.assert_called_with(
            sp_playlistcontainer
        )
        self.assertEqual(result, 0)

    @mock.patch("spotify.playlist.lib", lib=spotify.lib)
    def test_getitem(self, playlist_lib_mock, lib_mock):
        lib_mock.sp_playlistcontainer_num_playlists.return_value = 1
        sp_playlist = spotify.ffi.cast("sp_playlist *", 43)
        lib_mock.sp_playlistcontainer_playlist_type.return_value = int(
            spotify.PlaylistType.PLAYLIST
        )
        lib_mock.sp_playlistcontainer_playlist.return_value = sp_playlist
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )

        result = playlist_container[0]

        lib_mock.sp_playlistcontainer_playlist.assert_called_with(
            sp_playlistcontainer, 0
        )
        playlist_lib_mock.sp_playlist_add_ref.assert_called_with(sp_playlist)
        self.assertIsInstance(result, spotify.Playlist)
        self.assertEqual(result._sp_playlist, sp_playlist)

    @mock.patch("spotify.playlist.lib", lib=spotify.lib)
    def test_getitem_with_negative_index(self, playlist_lib_mock, lib_mock):
        lib_mock.sp_playlistcontainer_num_playlists.return_value = 1
        sp_playlist = spotify.ffi.cast("sp_playlist *", 43)
        lib_mock.sp_playlistcontainer_playlist_type.return_value = int(
            spotify.PlaylistType.PLAYLIST
        )
        lib_mock.sp_playlistcontainer_playlist.return_value = sp_playlist
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )

        result = playlist_container[-1]

        lib_mock.sp_playlistcontainer_playlist.assert_called_with(
            sp_playlistcontainer, 0
        )
        playlist_lib_mock.sp_playlist_add_ref.assert_called_with(sp_playlist)
        self.assertIsInstance(result, spotify.Playlist)
        self.assertEqual(result._sp_playlist, sp_playlist)

    @mock.patch("spotify.playlist.lib", lib=spotify.lib)
    def test_getitem_with_slice(self, playlist_lib_mock, lib_mock):
        lib_mock.sp_playlistcontainer_num_playlists.return_value = 3
        lib_mock.sp_playlistcontainer_playlist_type.side_effect = [
            int(spotify.PlaylistType.PLAYLIST),
            int(spotify.PlaylistType.PLAYLIST),
            int(spotify.PlaylistType.PLAYLIST),
        ]
        sp_playlist1 = spotify.ffi.cast("sp_playlist *", 43)
        sp_playlist2 = spotify.ffi.cast("sp_playlist *", 44)
        sp_playlist3 = spotify.ffi.cast("sp_playlist *", 45)
        lib_mock.sp_playlistcontainer_playlist.side_effect = [
            sp_playlist1,
            sp_playlist2,
            sp_playlist3,
        ]
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )

        result = playlist_container[0:2]

        # Entire collection of length 3 is created as a list
        self.assertEqual(lib_mock.sp_playlistcontainer_playlist.call_count, 3)
        self.assertEqual(playlist_lib_mock.sp_playlist_add_ref.call_count, 3)

        # Only a subslice of length 2 is returned
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]._sp_playlist, sp_playlist1)
        self.assertEqual(result[1]._sp_playlist, sp_playlist2)

    @mock.patch("spotify.playlist.lib", lib=spotify.lib)
    def test_getitem_with_folder(self, playlist_lib_mock, lib_mock):
        folder_name = "foobar"

        lib_mock.sp_playlistcontainer_num_playlists.return_value = 3
        lib_mock.sp_playlistcontainer_playlist_type.side_effect = [
            int(spotify.PlaylistType.START_FOLDER),
            int(spotify.PlaylistType.PLAYLIST),
            int(spotify.PlaylistType.END_FOLDER),
        ]
        sp_playlist = spotify.ffi.cast("sp_playlist *", 43)
        lib_mock.sp_playlistcontainer_playlist.return_value = sp_playlist
        lib_mock.sp_playlistcontainer_playlist_folder_id.side_effect = [
            1001,
            1002,
        ]
        func = tests.buffer_writer(folder_name)
        lib_mock.sp_playlistcontainer_playlist_folder_name.side_effect = func
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )

        result = playlist_container[0]

        lib_mock.sp_playlistcontainer_playlist_type.assert_called_with(
            sp_playlistcontainer, 0
        )
        lib_mock.sp_playlistcontainer_playlist_folder_id.assert_called_with(
            sp_playlistcontainer, 0
        )
        self.assertIsInstance(result, spotify.PlaylistFolder)
        self.assertEqual(result.id, 1001)
        self.assertEqual(result.name, "foobar")
        self.assertEqual(result.type, spotify.PlaylistType.START_FOLDER)

        result = playlist_container[1]

        lib_mock.sp_playlistcontainer_playlist_type.assert_called_with(
            sp_playlistcontainer, 1
        )
        lib_mock.sp_playlistcontainer_playlist.assert_called_with(
            sp_playlistcontainer, 1
        )
        playlist_lib_mock.sp_playlist_add_ref.assert_called_with(sp_playlist)
        self.assertIsInstance(result, spotify.Playlist)
        self.assertEqual(result._sp_playlist, sp_playlist)

        result = playlist_container[2]

        lib_mock.sp_playlistcontainer_playlist_type.assert_called_with(
            sp_playlistcontainer, 2
        )
        lib_mock.sp_playlistcontainer_playlist_folder_id.assert_called_with(
            sp_playlistcontainer, 2
        )
        self.assertIsInstance(result, spotify.PlaylistFolder)
        self.assertEqual(result.id, 1002)
        # self.assertEqual(result.name, '')  # Needs better mock impl
        self.assertEqual(result.type, spotify.PlaylistType.END_FOLDER)

    def test_getitem_with_placeholder(self, lib_mock):
        lib_mock.sp_playlistcontainer_num_playlists.return_value = 1
        lib_mock.sp_playlistcontainer_playlist_type.return_value = int(
            spotify.PlaylistType.PLACEHOLDER
        )
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )

        result = playlist_container[0]

        self.assertEqual(lib_mock.sp_playlistcontainer_playlist.call_count, 0)
        self.assertIsInstance(result, spotify.PlaylistPlaceholder)

    def test_getitem_raises_index_error_on_too_low_index(self, lib_mock):
        lib_mock.sp_playlistcontainer_num_playlists.return_value = 1
        sp_playlist = spotify.ffi.cast("sp_playlist *", 43)
        lib_mock.sp_playlistcontainer_playlist.return_value = sp_playlist
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )

        with self.assertRaises(IndexError):
            playlist_container[-3]

    def test_getitem_raises_index_error_on_too_high_index(self, lib_mock):
        lib_mock.sp_playlistcontainer_num_playlists.return_value = 1
        sp_playlist = spotify.ffi.cast("sp_playlist *", 43)
        lib_mock.sp_playlistcontainer_playlist.return_value = sp_playlist
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )

        with self.assertRaises(IndexError):
            playlist_container[1]

    def test_getitem_raises_type_error_on_non_integral_index(self, lib_mock):
        lib_mock.sp_playlistcontainer_num_playlists.return_value = 1
        sp_playlist = spotify.ffi.cast("sp_playlist *", 43)
        lib_mock.sp_playlistcontainer_playlist.return_value = sp_playlist
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )

        with self.assertRaises(TypeError):
            playlist_container["abc"]

    def test_setitem_with_playlist_name(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )
        playlist_container.__len__ = mock.Mock(return_value=5)
        playlist_container.remove_playlist = mock.Mock()
        playlist_container.add_new_playlist = mock.Mock()

        playlist_container[0] = "New playlist"

        playlist_container.add_new_playlist.assert_called_with("New playlist", index=0)
        playlist_container.remove_playlist.assert_called_with(1)

    @mock.patch("spotify.playlist.lib", lib=spotify.lib)
    def test_setitem_with_existing_playlist(self, playlist_lib_mock, lib_mock):
        sp_playlist = spotify.ffi.cast("sp_playlist *", 43)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )
        playlist_container.__len__ = mock.Mock(return_value=5)
        playlist_container.remove_playlist = mock.Mock()
        playlist_container.add_playlist = mock.Mock()

        playlist_container[0] = playlist

        playlist_container.add_playlist.assert_called_with(playlist, index=0)
        playlist_container.remove_playlist.assert_called_with(1)

    @mock.patch("spotify.playlist.lib", lib=spotify.lib)
    def test_setitem_with_slice(self, playlist_lib_mock, lib_mock):
        sp_playlist = spotify.ffi.cast("sp_playlist *", 43)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )
        playlist_container.__len__ = mock.Mock(return_value=5)
        playlist_container.remove_playlist = mock.Mock()
        playlist_container.add_new_playlist = mock.Mock()
        playlist_container.add_playlist = mock.Mock()

        playlist_container[0:2] = ["New playlist", playlist]

        playlist_container.add_new_playlist.assert_called_with("New playlist", index=0)
        playlist_container.add_playlist.assert_called_with(playlist, index=1)
        playlist_container.remove_playlist.assert_has_calls(
            [mock.call(3), mock.call(2)], any_order=False
        )

    @mock.patch("spotify.playlist.lib", lib=spotify.lib)
    def test_setittem_with_slice_and_noniterable_value_fails(
        self, playlist_lib_mock, lib_mock
    ):

        sp_playlist = spotify.ffi.cast("sp_playlist *", 43)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )
        playlist_container.__len__ = mock.Mock(return_value=3)
        playlist_container.remove_playlist = mock.Mock()
        playlist_container.add_new_playlist = mock.Mock()

        with self.assertRaises(TypeError):
            playlist_container[0:2] = playlist

    def test_setitem_raises_error_on_unknown_playlist_type(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )
        playlist_container.__len__ = mock.Mock(return_value=1)
        playlist_container.remove_playlist = mock.Mock()
        playlist_container.add_new_playlist = mock.Mock(side_effect=ValueError)

        with self.assertRaises(ValueError):
            playlist_container[0] = False

        playlist_container.add_new_playlist.assert_called_with(False, index=0)
        self.assertEqual(playlist_container.remove_playlist.call_count, 0)

    def test_setitem_raises_index_error_on_negative_index(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )
        playlist_container.__len__ = mock.Mock(return_value=1)

        with self.assertRaises(IndexError):
            playlist_container[-1] = None

    def test_setitem_raises_index_error_on_too_high_index(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )
        playlist_container.__len__ = mock.Mock(return_value=1)

        with self.assertRaises(IndexError):
            playlist_container[1] = None

    def test_setitem_raises_type_error_on_non_integral_index(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )
        playlist_container.__len__ = mock.Mock(return_value=1)

        with self.assertRaises(TypeError):
            playlist_container["abc"] = None

    def test_delitem(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )
        playlist_container.__len__ = mock.Mock(return_value=1)
        playlist_container.remove_playlist = mock.Mock()

        del playlist_container[0]

        playlist_container.remove_playlist.assert_called_with(0)

    def test_delitem_with_slice(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )
        playlist_container.__len__ = mock.Mock(return_value=3)
        playlist_container.remove_playlist = mock.Mock()

        del playlist_container[0:2]

        # Delete items in reverse order, so the indexes doesn't change
        playlist_container.remove_playlist.assert_has_calls(
            [mock.call(1), mock.call(0)], any_order=False
        )

    def test_delitem_raises_index_error_on_negative_index(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )
        playlist_container.__len__ = mock.Mock(return_value=1)

        with self.assertRaises(IndexError):
            del playlist_container[-1]

    def test_delitem_raises_index_error_on_too_high_index(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )
        playlist_container.__len__ = mock.Mock(return_value=1)

        with self.assertRaises(IndexError):
            del playlist_container[1]

    def test_delitem_raises_type_error_on_non_integral_index(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )
        playlist_container.__len__ = mock.Mock(return_value=1)

        with self.assertRaises(TypeError):
            del playlist_container["abc"]

    def test_insert_with_playlist_name(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )
        playlist_container.__len__ = mock.Mock(return_value=5)
        playlist_container.remove_playlist = mock.Mock()
        playlist_container.add_new_playlist = mock.Mock()

        playlist_container.insert(3, "New playlist")

        playlist_container.add_new_playlist.assert_called_with("New playlist", index=3)

    @mock.patch("spotify.playlist.lib", spec=spotify.lib)
    def test_insert_with_existing_playlist(self, playlist_lib_mock, lib_mock):
        sp_playlist = spotify.ffi.cast("sp_playlist *", 43)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )
        playlist_container.__len__ = mock.Mock(return_value=5)
        playlist_container.remove_playlist = mock.Mock()
        playlist_container.add_playlist = mock.Mock()

        playlist_container.insert(3, playlist)

        playlist_container.add_playlist.assert_called_with(playlist, index=3)

    def test_is_a_sequence(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )

        self.assertIsInstance(playlist_container, compat.Sequence)

    def test_is_a_mutable_sequence(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )

        self.assertIsInstance(playlist_container, compat.MutableSequence)

    @mock.patch("spotify.playlist.lib", lib=spotify.lib)
    def test_add_new_playlist_to_end_of_container(self, playlist_lib_mock, lib_mock):

        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )
        sp_playlist = spotify.ffi.cast("sp_playlist *", 43)
        lib_mock.sp_playlistcontainer_add_new_playlist.return_value = sp_playlist

        result = playlist_container.add_new_playlist("foo bar")

        lib_mock.sp_playlistcontainer_add_new_playlist.assert_called_with(
            sp_playlistcontainer, mock.ANY
        )
        self.assertEqual(
            spotify.ffi.string(
                lib_mock.sp_playlistcontainer_add_new_playlist.call_args[0][1]
            ),
            b"foo bar",
        )
        self.assertIsInstance(result, spotify.Playlist)
        self.assertEqual(result._sp_playlist, sp_playlist)
        playlist_lib_mock.sp_playlist_add_ref.assert_called_with(sp_playlist)
        self.assertEqual(lib_mock.sp_playlistcontainer_move_playlist.call_count, 0)

    @mock.patch("spotify.playlist.lib", lib=spotify.lib)
    def test_add_new_playlist_at_given_index(self, playlist_lib_mock, lib_mock):

        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )
        sp_playlist = spotify.ffi.cast("sp_playlist *", 43)
        lib_mock.sp_playlistcontainer_add_new_playlist.return_value = sp_playlist
        lib_mock.sp_playlistcontainer_num_playlists.return_value = 100
        lib_mock.sp_playlistcontainer_move_playlist.return_value = int(
            spotify.ErrorType.OK
        )

        result = playlist_container.add_new_playlist("foo bar", index=7)

        lib_mock.sp_playlistcontainer_add_new_playlist.assert_called_with(
            sp_playlistcontainer, mock.ANY
        )
        self.assertEqual(
            spotify.ffi.string(
                lib_mock.sp_playlistcontainer_add_new_playlist.call_args[0][1]
            ),
            b"foo bar",
        )
        self.assertIsInstance(result, spotify.Playlist)
        self.assertEqual(result._sp_playlist, sp_playlist)
        playlist_lib_mock.sp_playlist_add_ref.assert_called_with(sp_playlist)
        lib_mock.sp_playlistcontainer_move_playlist.assert_called_with(
            sp_playlistcontainer, 99, 7, 0
        )

    def test_add_new_playlist_fails_if_name_is_space_only(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )

        with self.assertRaises(ValueError):
            playlist_container.add_new_playlist("   ")

        # Spotify seems to accept e.g. tab-only names, but it doesn't make any
        # sense to allow it, so we disallow names with all combinations of just
        # whitespace.
        with self.assertRaises(ValueError):
            playlist_container.add_new_playlist("\t\t")
        with self.assertRaises(ValueError):
            playlist_container.add_new_playlist("\r\r")
        with self.assertRaises(ValueError):
            playlist_container.add_new_playlist("\n\n")
        with self.assertRaises(ValueError):
            playlist_container.add_new_playlist(" \t\r\n")

    def test_add_new_playlist_fails_if_name_is_too_long(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )

        with self.assertRaises(ValueError):
            playlist_container.add_new_playlist("x" * 300)

    def test_add_new_playlist_fails_if_operation_fails(self, lib_mock):
        lib_mock.sp_playlistcontainer_add_new_playlist.return_value = spotify.ffi.NULL
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )

        with self.assertRaises(spotify.Error):
            playlist_container.add_new_playlist("foo bar")

    @mock.patch("spotify.link.lib", lib=spotify.lib)
    @mock.patch("spotify.playlist.lib", lib=spotify.lib)
    def test_add_playlist_from_link(self, playlist_lib_mock, link_lib_mock, lib_mock):
        sp_link = spotify.ffi.cast("sp_link *", 43)
        link = spotify.Link(self.session, sp_link=sp_link, add_ref=False)
        sp_playlist = spotify.ffi.cast("sp_playlist *", 44)
        lib_mock.sp_playlistcontainer_add_playlist.return_value = sp_playlist
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )

        result = playlist_container.add_playlist(link)

        lib_mock.sp_playlistcontainer_add_playlist.assert_called_with(
            sp_playlistcontainer, sp_link
        )
        self.assertIsInstance(result, spotify.Playlist)
        self.assertEqual(result._sp_playlist, sp_playlist)
        playlist_lib_mock.sp_playlist_add_ref.assert_called_with(sp_playlist)
        self.assertEqual(lib_mock.sp_playlistcontainer_move_playlist.call_count, 0)

    @mock.patch("spotify.link.lib", lib=spotify.lib)
    @mock.patch("spotify.playlist.lib", lib=spotify.lib)
    def test_add_playlist_from_playlist(
        self, playlist_lib_mock, link_lib_mock, lib_mock
    ):
        sp_link = spotify.ffi.cast("sp_link *", 43)
        link = spotify.Link(self.session, sp_link=sp_link, add_ref=False)
        existing_playlist = mock.Mock(spec=spotify.Playlist)
        existing_playlist.link = link
        added_sp_playlist = spotify.ffi.cast("sp_playlist *", 44)
        lib_mock.sp_playlistcontainer_add_playlist.return_value = added_sp_playlist
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )

        result = playlist_container.add_playlist(existing_playlist)

        lib_mock.sp_playlistcontainer_add_playlist.assert_called_with(
            sp_playlistcontainer, sp_link
        )
        self.assertIsInstance(result, spotify.Playlist)
        self.assertEqual(result._sp_playlist, added_sp_playlist)
        playlist_lib_mock.sp_playlist_add_ref.assert_called_with(added_sp_playlist)
        self.assertEqual(lib_mock.sp_playlistcontainer_move_playlist.call_count, 0)

    @mock.patch("spotify.link.lib", lib=spotify.lib)
    @mock.patch("spotify.playlist.lib", lib=spotify.lib)
    def test_add_playlist_at_given_index(
        self, playlist_lib_mock, link_lib_mock, lib_mock
    ):
        sp_link = spotify.ffi.cast("sp_link *", 43)
        link = spotify.Link(self.session, sp_link=sp_link, add_ref=False)
        sp_playlist = spotify.ffi.cast("sp_playlist *", 44)
        lib_mock.sp_playlistcontainer_add_playlist.return_value = sp_playlist
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )
        lib_mock.sp_playlistcontainer_num_playlists.return_value = 100
        lib_mock.sp_playlistcontainer_move_playlist.return_value = int(
            spotify.ErrorType.OK
        )

        result = playlist_container.add_playlist(link, index=7)

        lib_mock.sp_playlistcontainer_add_playlist.assert_called_with(
            sp_playlistcontainer, sp_link
        )
        self.assertIsInstance(result, spotify.Playlist)
        self.assertEqual(result._sp_playlist, sp_playlist)
        playlist_lib_mock.sp_playlist_add_ref.assert_called_with(sp_playlist)
        lib_mock.sp_playlistcontainer_move_playlist.assert_called_with(
            sp_playlistcontainer, 99, 7, 0
        )

    @mock.patch("spotify.link.lib", lib=spotify.lib)
    def test_add_playlist_already_in_the_container(self, link_lib_mock, lib_mock):
        sp_link = spotify.ffi.cast("sp_link *", 43)
        link = spotify.Link(self.session, sp_link=sp_link, add_ref=False)
        lib_mock.sp_playlistcontainer_add_playlist.return_value = spotify.ffi.NULL
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )

        result = playlist_container.add_playlist(link)

        lib_mock.sp_playlistcontainer_add_playlist.assert_called_with(
            sp_playlistcontainer, sp_link
        )
        self.assertIsNone(result)
        self.assertEqual(lib_mock.sp_playlistcontainer_move_playlist.call_count, 0)

    def test_add_playlist_from_unknown_type_fails(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )

        with self.assertRaises(TypeError):
            playlist_container.add_playlist(None)

    def test_add_folder(self, lib_mock):
        lib_mock.sp_playlistcontainer_add_folder.return_value = int(
            spotify.ErrorType.OK
        )
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )

        playlist_container.add_folder("foo bar", index=3)

        lib_mock.sp_playlistcontainer_add_folder.assert_called_with(
            sp_playlistcontainer, 3, mock.ANY
        )
        self.assertEqual(
            spotify.ffi.string(
                lib_mock.sp_playlistcontainer_add_folder.call_args[0][2]
            ),
            b"foo bar",
        )

    def test_add_folder_without_index_adds_to_end(self, lib_mock):
        lib_mock.sp_playlistcontainer_num_playlists.return_value = 7
        lib_mock.sp_playlistcontainer_add_folder.return_value = int(
            spotify.ErrorType.OK
        )
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )

        playlist_container.add_folder("foo bar")

        lib_mock.sp_playlistcontainer_add_folder.assert_called_with(
            sp_playlistcontainer, 7, mock.ANY
        )
        self.assertEqual(
            spotify.ffi.string(
                lib_mock.sp_playlistcontainer_add_folder.call_args[0][2]
            ),
            b"foo bar",
        )

    def test_add_folder_out_of_range_fails(self, lib_mock):
        lib_mock.sp_playlistcontainer_add_folder.return_value = int(
            spotify.ErrorType.INDEX_OUT_OF_RANGE
        )

        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )

        with self.assertRaises(spotify.Error):
            playlist_container.add_folder("foo bar", index=3)

    def test_add_folder_fails_if_name_is_space_only(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )

        with self.assertRaises(ValueError):
            playlist_container.add_folder("   ")

        # Spotify seems to accept e.g. tab-only names, but it doesn't make any
        # sense to allow it, so we disallow names with all combinations of just
        # whitespace.
        with self.assertRaises(ValueError):
            playlist_container.add_folder("\t\t")
        with self.assertRaises(ValueError):
            playlist_container.add_folder("\r\r")
        with self.assertRaises(ValueError):
            playlist_container.add_folder("\n\n")
        with self.assertRaises(ValueError):
            playlist_container.add_folder(" \t\r\n")

    def test_add_folder_fails_if_name_is_too_long(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )

        with self.assertRaises(ValueError):
            playlist_container.add_folder("x" * 300)

    @mock.patch("spotify.playlist.lib", lib=spotify.lib)
    def test_remove_playlist(self, playlist_lib_mock, lib_mock):
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )
        lib_mock.sp_playlistcontainer_num_playlists.return_value = 9
        sp_playlist = spotify.ffi.cast("sp_playlist *", 43)
        lib_mock.sp_playlistcontainer_playlist.return_value = sp_playlist
        lib_mock.sp_playlistcontainer_playlist_type.return_value = int(
            spotify.PlaylistType.PLAYLIST
        )
        lib_mock.sp_playlistcontainer_remove_playlist.return_value = int(
            spotify.ErrorType.OK
        )

        playlist_container.remove_playlist(5)

        lib_mock.sp_playlistcontainer_remove_playlist.assert_called_with(
            sp_playlistcontainer, 5
        )

    @mock.patch("spotify.playlist.lib", lib=spotify.lib)
    def test_remove_playlist_out_of_range_fails(self, playlist_lib_mock, lib_mock):

        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )
        lib_mock.sp_playlistcontainer_num_playlists.return_value = 9
        sp_playlist = spotify.ffi.cast("sp_playlist *", 43)
        lib_mock.sp_playlistcontainer_playlist.return_value = sp_playlist
        lib_mock.sp_playlistcontainer_playlist_type.return_value = int(
            spotify.PlaylistType.PLAYLIST
        )
        lib_mock.sp_playlistcontainer_remove_playlist.return_value = int(
            spotify.ErrorType.INDEX_OUT_OF_RANGE
        )

        with self.assertRaises(spotify.Error):
            playlist_container.remove_playlist(3)

    def test_remove_start_folder_removes_end_folder_too(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )
        lib_mock.sp_playlistcontainer_num_playlists.return_value = 3
        sp_playlist = spotify.ffi.cast("sp_playlist *", 43)
        lib_mock.sp_playlistcontainer_playlist.return_value = sp_playlist
        lib_mock.sp_playlistcontainer_playlist_type.side_effect = [
            int(spotify.PlaylistType.START_FOLDER),
            int(spotify.PlaylistType.PLAYLIST),
            int(spotify.PlaylistType.END_FOLDER),
        ]
        lib_mock.sp_playlistcontainer_playlist_folder_id.side_effect = [
            173,
            173,
        ]
        playlist_container._find_folder_indexes = lambda *a: [0, 2]
        lib_mock.sp_playlistcontainer_remove_playlist.return_value = int(
            spotify.ErrorType.OK
        )

        playlist_container.remove_playlist(0)

        lib_mock.sp_playlistcontainer_playlist_type.assert_called_with(
            sp_playlistcontainer, 0
        )
        lib_mock.sp_playlistcontainer_playlist_folder_id.assert_called_with(
            sp_playlistcontainer, 0
        )
        lib_mock.sp_playlistcontainer_remove_playlist.assert_has_calls(
            [
                mock.call(sp_playlistcontainer, 2),
                mock.call(sp_playlistcontainer, 0),
            ],
            any_order=False,
        )

    def test_remove_end_folder_removes_start_folder_too(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )
        lib_mock.sp_playlistcontainer_num_playlists.return_value = 3
        sp_playlist = spotify.ffi.cast("sp_playlist *", 43)
        lib_mock.sp_playlistcontainer_playlist.return_value = sp_playlist
        lib_mock.sp_playlistcontainer_playlist_type.side_effect = [
            int(spotify.PlaylistType.START_FOLDER),
            int(spotify.PlaylistType.PLAYLIST),
            int(spotify.PlaylistType.END_FOLDER),
        ]
        lib_mock.sp_playlistcontainer_playlist_folder_id.side_effect = [
            173,
            173,
        ]
        playlist_container._find_folder_indexes = lambda *a: [0, 2]
        lib_mock.sp_playlistcontainer_remove_playlist.return_value = int(
            spotify.ErrorType.OK
        )

        playlist_container.remove_playlist(2)

        lib_mock.sp_playlistcontainer_playlist_type.assert_called_with(
            sp_playlistcontainer, 2
        )
        lib_mock.sp_playlistcontainer_playlist_folder_id.assert_called_with(
            sp_playlistcontainer, 2
        )
        lib_mock.sp_playlistcontainer_remove_playlist.assert_has_calls(
            [
                mock.call(sp_playlistcontainer, 2),
                mock.call(sp_playlistcontainer, 0),
            ],
            any_order=False,
        )

    def test_remove_folder_with_everything_in_it(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )
        lib_mock.sp_playlistcontainer_num_playlists.return_value = 3
        sp_playlist = spotify.ffi.cast("sp_playlist *", 43)
        lib_mock.sp_playlistcontainer_playlist.return_value = sp_playlist
        lib_mock.sp_playlistcontainer_playlist_type.side_effect = [
            int(spotify.PlaylistType.START_FOLDER),
            int(spotify.PlaylistType.PLAYLIST),
            int(spotify.PlaylistType.END_FOLDER),
        ]
        lib_mock.sp_playlistcontainer_playlist_folder_id.side_effect = [
            173,
            173,
        ]
        playlist_container._find_folder_indexes = lambda *a: [0, 1, 2]
        lib_mock.sp_playlistcontainer_remove_playlist.return_value = int(
            spotify.ErrorType.OK
        )

        playlist_container.remove_playlist(0, recursive=True)

        lib_mock.sp_playlistcontainer_playlist_type.assert_called_with(
            sp_playlistcontainer, 0
        )
        lib_mock.sp_playlistcontainer_playlist_folder_id.assert_called_with(
            sp_playlistcontainer, 0
        )
        lib_mock.sp_playlistcontainer_remove_playlist.assert_has_calls(
            [
                mock.call(sp_playlistcontainer, 2),
                mock.call(sp_playlistcontainer, 1),
                mock.call(sp_playlistcontainer, 0),
            ],
            any_order=False,
        )

    @mock.patch("spotify.playlist.lib", spec=spotify.lib)
    def test_find_folder_indexes(self, playlist_lib_mock, lib_mock):
        sp_playlist = spotify.ffi.cast("sp_playlist *", 43)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)
        playlists = [
            spotify.PlaylistFolder(173, "foo", spotify.PlaylistType.START_FOLDER),
            playlist,
            spotify.PlaylistFolder(173, "", spotify.PlaylistType.END_FOLDER),
        ]

        result = spotify.PlaylistContainer._find_folder_indexes(
            playlists, 173, recursive=False
        )

        self.assertEqual(result, [0, 2])

    @mock.patch("spotify.playlist.lib", spec=spotify.lib)
    def test_find_folder_indexes_with_unknown_id(self, playlist_lib_mock, lib_mock):

        sp_playlist = spotify.ffi.cast("sp_playlist *", 43)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)
        playlists = [
            spotify.PlaylistFolder(173, "foo", spotify.PlaylistType.START_FOLDER),
            playlist,
            spotify.PlaylistFolder(173, "", spotify.PlaylistType.END_FOLDER),
        ]

        result = spotify.PlaylistContainer._find_folder_indexes(
            playlists, 174, recursive=False
        )

        self.assertEqual(result, [])

    @mock.patch("spotify.playlist.lib", spec=spotify.lib)
    def test_find_folder_indexes_recursive(self, playlist_lib_mock, lib_mock):
        sp_playlist = spotify.ffi.cast("sp_playlist *", 43)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)
        playlists = [
            spotify.PlaylistFolder(173, "foo", spotify.PlaylistType.START_FOLDER),
            playlist,
            spotify.PlaylistFolder(173, "", spotify.PlaylistType.END_FOLDER),
        ]

        result = spotify.PlaylistContainer._find_folder_indexes(
            playlists, 173, recursive=True
        )

        self.assertEqual(result, [0, 1, 2])

    @mock.patch("spotify.playlist.lib", spec=spotify.lib)
    def test_find_folder_indexes_without_end(self, playlist_lib_mock, lib_mock):

        sp_playlist = spotify.ffi.cast("sp_playlist *", 43)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)
        playlists = [
            spotify.PlaylistFolder(173, "foo", spotify.PlaylistType.START_FOLDER),
            playlist,
        ]

        result = spotify.PlaylistContainer._find_folder_indexes(
            playlists, 173, recursive=True
        )

        self.assertEqual(result, [0])

    @mock.patch("spotify.playlist.lib", spec=spotify.lib)
    def test_find_folder_indexes_without_start(self, playlist_lib_mock, lib_mock):

        sp_playlist = spotify.ffi.cast("sp_playlist *", 43)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)
        playlists = [
            playlist,
            spotify.PlaylistFolder(173, "", spotify.PlaylistType.END_FOLDER),
        ]

        result = spotify.PlaylistContainer._find_folder_indexes(
            playlists, 173, recursive=True
        )

        self.assertEqual(result, [1])

    def test_move_playlist(self, lib_mock):
        lib_mock.sp_playlistcontainer_move_playlist.return_value = int(
            spotify.ErrorType.OK
        )
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )

        playlist_container.move_playlist(5, 7)

        lib_mock.sp_playlistcontainer_move_playlist.assert_called_with(
            sp_playlistcontainer, 5, 7, 0
        )

    def test_move_playlist_dry_run(self, lib_mock):
        lib_mock.sp_playlistcontainer_move_playlist.return_value = int(
            spotify.ErrorType.OK
        )
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )

        playlist_container.move_playlist(5, 7, dry_run=True)

        lib_mock.sp_playlistcontainer_move_playlist.assert_called_with(
            sp_playlistcontainer, 5, 7, 1
        )

    def test_move_playlist_out_of_range_fails(self, lib_mock):
        lib_mock.sp_playlistcontainer_move_playlist.return_value = int(
            spotify.ErrorType.INDEX_OUT_OF_RANGE
        )
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )

        with self.assertRaises(spotify.Error):
            playlist_container.move_playlist(5, 7)

    def test_move_playlist_to_itself_is_a_noop(self, lib_mock):
        lib_mock.sp_playlistcontainer_move_playlist.return_value = int(
            spotify.ErrorType.INVALID_INDATA
        )
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )

        playlist_container.move_playlist(5, 5)

        self.assertEqual(lib_mock.sp_playlistcontainer_move_playlist.call_count, 0)

    @mock.patch("spotify.User", spec=spotify.User)
    def test_owner(self, user_mock, lib_mock):
        user_mock.return_value = mock.sentinel.user
        sp_user = spotify.ffi.cast("sp_user *", 43)
        lib_mock.sp_playlistcontainer_owner.return_value = sp_user
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )

        result = playlist_container.owner

        lib_mock.sp_playlistcontainer_owner.assert_called_with(sp_playlistcontainer)
        user_mock.assert_called_with(self.session, sp_user=sp_user, add_ref=True)
        self.assertEqual(result, mock.sentinel.user)

    @mock.patch("spotify.playlist.lib", spec=spotify.lib)
    @mock.patch("spotify.playlist_unseen_tracks.lib", spec=spotify.lib)
    def test_get_unseen_tracks(self, unseen_lib_mock, playlist_lib_mock, lib_mock):

        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )
        sp_playlist = spotify.ffi.cast("sp_playlist *", 43)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)
        unseen_lib_mock.sp_playlistcontainer_get_unseen_tracks.return_value = 0

        result = playlist_container.get_unseen_tracks(playlist)

        self.assertIsInstance(result, spotify.PlaylistUnseenTracks)
        self.assertEqual(len(result), 0)

    @mock.patch("spotify.playlist.lib", spec=spotify.lib)
    def test_clear_unseen_tracks(self, playlist_lib_mock, lib_mock):
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )
        sp_playlist = spotify.ffi.cast("sp_playlist *", 43)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)
        lib_mock.sp_playlistcontainer_clear_unseen_tracks.return_value = 0

        playlist_container.clear_unseen_tracks(playlist)

        lib_mock.sp_playlistcontainer_clear_unseen_tracks.assert_called_with(
            sp_playlistcontainer, sp_playlist
        )

    @mock.patch("spotify.playlist.lib", spec=spotify.lib)
    def test_clear_unseen_tracks_raises_error_on_failure(
        self, playlist_lib_mock, lib_mock
    ):

        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )
        sp_playlist = spotify.ffi.cast("sp_playlist *", 43)
        playlist = spotify.Playlist(self.session, sp_playlist=sp_playlist)
        lib_mock.sp_playlistcontainer_clear_unseen_tracks.return_value = -1

        with self.assertRaises(spotify.Error):
            playlist_container.clear_unseen_tracks(playlist)

    def test_first_on_call_adds_obj_emitters_list(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )

        playlist_container.on(
            spotify.PlaylistContainerEvent.PLAYLIST_ADDED, lambda *args: None
        )

        self.assertIn(playlist_container, self.session._emitters)

        playlist_container.off()

    def test_last_off_call_removes_obj_from_emitters_list(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )

        playlist_container.on(
            spotify.PlaylistContainerEvent.PLAYLIST_ADDED, lambda *args: None
        )
        playlist_container.off(spotify.PlaylistContainerEvent.PLAYLIST_ADDED)

        self.assertNotIn(playlist_container, self.session._emitters)

    def test_other_off_calls_keeps_obj_in_emitters_list(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 42)
        playlist_container = spotify.PlaylistContainer(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )

        playlist_container.on(
            spotify.PlaylistContainerEvent.PLAYLIST_ADDED, lambda *args: None
        )
        playlist_container.on(
            spotify.PlaylistContainerEvent.PLAYLIST_MOVED, lambda *args: None
        )
        playlist_container.off(spotify.PlaylistContainerEvent.PLAYLIST_ADDED)

        self.assertIn(playlist_container, self.session._emitters)

        playlist_container.off(spotify.PlaylistContainerEvent.PLAYLIST_MOVED)

        self.assertNotIn(playlist_container, self.session._emitters)


@unittest.skipIf("TRAVIS" in os.environ, "Crashes on Travis trusty with Python 3.5.0")
@mock.patch("spotify.playlist_container.lib", spec=spotify.lib)
class PlaylistContainerCallbacksTest(unittest.TestCase):
    def setUp(self):
        self.session = tests.create_session_mock()
        spotify._session_instance = self.session

    def tearDown(self):
        spotify._session_instance = None

    @mock.patch("spotify.playlist.lib", spec=spotify.lib)
    def test_playlist_added_callback(self, playlist_lib_mock, lib_mock):
        callback = mock.Mock()
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 43)
        playlist_container = spotify.PlaylistContainer._cached(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )
        playlist_container.on(spotify.PlaylistContainerEvent.PLAYLIST_ADDED, callback)

        _PlaylistContainerCallbacks.playlist_added(
            sp_playlistcontainer, sp_playlist, 7, spotify.ffi.NULL
        )

        callback.assert_called_once_with(playlist_container, mock.ANY, 7)
        playlist = callback.call_args[0][1]
        self.assertIsInstance(playlist, spotify.Playlist)
        self.assertEqual(playlist._sp_playlist, sp_playlist)

    @mock.patch("spotify.playlist.lib", spec=spotify.lib)
    def test_playlist_removed_callback(self, playlist_lib_mock, lib_mock):
        callback = mock.Mock()
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 43)
        playlist_container = spotify.PlaylistContainer._cached(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )
        playlist_container.on(spotify.PlaylistContainerEvent.PLAYLIST_REMOVED, callback)

        _PlaylistContainerCallbacks.playlist_removed(
            sp_playlistcontainer, sp_playlist, 7, spotify.ffi.NULL
        )

        callback.assert_called_once_with(playlist_container, mock.ANY, 7)
        playlist = callback.call_args[0][1]
        self.assertIsInstance(playlist, spotify.Playlist)
        self.assertEqual(playlist._sp_playlist, sp_playlist)

    @mock.patch("spotify.playlist.lib", spec=spotify.lib)
    def test_playlist_moved_callback(self, playlist_lib_mock, lib_mock):
        callback = mock.Mock()
        sp_playlist = spotify.ffi.cast("sp_playlist *", 42)
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 43)
        playlist_container = spotify.PlaylistContainer._cached(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )
        playlist_container.on(spotify.PlaylistContainerEvent.PLAYLIST_MOVED, callback)

        _PlaylistContainerCallbacks.playlist_moved(
            sp_playlistcontainer, sp_playlist, 7, 13, spotify.ffi.NULL
        )

        callback.assert_called_once_with(playlist_container, mock.ANY, 7, 13)
        playlist = callback.call_args[0][1]
        self.assertIsInstance(playlist, spotify.Playlist)
        self.assertEqual(playlist._sp_playlist, sp_playlist)

    def test_container_loaded_callback(self, lib_mock):
        callback = mock.Mock()
        sp_playlistcontainer = spotify.ffi.cast("sp_playlistcontainer *", 43)
        playlist_container = spotify.PlaylistContainer._cached(
            self.session, sp_playlistcontainer=sp_playlistcontainer
        )
        playlist_container.on(spotify.PlaylistContainerEvent.CONTAINER_LOADED, callback)

        _PlaylistContainerCallbacks.container_loaded(
            sp_playlistcontainer, spotify.ffi.NULL
        )

        callback.assert_called_once_with(playlist_container)


class PlaylistFolderTest(unittest.TestCase):
    def test_id(self):
        folder = spotify.PlaylistFolder(
            id=123, name="foo", type=spotify.PlaylistType.START_FOLDER
        )

        self.assertEqual(folder.id, 123)

    def test_image(self):
        folder = spotify.PlaylistFolder(
            id=123, name="foo", type=spotify.PlaylistType.START_FOLDER
        )

        self.assertEqual(folder.name, "foo")

    def test_type(self):
        folder = spotify.PlaylistFolder(
            id=123, name="foo", type=spotify.PlaylistType.START_FOLDER
        )

        self.assertEqual(folder.type, spotify.PlaylistType.START_FOLDER)


class PlaylistTypeTest(unittest.TestCase):
    def test_has_constants(self):
        self.assertEqual(spotify.PlaylistType.PLAYLIST, 0)
        self.assertEqual(spotify.PlaylistType.START_FOLDER, 1)
        self.assertEqual(spotify.PlaylistType.END_FOLDER, 2)
