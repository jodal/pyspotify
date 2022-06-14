# encoding: utf-8

from __future__ import unicode_literals

import unittest

import pytest

import spotify
import tests
from spotify.session import _SessionCallbacks
from tests import mock


@mock.patch("spotify.session.lib", spec=spotify.lib)
class SessionTest(unittest.TestCase):
    def tearDown(self):
        spotify._session_instance = None

    def test_raises_error_if_a_session_already_exists(self, lib_mock):
        tests.create_real_session(lib_mock)

        with self.assertRaises(RuntimeError):
            tests.create_real_session(lib_mock)

    @mock.patch("spotify.Config")
    def test_creates_config_if_none_provided(self, config_cls_mock, lib_mock):
        lib_mock.sp_session_create.return_value = spotify.ErrorType.OK

        session = spotify.Session()

        config_cls_mock.assert_called_once_with()
        self.assertEqual(session.config, config_cls_mock.return_value)

    @mock.patch("spotify.Config")
    def test_tries_to_load_application_key_if_none_provided(
        self, config_cls_mock, lib_mock
    ):
        lib_mock.sp_session_create.return_value = spotify.ErrorType.OK
        config_mock = config_cls_mock.return_value
        config_mock.application_key = None

        spotify.Session()

        config_mock.load_application_key_file.assert_called_once_with()

    def test_raises_error_if_not_ok(self, lib_mock):
        lib_mock.sp_session_create.return_value = spotify.ErrorType.BAD_API_VERSION
        config = spotify.Config()
        config.application_key = b"\x01" * 321

        with self.assertRaises(spotify.Error):
            spotify.Session(config=config)

    def test_releases_sp_session_when_session_dies(self, lib_mock):
        sp_session = spotify.ffi.NULL

        def func(sp_session_config, sp_session_ptr):
            sp_session_ptr[0] = sp_session
            return spotify.ErrorType.OK

        lib_mock.sp_session_create.side_effect = func
        config = spotify.Config()
        config.application_key = b"\x01" * 321

        session = spotify.Session(config=config)
        session = None  # noqa
        spotify._session_instance = None
        tests.gc_collect()

        lib_mock.sp_session_release.assert_called_with(sp_session)

    def test_login_raises_error_if_no_password_and_no_blob(self, lib_mock):
        lib_mock.sp_session_login.return_value = spotify.ErrorType.OK
        session = tests.create_real_session(lib_mock)

        with self.assertRaises(AttributeError):
            session.login("alice")

    def test_login_with_password(self, lib_mock):
        lib_mock.sp_session_login.return_value = spotify.ErrorType.OK
        session = tests.create_real_session(lib_mock)

        session.login("alice", "secret")

        lib_mock.sp_session_login.assert_called_once_with(
            session._sp_session, mock.ANY, mock.ANY, False, spotify.ffi.NULL
        )
        self.assertEqual(
            spotify.ffi.string(lib_mock.sp_session_login.call_args[0][1]),
            b"alice",
        )
        self.assertEqual(
            spotify.ffi.string(lib_mock.sp_session_login.call_args[0][2]),
            b"secret",
        )

    def test_login_with_blob(self, lib_mock):
        lib_mock.sp_session_login.return_value = spotify.ErrorType.OK
        session = tests.create_real_session(lib_mock)

        session.login("alice", blob="secret blob")

        lib_mock.sp_session_login.assert_called_once_with(
            session._sp_session, mock.ANY, spotify.ffi.NULL, False, mock.ANY
        )
        self.assertEqual(
            spotify.ffi.string(lib_mock.sp_session_login.call_args[0][1]),
            b"alice",
        )
        self.assertEqual(
            spotify.ffi.string(lib_mock.sp_session_login.call_args[0][4]),
            b"secret blob",
        )

    def test_login_with_remember_me_flag(self, lib_mock):
        lib_mock.sp_session_login.return_value = spotify.ErrorType.OK
        session = tests.create_real_session(lib_mock)

        session.login("alice", "secret", remember_me="anything truish")

        lib_mock.sp_session_login.assert_called_once_with(
            session._sp_session, mock.ANY, mock.ANY, True, spotify.ffi.NULL
        )

    def test_login_fail_raises_error(self, lib_mock):
        lib_mock.sp_session_login.return_value = spotify.ErrorType.NO_SUCH_USER
        session = tests.create_real_session(lib_mock)

        with self.assertRaises(spotify.Error):
            session.login("alice", "secret")

    def test_logout(self, lib_mock):
        lib_mock.sp_session_logout.return_value = spotify.ErrorType.OK
        session = tests.create_real_session(lib_mock)

        session.logout()

        lib_mock.sp_session_logout.assert_called_once_with(session._sp_session)

    def test_logout_fail_raises_error(self, lib_mock):
        lib_mock.sp_session_login.return_value = spotify.ErrorType.BAD_API_VERSION
        session = tests.create_real_session(lib_mock)

        with self.assertRaises(spotify.Error):
            session.logout()

    def test_remembered_user_name_grows_buffer_to_fit_username(self, lib_mock):
        username = "alice" * 100

        lib_mock.sp_session_remembered_user.side_effect = tests.buffer_writer(username)
        session = tests.create_real_session(lib_mock)

        result = session.remembered_user_name

        lib_mock.sp_session_remembered_user.assert_called_with(
            session._sp_session, mock.ANY, mock.ANY
        )
        self.assertEqual(result, username)

    def test_remembered_user_name_is_none_if_not_remembered(self, lib_mock):
        lib_mock.sp_session_remembered_user.return_value = -1
        session = tests.create_real_session(lib_mock)

        result = session.remembered_user_name

        lib_mock.sp_session_remembered_user.assert_called_with(
            session._sp_session, mock.ANY, mock.ANY
        )
        self.assertIsNone(result)

    def test_relogin(self, lib_mock):
        lib_mock.sp_session_relogin.return_value = spotify.ErrorType.OK
        session = tests.create_real_session(lib_mock)

        session.relogin()

        lib_mock.sp_session_relogin.assert_called_once_with(session._sp_session)

    def test_relogin_fail_raises_error(self, lib_mock):
        lib_mock.sp_session_relogin.return_value = spotify.ErrorType.NO_CREDENTIALS
        session = tests.create_real_session(lib_mock)

        with self.assertRaises(spotify.Error):
            session.relogin()

    def test_forget_me(self, lib_mock):
        lib_mock.sp_session_forget_me.return_value = spotify.ErrorType.OK
        session = tests.create_real_session(lib_mock)

        session.forget_me()

        lib_mock.sp_session_forget_me.assert_called_with(session._sp_session)

    def test_forget_me_fail_raises_error(self, lib_mock):
        lib_mock.sp_session_forget_me.return_value = spotify.ErrorType.BAD_API_VERSION
        session = tests.create_real_session(lib_mock)

        with self.assertRaises(spotify.Error):
            session.forget_me()

    @mock.patch("spotify.user.lib", spec=spotify.lib)
    def test_user(self, user_lib_mock, lib_mock):
        lib_mock.sp_session_user.return_value = spotify.ffi.cast("sp_user *", 42)
        session = tests.create_real_session(lib_mock)

        result = session.user

        lib_mock.sp_session_user.assert_called_with(session._sp_session)
        self.assertIsInstance(result, spotify.User)

    def test_user_if_not_logged_in(self, lib_mock):
        lib_mock.sp_session_user.return_value = spotify.ffi.NULL
        session = tests.create_real_session(lib_mock)

        result = session.user

        lib_mock.sp_session_user.assert_called_with(session._sp_session)
        self.assertIsNone(result)

    def test_user_name(self, lib_mock):
        lib_mock.sp_session_user_name.return_value = spotify.ffi.new("char[]", b"alice")
        session = tests.create_real_session(lib_mock)

        result = session.user_name

        lib_mock.sp_session_user_name.assert_called_with(session._sp_session)
        self.assertEqual(result, "alice")

    def test_user_country(self, lib_mock):
        lib_mock.sp_session_user_country.return_value = ord("S") << 8 | ord("E")
        session = tests.create_real_session(lib_mock)

        result = session.user_country

        lib_mock.sp_session_user_country.assert_called_with(session._sp_session)
        self.assertEqual(result, "SE")

    @mock.patch("spotify.playlist_container.lib", spec=spotify.lib)
    def test_playlist_container(self, playlist_lib_mock, lib_mock):
        lib_mock.sp_session_playlistcontainer.return_value = spotify.ffi.cast(
            "sp_playlistcontainer *", 42
        )
        session = tests.create_real_session(lib_mock)

        with pytest.warns(
            UserWarning, match="Spotify broke the libspotify playlists API"
        ):
            result = session.playlist_container

        lib_mock.sp_session_playlistcontainer.assert_called_with(session._sp_session)
        self.assertIsInstance(result, spotify.PlaylistContainer)

    @mock.patch("spotify.playlist_container.lib", spec=spotify.lib)
    def test_playlist_container_if_already_listened_to(
        self, playlist_lib_mock, lib_mock
    ):
        lib_mock.sp_session_playlistcontainer.return_value = spotify.ffi.cast(
            "sp_playlistcontainer *", 42
        )
        session = tests.create_real_session(lib_mock)

        with pytest.warns(
            UserWarning, match="Spotify broke the libspotify playlists API"
        ):
            result1 = session.playlist_container
        result1.on(spotify.PlaylistContainerEvent.PLAYLIST_ADDED, lambda *args: None)
        with pytest.warns(
            UserWarning, match="Spotify broke the libspotify playlists API"
        ):
            result2 = session.playlist_container

        result1.off()

        self.assertIsInstance(result1, spotify.PlaylistContainer)
        self.assertIs(result1, result2)

    def test_playlist_container_if_not_logged_in(self, lib_mock):
        lib_mock.sp_session_playlistcontainer.return_value = spotify.ffi.NULL
        session = tests.create_real_session(lib_mock)

        with pytest.warns(
            UserWarning, match="Spotify broke the libspotify playlists API"
        ):
            result = session.playlist_container

        lib_mock.sp_session_playlistcontainer.assert_called_with(session._sp_session)
        self.assertIsNone(result)

    @mock.patch("spotify.playlist.lib", spec=spotify.lib)
    def test_inbox(self, playlist_lib_mock, lib_mock):
        lib_mock.sp_session_inbox_create.return_value = spotify.ffi.cast(
            "sp_playlist *", 42
        )
        session = tests.create_real_session(lib_mock)

        with pytest.warns(
            UserWarning, match="Spotify broke the libspotify playlists API"
        ):
            result = session.inbox

        lib_mock.sp_session_inbox_create.assert_called_with(session._sp_session)
        self.assertIsInstance(result, spotify.Playlist)

        # Since we *created* the sp_playlist, we already have a refcount of 1
        # and shouldn't increase the refcount when wrapping this sp_playlist in
        # a Playlist object
        self.assertEqual(playlist_lib_mock.sp_playlist_add_ref.call_count, 0)

    def test_inbox_if_not_logged_in(self, lib_mock):
        lib_mock.sp_session_inbox_create.return_value = spotify.ffi.NULL
        session = tests.create_real_session(lib_mock)

        with pytest.warns(
            UserWarning, match="Spotify broke the libspotify playlists API"
        ):
            result = session.inbox

        lib_mock.sp_session_inbox_create.assert_called_with(session._sp_session)
        self.assertIsNone(result)

    def test_set_cache_size(self, lib_mock):
        lib_mock.sp_session_set_cache_size.return_value = spotify.ErrorType.OK
        session = tests.create_real_session(lib_mock)

        session.set_cache_size(100)

        lib_mock.sp_session_set_cache_size.assert_called_once_with(
            session._sp_session, 100
        )

    def test_set_cache_size_fail_raises_error(self, lib_mock):
        lib_mock.sp_session_set_cache_size.return_value = (
            spotify.ErrorType.BAD_API_VERSION
        )
        session = tests.create_real_session(lib_mock)

        with self.assertRaises(spotify.Error):
            session.set_cache_size(100)

    def test_flush_caches(self, lib_mock):
        lib_mock.sp_session_flush_caches.return_value = spotify.ErrorType.OK
        session = tests.create_real_session(lib_mock)

        session.flush_caches()

        lib_mock.sp_session_flush_caches.assert_called_once_with(session._sp_session)

    def test_flush_caches_fail_raises_error(self, lib_mock):
        lib_mock.sp_session_flush_caches.return_value = (
            spotify.ErrorType.BAD_API_VERSION
        )
        session = tests.create_real_session(lib_mock)

        with self.assertRaises(spotify.Error):
            session.flush_caches()

    def test_preferred_bitrate(self, lib_mock):
        lib_mock.sp_session_preferred_bitrate.return_value = spotify.ErrorType.OK
        session = tests.create_real_session(lib_mock)

        session.preferred_bitrate(spotify.Bitrate.BITRATE_320k)

        lib_mock.sp_session_preferred_bitrate.assert_called_with(
            session._sp_session, spotify.Bitrate.BITRATE_320k
        )

    def test_preferred_bitrate_fail_raises_error(self, lib_mock):
        lib_mock.sp_session_preferred_bitrate.return_value = (
            spotify.ErrorType.INVALID_ARGUMENT
        )
        session = tests.create_real_session(lib_mock)

        with self.assertRaises(spotify.Error):
            session.preferred_bitrate(17)

    def test_preferred_offline_bitrate(self, lib_mock):
        lib_mock.sp_session_preferred_offline_bitrate.return_value = (
            spotify.ErrorType.OK
        )
        session = tests.create_real_session(lib_mock)

        session.preferred_offline_bitrate(spotify.Bitrate.BITRATE_320k)

        lib_mock.sp_session_preferred_offline_bitrate.assert_called_with(
            session._sp_session, spotify.Bitrate.BITRATE_320k, 0
        )

    def test_preferred_offline_bitrate_with_allow_resync(self, lib_mock):
        lib_mock.sp_session_preferred_offline_bitrate.return_value = (
            spotify.ErrorType.OK
        )
        session = tests.create_real_session(lib_mock)

        session.preferred_offline_bitrate(
            spotify.Bitrate.BITRATE_320k, allow_resync=True
        )

        lib_mock.sp_session_preferred_offline_bitrate.assert_called_with(
            session._sp_session, spotify.Bitrate.BITRATE_320k, 1
        )

    def test_preferred_offline_bitrate_fail_raises_error(self, lib_mock):
        lib_mock.sp_session_preferred_offline_bitrate.return_value = (
            spotify.ErrorType.INVALID_ARGUMENT
        )
        session = tests.create_real_session(lib_mock)

        with self.assertRaises(spotify.Error):
            session.preferred_offline_bitrate(17)

    def test_get_volume_normalization(self, lib_mock):
        lib_mock.sp_session_get_volume_normalization.return_value = 0
        session = tests.create_real_session(lib_mock)

        result = session.volume_normalization

        lib_mock.sp_session_get_volume_normalization.assert_called_with(
            session._sp_session
        )
        self.assertFalse(result)

    def test_set_volume_normalization(self, lib_mock):
        lib_mock.sp_session_set_volume_normalization.return_value = spotify.ErrorType.OK
        session = tests.create_real_session(lib_mock)

        session.volume_normalization = True

        lib_mock.sp_session_set_volume_normalization.assert_called_with(
            session._sp_session, 1
        )

    def test_set_volume_normalization_fail_raises_error(self, lib_mock):
        lib_mock.sp_session_set_volume_normalization.return_value = (
            spotify.ErrorType.BAD_API_VERSION
        )
        session = tests.create_real_session(lib_mock)

        with self.assertRaises(spotify.Error):
            session.volume_normalization = True

    def test_process_events_returns_ms_to_next_timeout(self, lib_mock):
        def func(sp_session, int_ptr):
            int_ptr[0] = 5500
            return spotify.ErrorType.OK

        lib_mock.sp_session_process_events.side_effect = func

        session = tests.create_real_session(lib_mock)

        timeout = session.process_events()

        self.assertEqual(timeout, 5500)

    def test_process_events_fail_raises_error(self, lib_mock):
        lib_mock.sp_session_process_events.return_value = (
            spotify.ErrorType.BAD_API_VERSION
        )
        session = tests.create_real_session(lib_mock)

        with self.assertRaises(spotify.Error):
            session.process_events()

    @mock.patch("spotify.InboxPostResult", spec=spotify.InboxPostResult)
    def test_inbox_post_tracks(self, inbox_mock, lib_mock):
        session = tests.create_real_session(lib_mock)
        inbox_instance_mock = inbox_mock.return_value

        result = session.inbox_post_tracks(
            mock.sentinel.username,
            mock.sentinel.tracks,
            mock.sentinel.message,
            mock.sentinel.callback,
        )

        inbox_mock.assert_called_with(
            session,
            mock.sentinel.username,
            mock.sentinel.tracks,
            mock.sentinel.message,
            mock.sentinel.callback,
        )
        self.assertEqual(result, inbox_instance_mock)

    @mock.patch("spotify.playlist.lib", spec=spotify.lib)
    def test_get_starred(self, playlist_lib_mock, lib_mock):
        lib_mock.sp_session_starred_for_user_create.return_value = spotify.ffi.cast(
            "sp_playlist *", 42
        )
        session = tests.create_real_session(lib_mock)

        with pytest.warns(
            UserWarning, match="Spotify broke the libspotify playlists API"
        ):
            result = session.get_starred("alice")

        lib_mock.sp_session_starred_for_user_create.assert_called_with(
            session._sp_session, b"alice"
        )
        self.assertIsInstance(result, spotify.Playlist)

        # Since we *created* the sp_playlist, we already have a refcount of 1
        # and shouldn't increase the refcount when wrapping this sp_playlist in
        # a Playlist object
        self.assertEqual(playlist_lib_mock.sp_playlist_add_ref.call_count, 0)

    @mock.patch("spotify.playlist.lib", spec=spotify.lib)
    def test_get_starred_for_current_user(self, playlist_lib_mock, lib_mock):
        lib_mock.sp_session_starred_create.return_value = spotify.ffi.cast(
            "sp_playlist *", 42
        )
        session = tests.create_real_session(lib_mock)

        with pytest.warns(
            UserWarning, match="Spotify broke the libspotify playlists API"
        ):
            result = session.get_starred()

        lib_mock.sp_session_starred_create.assert_called_with(session._sp_session)
        self.assertIsInstance(result, spotify.Playlist)

        # Since we *created* the sp_playlist, we already have a refcount of 1
        # and shouldn't increase the refcount when wrapping this sp_playlist in
        # a Playlist object
        self.assertEqual(playlist_lib_mock.sp_playlist_add_ref.call_count, 0)

    def test_get_starred_if_not_logged_in(self, lib_mock):
        lib_mock.sp_session_starred_for_user_create.return_value = spotify.ffi.NULL
        session = tests.create_real_session(lib_mock)

        with pytest.warns(
            UserWarning, match="Spotify broke the libspotify playlists API"
        ):
            result = session.get_starred("alice")

        lib_mock.sp_session_starred_for_user_create.assert_called_with(
            session._sp_session, b"alice"
        )
        self.assertIsNone(result)

    @mock.patch("spotify.playlist_container.lib", spec=spotify.lib)
    def test_get_published_playlists(self, playlist_lib_mock, lib_mock):
        func_mock = lib_mock.sp_session_publishedcontainer_for_user_create
        func_mock.return_value = spotify.ffi.cast("sp_playlistcontainer *", 42)
        session = tests.create_real_session(lib_mock)

        with pytest.warns(
            UserWarning, match="Spotify broke the libspotify playlists API"
        ):
            result = session.get_published_playlists("alice")

        func_mock.assert_called_with(session._sp_session, b"alice")
        self.assertIsInstance(result, spotify.PlaylistContainer)

        # Since we *created* the sp_playlistcontainer, we already have a
        # refcount of 1 and shouldn't increase the refcount when wrapping this
        # sp_playlistcontainer in a PlaylistContainer object
        self.assertEqual(playlist_lib_mock.sp_playlistcontainer_add_ref.call_count, 0)

    @mock.patch("spotify.playlist_container.lib", spec=spotify.lib)
    def test_get_published_playlists_for_current_user(
        self, playlist_lib_mock, lib_mock
    ):
        func_mock = lib_mock.sp_session_publishedcontainer_for_user_create
        func_mock.return_value = spotify.ffi.cast("sp_playlistcontainer *", 42)
        session = tests.create_real_session(lib_mock)

        with pytest.warns(
            UserWarning, match="Spotify broke the libspotify playlists API"
        ):
            result = session.get_published_playlists()

        func_mock.assert_called_with(session._sp_session, spotify.ffi.NULL)
        self.assertIsInstance(result, spotify.PlaylistContainer)

    def test_get_published_playlists_if_not_logged_in(self, lib_mock):
        func_mock = lib_mock.sp_session_publishedcontainer_for_user_create
        func_mock.return_value = spotify.ffi.NULL
        session = tests.create_real_session(lib_mock)

        with pytest.warns(
            UserWarning, match="Spotify broke the libspotify playlists API"
        ):
            result = session.get_published_playlists("alice")

        func_mock.assert_called_with(session._sp_session, b"alice")
        self.assertIsNone(result)

    @mock.patch("spotify.Link")
    def test_get_link(self, link_mock, lib_mock):
        session = tests.create_real_session(lib_mock)
        link_mock.return_value = mock.sentinel.link

        result = session.get_link("spotify:any:foo")

        self.assertIs(result, mock.sentinel.link)
        link_mock.assert_called_with(session, uri="spotify:any:foo")

    @mock.patch("spotify.Track")
    def test_get_track(self, track_mock, lib_mock):
        session = tests.create_real_session(lib_mock)
        track_mock.return_value = mock.sentinel.track

        result = session.get_track("spotify:track:foo")

        self.assertIs(result, mock.sentinel.track)
        track_mock.assert_called_with(session, uri="spotify:track:foo")

    @mock.patch("spotify.Track")
    def test_get_local_track(self, track_mock, lib_mock):
        session = tests.create_real_session(lib_mock)
        sp_track = spotify.ffi.cast("sp_track *", 42)
        lib_mock.sp_localtrack_create.return_value = sp_track
        track_mock.return_value = mock.sentinel.track

        track = session.get_local_track(
            artist="foo", title="bar", album="baz", length=210000
        )

        self.assertEqual(track, mock.sentinel.track)
        lib_mock.sp_localtrack_create.assert_called_once_with(
            mock.ANY, mock.ANY, mock.ANY, 210000
        )
        self.assertEqual(
            spotify.ffi.string(lib_mock.sp_localtrack_create.call_args[0][0]),
            b"foo",
        )
        self.assertEqual(
            spotify.ffi.string(lib_mock.sp_localtrack_create.call_args[0][1]),
            b"bar",
        )
        self.assertEqual(
            spotify.ffi.string(lib_mock.sp_localtrack_create.call_args[0][2]),
            b"baz",
        )
        self.assertEqual(lib_mock.sp_localtrack_create.call_args[0][3], 210000)

        # Since we *created* the sp_track, we already have a refcount of 1 and
        # shouldn't increase the refcount when wrapping this sp_track in a
        # Track object
        track_mock.assert_called_with(session, sp_track=sp_track, add_ref=False)

    @mock.patch("spotify.Track")
    def test_get_local_track_with_defaults(self, track_mock, lib_mock):
        session = tests.create_real_session(lib_mock)
        sp_track = spotify.ffi.cast("sp_track *", 42)
        lib_mock.sp_localtrack_create.return_value = sp_track
        track_mock.return_value = mock.sentinel.track

        track = session.get_local_track()

        self.assertEqual(track, mock.sentinel.track)
        lib_mock.sp_localtrack_create.assert_called_once_with(
            mock.ANY, mock.ANY, mock.ANY, -1
        )
        self.assertEqual(
            spotify.ffi.string(lib_mock.sp_localtrack_create.call_args[0][0]),
            b"",
        )
        self.assertEqual(
            spotify.ffi.string(lib_mock.sp_localtrack_create.call_args[0][1]),
            b"",
        )
        self.assertEqual(
            spotify.ffi.string(lib_mock.sp_localtrack_create.call_args[0][2]),
            b"",
        )
        self.assertEqual(lib_mock.sp_localtrack_create.call_args[0][3], -1)

        # Since we *created* the sp_track, we already have a refcount of 1 and
        # shouldn't increase the refcount when wrapping this sp_track in a
        # Track object
        track_mock.assert_called_with(session, sp_track=sp_track, add_ref=False)

    @mock.patch("spotify.Album")
    def test_get_album(self, album_mock, lib_mock):
        session = tests.create_real_session(lib_mock)
        album_mock.return_value = mock.sentinel.album

        result = session.get_album("spotify:album:foo")

        self.assertIs(result, mock.sentinel.album)
        album_mock.assert_called_with(session, uri="spotify:album:foo")

    @mock.patch("spotify.Artist")
    def test_get_artist(self, artist_mock, lib_mock):
        session = tests.create_real_session(lib_mock)
        artist_mock.return_value = mock.sentinel.artist

        result = session.get_artist("spotify:artist:foo")

        self.assertIs(result, mock.sentinel.artist)
        artist_mock.assert_called_with(session, uri="spotify:artist:foo")

    @mock.patch("spotify.Playlist")
    def test_get_playlist(self, playlist_mock, lib_mock):
        session = tests.create_real_session(lib_mock)
        playlist_mock.return_value = mock.sentinel.playlist

        with pytest.warns(
            UserWarning, match="Spotify broke the libspotify playlists API"
        ):
            result = session.get_playlist("spotify:playlist:foo")

        self.assertIs(result, mock.sentinel.playlist)
        playlist_mock.assert_called_with(session, uri="spotify:playlist:foo")

    @mock.patch("spotify.User")
    def test_get_user(self, user_mock, lib_mock):
        session = tests.create_real_session(lib_mock)
        user_mock.return_value = mock.sentinel.user

        result = session.get_user("spotify:user:foo")

        self.assertIs(result, mock.sentinel.user)
        user_mock.assert_called_with(session, uri="spotify:user:foo")

    @mock.patch("spotify.Image")
    def test_get_image(self, image_mock, lib_mock):
        session = tests.create_real_session(lib_mock)
        callback = mock.Mock()
        image_mock.return_value = mock.sentinel.image

        result = session.get_image("spotify:image:foo", callback=callback)

        self.assertIs(result, mock.sentinel.image)
        image_mock.assert_called_with(
            session, uri="spotify:image:foo", callback=callback
        )

    @mock.patch("spotify.Search")
    def test_search(self, search_mock, lib_mock):
        session = tests.create_real_session(lib_mock)

        with self.assertRaises(Exception):  # noqa
            session.search("alice")

        self.assertEqual(search_mock.call_count, 0)

    @mock.patch("spotify.Toplist")
    def test_toplist(self, toplist_mock, lib_mock):
        session = tests.create_real_session(lib_mock)
        toplist_mock.return_value = mock.sentinel.toplist

        result = session.get_toplist(type=spotify.ToplistType.TRACKS, region="NO")

        self.assertIs(result, mock.sentinel.toplist)
        toplist_mock.assert_called_with(
            session,
            type=spotify.ToplistType.TRACKS,
            region="NO",
            canonical_username=None,
            callback=None,
        )


@mock.patch("spotify.session.lib", spec=spotify.lib)
class SessionCallbacksTest(unittest.TestCase):
    def tearDown(self):
        spotify._session_instance = None

    def test_logged_in_callback(self, lib_mock):
        callback = mock.Mock()
        session = tests.create_real_session(lib_mock)
        session.on(spotify.SessionEvent.LOGGED_IN, callback)

        _SessionCallbacks.logged_in(
            session._sp_session, int(spotify.ErrorType.BAD_API_VERSION)
        )

        callback.assert_called_once_with(session, spotify.ErrorType.BAD_API_VERSION)

    def test_logged_out_callback(self, lib_mock):
        callback = mock.Mock()
        session = tests.create_real_session(lib_mock)
        session.on(spotify.SessionEvent.LOGGED_OUT, callback)

        _SessionCallbacks.logged_out(session._sp_session)

        callback.assert_called_once_with(session)

    def test_metadata_updated_callback(self, lib_mock):
        callback = mock.Mock()
        session = tests.create_real_session(lib_mock)
        session.on(spotify.SessionEvent.METADATA_UPDATED, callback)

        _SessionCallbacks.metadata_updated(session._sp_session)

        callback.assert_called_once_with(session)

    def test_connection_error_callback(self, lib_mock):
        callback = mock.Mock()
        session = tests.create_real_session(lib_mock)
        session.on(spotify.SessionEvent.CONNECTION_ERROR, callback)

        _SessionCallbacks.connection_error(
            session._sp_session, int(spotify.ErrorType.OK)
        )

        callback.assert_called_once_with(session, spotify.ErrorType.OK)

    def test_message_to_user_callback(self, lib_mock):
        callback = mock.Mock()
        session = tests.create_real_session(lib_mock)
        session.on(spotify.SessionEvent.MESSAGE_TO_USER, callback)
        data = spotify.ffi.new("char[]", b"a log message\n")

        _SessionCallbacks.message_to_user(session._sp_session, data)

        callback.assert_called_once_with(session, "a log message")

    def test_notify_main_thread_callback(self, lib_mock):
        callback = mock.Mock()
        session = tests.create_real_session(lib_mock)
        session.on(spotify.SessionEvent.NOTIFY_MAIN_THREAD, callback)

        _SessionCallbacks.notify_main_thread(session._sp_session)

        callback.assert_called_once_with(session)

    def test_music_delivery_callback(self, lib_mock):
        sp_audioformat = spotify.ffi.new("sp_audioformat *")
        sp_audioformat.channels = 2
        audio_format = spotify.AudioFormat(sp_audioformat)

        num_frames = 10
        frames_size = audio_format.frame_size() * num_frames
        frames = spotify.ffi.new("char[]", frames_size)
        frames[0:3] = [b"a", b"b", b"c"]
        frames_void_ptr = spotify.ffi.cast("void *", frames)

        callback = mock.Mock()
        callback.return_value = num_frames
        session = tests.create_real_session(lib_mock)
        session.on("music_delivery", callback)

        result = _SessionCallbacks.music_delivery(
            session._sp_session, sp_audioformat, frames_void_ptr, num_frames
        )

        callback.assert_called_once_with(session, mock.ANY, mock.ANY, num_frames)
        self.assertEqual(callback.call_args[0][1]._sp_audioformat, sp_audioformat)
        self.assertEqual(callback.call_args[0][2][:5], b"abc\x00\x00")
        self.assertEqual(result, num_frames)

    def test_music_delivery_without_callback_does_not_consume(self, lib_mock):
        session = tests.create_real_session(lib_mock)

        sp_audioformat = spotify.ffi.new("sp_audioformat *")
        num_frames = 10
        frames = spotify.ffi.new("char[]", 0)
        frames_void_ptr = spotify.ffi.cast("void *", frames)

        result = _SessionCallbacks.music_delivery(
            session._sp_session, sp_audioformat, frames_void_ptr, num_frames
        )

        self.assertEqual(result, 0)

    def test_play_token_lost_callback(self, lib_mock):
        callback = mock.Mock()
        session = tests.create_real_session(lib_mock)
        session.on(spotify.SessionEvent.PLAY_TOKEN_LOST, callback)

        _SessionCallbacks.play_token_lost(session._sp_session)

        callback.assert_called_once_with(session)

    def test_log_message_callback(self, lib_mock):
        callback = mock.Mock()
        session = tests.create_real_session(lib_mock)
        session.on(spotify.SessionEvent.LOG_MESSAGE, callback)
        data = spotify.ffi.new("char[]", b"a log message\n")

        _SessionCallbacks.log_message(session._sp_session, data)

        callback.assert_called_once_with(session, "a log message")

    def test_end_of_track_callback(self, lib_mock):
        callback = mock.Mock()
        session = tests.create_real_session(lib_mock)
        session.on(spotify.SessionEvent.END_OF_TRACK, callback)

        _SessionCallbacks.end_of_track(session._sp_session)

        callback.assert_called_once_with(session)

    def test_streaming_error_callback(self, lib_mock):
        callback = mock.Mock()
        session = tests.create_real_session(lib_mock)
        session.on(spotify.SessionEvent.STREAMING_ERROR, callback)

        _SessionCallbacks.streaming_error(
            session._sp_session, int(spotify.ErrorType.NO_STREAM_AVAILABLE)
        )

        callback.assert_called_once_with(session, spotify.ErrorType.NO_STREAM_AVAILABLE)

    def test_user_info_updated_callback(self, lib_mock):
        callback = mock.Mock()
        session = tests.create_real_session(lib_mock)
        session.on(spotify.SessionEvent.USER_INFO_UPDATED, callback)

        _SessionCallbacks.user_info_updated(session._sp_session)

        callback.assert_called_once_with(session)

    def test_start_playback_callback(self, lib_mock):
        callback = mock.Mock()
        session = tests.create_real_session(lib_mock)
        session.on(spotify.SessionEvent.START_PLAYBACK, callback)

        _SessionCallbacks.start_playback(session._sp_session)

        callback.assert_called_once_with(session)

    def test_stop_playback_callback(self, lib_mock):
        callback = mock.Mock()
        session = tests.create_real_session(lib_mock)
        session.on(spotify.SessionEvent.STOP_PLAYBACK, callback)

        _SessionCallbacks.stop_playback(session._sp_session)

        callback.assert_called_once_with(session)

    def test_get_audio_buffer_stats_callback(self, lib_mock):
        callback = mock.Mock()
        callback.return_value = spotify.AudioBufferStats(100, 5)
        session = tests.create_real_session(lib_mock)
        session.on(spotify.SessionEvent.GET_AUDIO_BUFFER_STATS, callback)
        sp_audio_buffer_stats = spotify.ffi.new("sp_audio_buffer_stats *")

        _SessionCallbacks.get_audio_buffer_stats(
            session._sp_session, sp_audio_buffer_stats
        )

        callback.assert_called_once_with(session)
        self.assertEqual(sp_audio_buffer_stats.samples, 100)
        self.assertEqual(sp_audio_buffer_stats.stutter, 5)

    def test_offline_status_updated_callback(self, lib_mock):
        callback = mock.Mock()
        session = tests.create_real_session(lib_mock)
        session.on(spotify.SessionEvent.OFFLINE_STATUS_UPDATED, callback)

        _SessionCallbacks.offline_status_updated(session._sp_session)

        callback.assert_called_once_with(session)

    def test_credentials_blob_updated_callback(self, lib_mock):
        callback = mock.Mock()
        session = tests.create_real_session(lib_mock)
        session.on(spotify.SessionEvent.CREDENTIALS_BLOB_UPDATED, callback)
        data = spotify.ffi.new("char[]", b"a credentials blob")

        _SessionCallbacks.credentials_blob_updated(session._sp_session, data)

        callback.assert_called_once_with(session, b"a credentials blob")

    def test_connection_state_updated_callback(self, lib_mock):
        callback = mock.Mock()
        session = tests.create_real_session(lib_mock)
        session.on(spotify.SessionEvent.CONNECTION_STATE_UPDATED, callback)

        _SessionCallbacks.connection_state_updated(session._sp_session)

        callback.assert_called_once_with(session)

    def test_scrobble_error_callback(self, lib_mock):
        callback = mock.Mock()
        session = tests.create_real_session(lib_mock)
        session.on(spotify.SessionEvent.SCROBBLE_ERROR, callback)

        _SessionCallbacks.scrobble_error(
            session._sp_session, int(spotify.ErrorType.LASTFM_AUTH_ERROR)
        )

        callback.assert_called_once_with(session, spotify.ErrorType.LASTFM_AUTH_ERROR)

    def test_private_session_mode_changed_callback(self, lib_mock):
        callback = mock.Mock()
        session = tests.create_real_session(lib_mock)
        session.on(spotify.SessionEvent.PRIVATE_SESSION_MODE_CHANGED, callback)

        _SessionCallbacks.private_session_mode_changed(session._sp_session, 1)

        callback.assert_called_once_with(session, True)
