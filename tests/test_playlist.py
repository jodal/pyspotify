from __future__ import unicode_literals

import gc
import mock
import unittest

import spotify


@mock.patch('spotify.playlist.lib', spec=spotify.lib)
class PlaylistTest(unittest.TestCase):

    def create_session(self, lib_mock):
        session = mock.sentinel.session
        session._sp_session = mock.sentinel.sp_session
        spotify.session_instance = session
        return session

    def tearDown(self):
        spotify.session_instance = None

    def test_create_without_uri_or_sp_playlist_fails(self, lib_mock):
        self.assertRaises(AssertionError, spotify.Playlist)

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

        self.assertRaises(ValueError, spotify.Playlist, uri)

    def test_adds_ref_to_sp_playlist_when_created(self, lib_mock):
        sp_playlist = spotify.ffi.new('int *')

        spotify.Playlist(sp_playlist=sp_playlist)

        lib_mock.sp_playlist_add_ref.assert_called_with(sp_playlist)

    def test_releases_sp_playlist_when_playlist_dies(self, lib_mock):
        sp_playlist = spotify.ffi.new('int *')

        playlist = spotify.Playlist(sp_playlist=sp_playlist)
        playlist = None  # noqa
        gc.collect()  # Needed for PyPy

        lib_mock.sp_playlist_release.assert_called_with(sp_playlist)

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
        link_mock.side_effect = ValueError('error message')
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

        self.assertRaises(spotify.Error, playlist.rename, 'Quux')

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

        self.assertRaises(
            spotify.Error, setattr, playlist, 'collaborative', False)

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

        self.assertRaises(spotify.Error, playlist.set_autolink_tracks, True)

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
        session = self.create_session(lib_mock)
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

    def test_is_in_ram(self, lib_mock):
        session = self.create_session(lib_mock)
        lib_mock.sp_playlist_is_in_ram.return_value = 1
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        result = playlist.in_ram

        lib_mock.sp_playlist_is_in_ram.assert_called_with(
            session._sp_session, sp_playlist)
        self.assertTrue(result)

    def test_set_in_ram(self, lib_mock):
        session = self.create_session(lib_mock)
        lib_mock.sp_playlist_set_in_ram.return_value = int(
            spotify.ErrorType.OK)
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        playlist.in_ram = False

        lib_mock.sp_playlist_set_in_ram.assert_called_with(
            session._sp_session, sp_playlist, 0)

    def test_set_in_ram_fails_if_error(self, lib_mock):
        self.create_session(lib_mock)
        lib_mock.sp_playlist_set_in_ram.return_value = int(
            spotify.ErrorType.BAD_API_VERSION)
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        self.assertRaises(
            spotify.Error, setattr, playlist, 'in_ram', False)

    def test_set_offline_mode(self, lib_mock):
        session = self.create_session(lib_mock)
        lib_mock.sp_playlist_set_offline_mode.return_value = int(
            spotify.ErrorType.OK)
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        playlist.set_offline_mode(False)

        lib_mock.sp_playlist_set_offline_mode.assert_called_with(
            session._sp_session, sp_playlist, 0)

    def test_set_offline_mode_fails_if_error(self, lib_mock):
        self.create_session(lib_mock)
        lib_mock.sp_playlist_set_offline_mode.return_value = int(
            spotify.ErrorType.BAD_API_VERSION)
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        self.assertRaises(
            spotify.Error, playlist.set_offline_mode, False)

    def test_offline_status(self, lib_mock):
        session = self.create_session(lib_mock)
        lib_mock.sp_playlist_get_offline_status.return_value = 2
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        result = playlist.offline_status

        lib_mock.sp_playlist_get_offline_status.assert_called_with(
            session._sp_session, sp_playlist)
        self.assertIs(result, spotify.PlaylistOfflineStatus.DOWNLOADING)

    def test_offline_download_completed(self, lib_mock):
        session = self.create_session(lib_mock)
        lib_mock.sp_playlist_get_offline_status.return_value = 2
        lib_mock.sp_playlist_get_offline_download_completed.return_value = 73
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        result = playlist.offline_download_completed

        lib_mock.sp_playlist_get_offline_download_completed.assert_called_with(
            session._sp_session, sp_playlist)
        self.assertEqual(result, 73)

    def test_offline_download_completed_when_not_downloading(self, lib_mock):
        self.create_session(lib_mock)
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
        link_mock.return_value = mock.sentinel.link
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        result = playlist.link

        link_mock.assert_called_once_with(playlist)
        self.assertEqual(result, mock.sentinel.link)


@mock.patch('spotify.playlist.lib', spec=spotify.lib)
class PlaylistContainerTest(unittest.TestCase):

    def create_session(self, lib_mock):
        session = mock.sentinel.session
        session._sp_session = mock.sentinel.sp_session
        spotify.session_instance = session
        return session

    def tearDown(self):
        spotify.session_instance = None

    def test_adds_ref_to_sp_playlistcontainer_when_created(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.new('int *')

        spotify.PlaylistContainer(sp_playlistcontainer)

        lib_mock.sp_playlistcontainer_add_ref.assert_called_with(
            sp_playlistcontainer)

    def test_releases_sp_playlistcontainer_when_container_dies(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.new('int *')

        playlist_container = spotify.PlaylistContainer(sp_playlistcontainer)
        playlist_container = None  # noqa
        gc.collect()  # Needed for PyPy

        lib_mock.sp_playlistcontainer_release.assert_called_with(
            sp_playlistcontainer)

    def test_repr(self, lib_mock):
        lib_mock.sp_playlistcontainer_num_playlists.return_value = 0
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)

        result = repr(playlist_container)

        self.assertEqual(result, '[]')

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

    def test_getitem_with_folder(self, lib_mock):
        folder_name = 'foobar'

        def func(sp_playlistcontainer, index, buffer_, buffer_size):
            # -1 to keep a char free for \0 terminating the string
            length = min(len(folder_name), buffer_size - 1)
            # Due to Python 3 treating bytes as an array of ints, we have to
            # encode and copy chars one by one.
            for i in range(length):
                buffer_[i] = folder_name[i].encode('utf-8')
            return len(folder_name)

        lib_mock.sp_session_remembered_user.side_effect = func

        lib_mock.sp_playlistcontainer_num_playlists.return_value = 3
        lib_mock.sp_playlistcontainer_playlist_type.side_effect = [
            int(spotify.PlaylistType.START_FOLDER),
            int(spotify.PlaylistType.PLAYLIST),
            int(spotify.PlaylistType.END_FOLDER)]
        sp_playlist = spotify.ffi.new('int *')
        lib_mock.sp_playlistcontainer_playlist.return_value = sp_playlist
        lib_mock.sp_playlistcontainer_playlist_folder_id.side_effect = [
            1001, 1002]
        lib_mock.sp_playlistcontainer_playlist_folder_name.side_effect = func
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

        self.assertRaises(RuntimeError, playlist_container.__getitem__, 0)

    def test_getitem_raises_index_error_on_negative_index(self, lib_mock):
        lib_mock.sp_playlistcontainer_num_playlists.return_value = 1
        sp_playlist = spotify.ffi.new('int *')
        lib_mock.sp_playlistcontainer_playlist.return_value = sp_playlist
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)

        self.assertRaises(IndexError, playlist_container.__getitem__, -1)

    def test_getitem_raises_index_error_on_too_high_index(self, lib_mock):
        lib_mock.sp_playlistcontainer_num_playlists.return_value = 1
        sp_playlist = spotify.ffi.new('int *')
        lib_mock.sp_playlistcontainer_playlist.return_value = sp_playlist
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)

        self.assertRaises(IndexError, playlist_container.__getitem__, 1)

    def test_getitem_raises_type_error_on_non_integral_index(self, lib_mock):
        lib_mock.sp_playlistcontainer_num_playlists.return_value = 1
        sp_playlist = spotify.ffi.new('int *')
        lib_mock.sp_playlistcontainer_playlist.return_value = sp_playlist
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)

        self.assertRaises(TypeError, playlist_container.__getitem__, 'abc')

    def test_add_new_playlist(self, lib_mock):
        sp_playlist = spotify.ffi.new('int *')
        lib_mock.sp_playlistcontainer_add_new_playlist.return_value = (
            sp_playlist)
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)

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

    def test_add_new_playlist_fails_if_name_is_space_only(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)

        self.assertRaises(
            ValueError, playlist_container.add_new_playlist, '   ')

    def test_add_new_playlist_fails_if_name_is_too_long(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)

        self.assertRaises(
            ValueError, playlist_container.add_new_playlist, 'x' * 300)

    def test_add_new_playlist_fails_if_operation_fails(self, lib_mock):
        lib_mock.sp_playlistcontainer_add_new_playlist.return_value = (
            spotify.ffi.NULL)
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)

        self.assertRaises(
            ValueError, playlist_container.add_new_playlist, 'foo bar')

    def test_add_playlist_from_link(self, lib_mock):
        self.create_session(lib_mock)
        sp_link = spotify.ffi.new('int *')
        link = spotify.Link(sp_link)
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

    def test_add_playlist_from_playlist(self, lib_mock):
        self.create_session(lib_mock)
        sp_link = spotify.ffi.new('int *')
        link = spotify.Link(sp_link)
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

    def test_add_playlist_already_in_the_container(self, lib_mock):
        self.create_session(lib_mock)
        sp_link = spotify.ffi.new('int *')
        link = spotify.Link(sp_link)
        lib_mock.sp_playlistcontainer_add_playlist.return_value = (
            spotify.ffi.NULL)
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)

        result = playlist_container.add_playlist(link)

        lib_mock.sp_playlistcontainer_add_playlist.assert_called_with(
            sp_playlistcontainer, sp_link)
        self.assertIsNone(result)

    def test_add_playlist_from_unknown_type_fails(self, lib_mock):
        sp_playlistcontainer = spotify.ffi.new('int *')
        playlist_container = spotify.PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer)

        self.assertRaises(ValueError, playlist_container.add_playlist, None)

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

        self.assertRaises(
            spotify.Error, playlist_container.add_folder, 'foo bar', index=3)

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


class PlaylistTypeTest(unittest.TestCase):

    def test_has_constants(self):
        self.assertEqual(spotify.PlaylistType.PLAYLIST, 0)
        self.assertEqual(spotify.PlaylistType.START_FOLDER, 1)
        self.assertEqual(spotify.PlaylistType.END_FOLDER, 2)
