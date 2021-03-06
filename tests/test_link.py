from __future__ import unicode_literals

import unittest

import spotify
import tests
from tests import mock


@mock.patch("spotify.link.lib", spec=spotify.lib)
class LinkTest(unittest.TestCase):
    def setUp(self):
        self.session = tests.create_session_mock()

    def test_create_without_uri_or_obj_or_sp_link_fails(self, lib_mock):
        with self.assertRaises(AssertionError):
            spotify.Link(self.session)

    def test_create_from_sp_link(self, lib_mock):
        sp_link = spotify.ffi.cast("sp_link *", 42)

        result = spotify.Link(self.session, sp_link=sp_link)

        self.assertEqual(result._sp_link, sp_link)

    def test_create_from_uri(self, lib_mock):
        sp_link = spotify.ffi.cast("sp_link *", 42)
        lib_mock.sp_link_create_from_string.return_value = sp_link

        spotify.Link(self.session, "spotify:track:foo")

        lib_mock.sp_link_create_from_string.assert_called_once_with(mock.ANY)
        self.assertEqual(
            spotify.ffi.string(lib_mock.sp_link_create_from_string.call_args[0][0]),
            b"spotify:track:foo",
        )
        self.assertEqual(lib_mock.sp_link_add_ref.call_count, 0)

    def test_create_from_open_spotify_com_url(self, lib_mock):
        sp_link = spotify.ffi.cast("sp_link *", 42)
        lib_mock.sp_link_create_from_string.return_value = sp_link

        spotify.Link(self.session, "http://open.spotify.com/track/bar ")

        lib_mock.sp_link_create_from_string.assert_called_once_with(mock.ANY)
        self.assertEqual(
            spotify.ffi.string(lib_mock.sp_link_create_from_string.call_args[0][0]),
            b"spotify:track:bar",
        )

    def test_create_from_play_spotify_com_url(self, lib_mock):
        sp_link = spotify.ffi.cast("sp_link *", 42)
        lib_mock.sp_link_create_from_string.return_value = sp_link

        spotify.Link(self.session, "https://play.spotify.com/track/bar?gurba=123")

        lib_mock.sp_link_create_from_string.assert_called_once_with(mock.ANY)
        self.assertEqual(
            spotify.ffi.string(lib_mock.sp_link_create_from_string.call_args[0][0]),
            b"spotify:track:bar",
        )

    def test_raises_error_if_string_isnt_parseable(self, lib_mock):
        lib_mock.sp_link_create_from_string.return_value = spotify.ffi.NULL

        with self.assertRaises(ValueError):
            spotify.Link(self.session, "invalid link string")

    def test_releases_sp_link_when_link_dies(self, lib_mock):
        sp_link = spotify.ffi.cast("sp_link *", 42)
        lib_mock.sp_link_create_from_string.return_value = sp_link

        link = spotify.Link(self.session, "spotify:track:foo")
        link = None  # noqa
        tests.gc_collect()

        lib_mock.sp_link_release.assert_called_with(sp_link)

    def test_repr(self, lib_mock):
        sp_link = spotify.ffi.cast("sp_link *", 42)
        lib_mock.sp_link_create_from_string.return_value = sp_link
        string = "foo"

        lib_mock.sp_link_as_string.side_effect = tests.buffer_writer(string)
        link = spotify.Link(self.session, string)

        result = repr(link)

        self.assertEqual(result, "Link(%r)" % string)

    def test_str(self, lib_mock):
        sp_link = spotify.ffi.cast("sp_link *", 42)
        lib_mock.sp_link_create_from_string.return_value = sp_link
        string = "foo"

        lib_mock.sp_link_as_string.side_effect = tests.buffer_writer(string)
        link = spotify.Link(self.session, string)

        self.assertEqual(str(link), link.uri)

    def test_eq(self, lib_mock):
        sp_link = spotify.ffi.cast("sp_link *", 42)
        link1 = spotify.Link(self.session, sp_link=sp_link)
        link2 = spotify.Link(self.session, sp_link=sp_link)

        self.assertTrue(link1 == link2)
        self.assertFalse(link1 == "foo")

    def test_ne(self, lib_mock):
        sp_link = spotify.ffi.cast("sp_link *", 42)
        link1 = spotify.Link(self.session, sp_link=sp_link)
        link2 = spotify.Link(self.session, sp_link=sp_link)

        self.assertFalse(link1 != link2)

    def test_hash(self, lib_mock):
        sp_link = spotify.ffi.cast("sp_link *", 42)
        link1 = spotify.Link(self.session, sp_link=sp_link)
        link2 = spotify.Link(self.session, sp_link=sp_link)

        self.assertEqual(hash(link1), hash(link2))

    def test_uri_grows_buffer_to_fit_link(self, lib_mock):
        sp_link = spotify.ffi.cast("sp_link *", 42)
        lib_mock.sp_link_create_from_string.return_value = sp_link
        string = "foo" * 100

        lib_mock.sp_link_as_string.side_effect = tests.buffer_writer(string)
        link = spotify.Link(self.session, string)

        result = link.uri

        lib_mock.sp_link_as_string.assert_called_with(sp_link, mock.ANY, mock.ANY)
        self.assertEqual(result, string)

    def test_url_expands_uri_to_http_url(self, lib_mock):
        sp_link = spotify.ffi.cast("sp_link *", 42)
        lib_mock.sp_link_create_from_string.return_value = sp_link
        string = "spotify:track:foo"
        lib_mock.sp_link_as_string.side_effect = tests.buffer_writer(string)
        link = spotify.Link(self.session, string)

        result = link.url

        self.assertEqual(result, "https://open.spotify.com/track/foo")

    def test_type(self, lib_mock):
        sp_link = spotify.ffi.cast("sp_link *", 42)
        lib_mock.sp_link_create_from_string.return_value = sp_link
        lib_mock.sp_link_type.return_value = 1
        link = spotify.Link(self.session, "spotify:track:foo")

        self.assertIs(link.type, spotify.LinkType.TRACK)

        lib_mock.sp_link_type.assert_called_once_with(sp_link)

    @mock.patch("spotify.track.lib", spec=spotify.lib)
    def test_as_track(self, track_lib_mock, lib_mock):
        sp_link = spotify.ffi.cast("sp_link *", 42)
        lib_mock.sp_link_create_from_string.return_value = sp_link
        sp_track = spotify.ffi.cast("sp_track *", 43)
        lib_mock.sp_link_as_track.return_value = sp_track

        link = spotify.Link(self.session, "spotify:track:foo")
        self.assertEqual(link.as_track()._sp_track, sp_track)

        lib_mock.sp_link_as_track.assert_called_once_with(sp_link)

    @mock.patch("spotify.track.lib", spec=spotify.lib)
    def test_as_track_if_not_a_track(self, track_lib_mock, lib_mock):
        sp_link = spotify.ffi.cast("sp_link *", 42)
        lib_mock.sp_link_create_from_string.return_value = sp_link
        lib_mock.sp_link_as_track.return_value = spotify.ffi.NULL

        link = spotify.Link(self.session, "spotify:track:foo")
        self.assertIsNone(link.as_track())

        lib_mock.sp_link_as_track.assert_called_once_with(sp_link)

    @mock.patch("spotify.track.lib", spec=spotify.lib)
    def test_as_track_with_offset(self, track_lib_mock, lib_mock):
        sp_link = spotify.ffi.cast("sp_link *", 42)
        lib_mock.sp_link_create_from_string.return_value = sp_link
        sp_track = spotify.ffi.cast("sp_track *", 43)

        def func(sp_link, offset_ptr):
            offset_ptr[0] = 90
            return sp_track

        lib_mock.sp_link_as_track_and_offset.side_effect = func

        link = spotify.Link(self.session, "spotify:track:foo")
        offset = link.as_track_offset()

        self.assertEqual(offset, 90)
        lib_mock.sp_link_as_track_and_offset.assert_called_once_with(sp_link, mock.ANY)

    @mock.patch("spotify.track.lib", spec=spotify.lib)
    def test_as_track_with_offset_if_not_a_track(self, track_lib_mock, lib_mock):
        sp_link = spotify.ffi.cast("sp_link *", 42)
        lib_mock.sp_link_create_from_string.return_value = sp_link
        lib_mock.sp_link_as_track_and_offset.return_value = spotify.ffi.NULL

        link = spotify.Link(self.session, "spotify:track:foo")
        offset = link.as_track_offset()

        self.assertIsNone(offset)
        lib_mock.sp_link_as_track_and_offset.assert_called_once_with(sp_link, mock.ANY)

    @mock.patch("spotify.album.lib", spec=spotify.lib)
    def test_as_album(self, album_lib_mock, lib_mock):
        sp_link = spotify.ffi.cast("sp_link *", 42)
        lib_mock.sp_link_create_from_string.return_value = sp_link
        sp_album = spotify.ffi.cast("sp_album *", 43)
        lib_mock.sp_link_as_album.return_value = sp_album

        link = spotify.Link(self.session, "spotify:album:foo")
        self.assertEqual(link.as_album()._sp_album, sp_album)

        lib_mock.sp_link_as_album.assert_called_once_with(sp_link)

    @mock.patch("spotify.album.lib", spec=spotify.lib)
    def test_as_album_if_not_an_album(self, album_lib_mock, lib_mock):
        sp_link = spotify.ffi.cast("sp_link *", 42)
        lib_mock.sp_link_create_from_string.return_value = sp_link
        lib_mock.sp_link_as_album.return_value = spotify.ffi.NULL

        link = spotify.Link(self.session, "spotify:album:foo")
        self.assertIsNone(link.as_album())

        lib_mock.sp_link_as_album.assert_called_once_with(sp_link)

    @mock.patch("spotify.artist.lib", spec=spotify.lib)
    def test_as_artist(self, artist_lib_mock, lib_mock):
        sp_link = spotify.ffi.cast("sp_link *", 42)
        lib_mock.sp_link_create_from_string.return_value = sp_link
        sp_artist = spotify.ffi.cast("sp_artist *", 43)
        lib_mock.sp_link_as_artist.return_value = sp_artist

        link = spotify.Link(self.session, "spotify:artist:foo")
        self.assertEqual(link.as_artist()._sp_artist, sp_artist)

        lib_mock.sp_link_as_artist.assert_called_once_with(sp_link)

    @mock.patch("spotify.artist.lib", spec=spotify.lib)
    def test_as_artist_if_not_an_artist(self, artist_lib_mock, lib_mock):
        sp_link = spotify.ffi.cast("sp_link *", 42)
        lib_mock.sp_link_create_from_string.return_value = sp_link
        lib_mock.sp_link_as_artist.return_value = spotify.ffi.NULL

        link = spotify.Link(self.session, "spotify:artist:foo")
        self.assertIsNone(link.as_artist())

        lib_mock.sp_link_as_artist.assert_called_once_with(sp_link)

    @mock.patch("spotify.playlist.lib", spec=spotify.lib)
    def test_as_playlist(self, playlist_lib_mock, lib_mock):
        sp_link = spotify.ffi.cast("sp_link *", 42)
        lib_mock.sp_link_create_from_string.return_value = sp_link
        lib_mock.sp_link_type.return_value = spotify.LinkType.PLAYLIST
        sp_playlist = spotify.ffi.cast("sp_playlist *", 43)
        lib_mock.sp_playlist_create.return_value = sp_playlist

        link = spotify.Link(self.session, "spotify:playlist:foo")
        self.assertEqual(link.as_playlist()._sp_playlist, sp_playlist)

        lib_mock.sp_playlist_create.assert_called_once_with(
            self.session._sp_session, sp_link
        )

        # Since we *created* the sp_playlist, we already have a refcount of 1
        # and shouldn't increase the refcount when wrapping this sp_playlist in
        # an Playlist object
        self.assertEqual(playlist_lib_mock.sp_playlist_add_ref.call_count, 0)

    @mock.patch("spotify.playlist.lib", spec=spotify.lib)
    def test_as_playlist_if_starred(self, playlist_lib_mock, lib_mock):
        uri = "spotify:user:alice:starred"
        sp_link = spotify.ffi.cast("sp_link *", 42)
        lib_mock.sp_link_create_from_string.return_value = sp_link
        lib_mock.sp_link_type.return_value = spotify.LinkType.STARRED
        lib_mock.sp_link_as_string.side_effect = tests.buffer_writer(uri)
        sp_playlist = spotify.ffi.cast("sp_playlist *", 43)
        lib_mock.sp_session_starred_for_user_create.return_value = sp_playlist

        link = spotify.Link(self.session, uri)
        self.assertEqual(link.as_playlist()._sp_playlist, sp_playlist)

        lib_mock.sp_session_starred_for_user_create.assert_called_once_with(
            self.session._sp_session, b"alice"
        )

    @mock.patch("spotify.playlist.lib", spec=spotify.lib)
    def test_as_playlist_if_not_a_playlist(self, playlist_lib_mock, lib_mock):
        sp_link = spotify.ffi.cast("sp_link *", 42)
        lib_mock.sp_link_create_from_string.return_value = sp_link
        lib_mock.sp_link_type.return_value = spotify.LinkType.ARTIST

        link = spotify.Link(self.session, "spotify:playlist:foo")
        self.assertIsNone(link.as_playlist())

        self.assertEqual(lib_mock.sp_playlist_create.call_count, 0)

    @mock.patch("spotify.user.lib", spec=spotify.lib)
    def test_as_user(self, user_lib_mock, lib_mock):
        sp_link = spotify.ffi.cast("sp_link *", 42)
        lib_mock.sp_link_create_from_string.return_value = sp_link
        sp_user = spotify.ffi.cast("sp_user *", 43)
        lib_mock.sp_link_as_user.return_value = sp_user

        link = spotify.Link(self.session, "spotify:user:foo")
        self.assertEqual(link.as_user()._sp_user, sp_user)

        lib_mock.sp_link_as_user.assert_called_once_with(sp_link)

    @mock.patch("spotify.user.lib", spec=spotify.lib)
    def test_as_user_if_not_a_user(self, user_lib_mock, lib_mock):
        sp_link = spotify.ffi.cast("sp_link *", 42)
        lib_mock.sp_link_create_from_string.return_value = sp_link
        lib_mock.sp_link_as_user.return_value = spotify.ffi.NULL

        link = spotify.Link(self.session, "spotify:user:foo")
        self.assertIsNone(link.as_user())

        lib_mock.sp_link_as_user.assert_called_once_with(sp_link)

    @mock.patch("spotify.Image", spec=spotify.Image)
    def test_as_image(self, image_mock, lib_mock):
        sp_link = spotify.ffi.cast("sp_link *", 42)
        lib_mock.sp_link_create_from_string.return_value = sp_link
        lib_mock.sp_link_type.return_value = spotify.LinkType.IMAGE
        sp_image = spotify.ffi.cast("sp_image *", 43)
        lib_mock.sp_image_create_from_link.return_value = sp_image
        image_mock.return_value = mock.sentinel.image
        callback = mock.Mock()

        link = spotify.Link(self.session, "spotify:image:foo")
        result = link.as_image(callback=callback)

        self.assertIs(result, mock.sentinel.image)
        lib_mock.sp_image_create_from_link.assert_called_once_with(
            self.session._sp_session, sp_link
        )

        # Since we *created* the sp_image, we already have a refcount of 1 and
        # shouldn't increase the refcount when wrapping this sp_image in an
        # Image object
        image_mock.assert_called_with(
            self.session, sp_image=sp_image, add_ref=False, callback=callback
        )

    def test_as_image_if_not_a_image(self, lib_mock):
        sp_link = spotify.ffi.cast("sp_link *", 42)
        lib_mock.sp_link_create_from_string.return_value = sp_link
        lib_mock.sp_link_type.return_value = spotify.LinkType.ARTIST

        link = spotify.Link(self.session, "spotify:image:foo")
        result = link.as_image()

        self.assertIsNone(result)
        self.assertEqual(lib_mock.sp_image_create_from_link.call_count, 0)


class LinkTypeTest(unittest.TestCase):
    def test_has_link_type_constants(self):
        self.assertEqual(spotify.LinkType.INVALID, 0)
        self.assertEqual(spotify.LinkType.TRACK, 1)
        self.assertEqual(spotify.LinkType.ALBUM, 2)
