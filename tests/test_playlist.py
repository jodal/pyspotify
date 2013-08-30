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
        link_instance_mock = link_mock.return_value
        link_instance_mock.uri = 'foo'
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist=sp_playlist)

        result = repr(playlist)

        self.assertEqual(result, 'spotify.Playlist(%r)' % 'foo')

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


class PlaylistOfflineStatusTest(unittest.TestCase):

    def test_has_constants(self):
        self.assertEqual(spotify.PlaylistOfflineStatus.NO, 0)
        self.assertEqual(spotify.PlaylistOfflineStatus.DOWNLOADING, 2)
