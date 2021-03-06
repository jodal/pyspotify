from __future__ import unicode_literals

import unittest

import spotify
import tests
from spotify import compat
from tests import mock


@mock.patch("spotify.artist.lib", spec=spotify.lib)
class ArtistTest(unittest.TestCase):
    def setUp(self):
        self.session = tests.create_session_mock()

    def test_create_without_uri_or_sp_artist_fails(self, lib_mock):
        with self.assertRaises(AssertionError):
            spotify.Artist(self.session)

    @mock.patch("spotify.Link", spec=spotify.Link)
    def test_create_from_uri(self, link_mock, lib_mock):
        sp_artist = spotify.ffi.cast("sp_artist *", 42)
        link_instance_mock = link_mock.return_value
        link_instance_mock.as_artist.return_value = spotify.Artist(
            self.session, sp_artist=sp_artist
        )
        lib_mock.sp_link_as_artist.return_value = sp_artist
        uri = "spotify:artist:foo"

        result = spotify.Artist(self.session, uri=uri)

        link_mock.assert_called_with(self.session, uri=uri)
        link_instance_mock.as_artist.assert_called_with()
        lib_mock.sp_artist_add_ref.assert_called_with(sp_artist)
        self.assertEqual(result._sp_artist, sp_artist)

    @mock.patch("spotify.Link", spec=spotify.Link)
    def test_create_from_uri_fail_raises_error(self, link_mock, lib_mock):
        link_instance_mock = link_mock.return_value
        link_instance_mock.as_artist.return_value = None
        lib_mock.sp_link_as_artist.return_value = spotify.ffi.NULL
        uri = "spotify:artist:foo"

        with self.assertRaises(ValueError):
            spotify.Artist(self.session, uri=uri)

    def test_adds_ref_to_sp_artist_when_created(self, lib_mock):
        sp_artist = spotify.ffi.cast("sp_artist *", 42)

        spotify.Artist(self.session, sp_artist=sp_artist)

        lib_mock.sp_artist_add_ref.assert_called_with(sp_artist)

    def test_releases_sp_artist_when_artist_dies(self, lib_mock):
        sp_artist = spotify.ffi.cast("sp_artist *", 42)

        artist = spotify.Artist(self.session, sp_artist=sp_artist)
        artist = None  # noqa
        tests.gc_collect()

        lib_mock.sp_artist_release.assert_called_with(sp_artist)

    @mock.patch("spotify.Link", spec=spotify.Link)
    def test_repr(self, link_mock, lib_mock):
        link_instance_mock = link_mock.return_value
        link_instance_mock.uri = "foo"
        sp_artist = spotify.ffi.cast("sp_artist *", 42)
        artist = spotify.Artist(self.session, sp_artist=sp_artist)

        result = repr(artist)

        self.assertEqual(result, "Artist(%r)" % "foo")

    def test_eq(self, lib_mock):
        sp_artist = spotify.ffi.cast("sp_artist *", 42)
        artist1 = spotify.Artist(self.session, sp_artist=sp_artist)
        artist2 = spotify.Artist(self.session, sp_artist=sp_artist)

        self.assertTrue(artist1 == artist2)
        self.assertFalse(artist1 == "foo")

    def test_ne(self, lib_mock):
        sp_artist = spotify.ffi.cast("sp_artist *", 42)
        artist1 = spotify.Artist(self.session, sp_artist=sp_artist)
        artist2 = spotify.Artist(self.session, sp_artist=sp_artist)

        self.assertFalse(artist1 != artist2)

    def test_hash(self, lib_mock):
        sp_artist = spotify.ffi.cast("sp_artist *", 42)
        artist1 = spotify.Artist(self.session, sp_artist=sp_artist)
        artist2 = spotify.Artist(self.session, sp_artist=sp_artist)

        self.assertEqual(hash(artist1), hash(artist2))

    def test_name(self, lib_mock):
        lib_mock.sp_artist_name.return_value = spotify.ffi.new("char[]", b"Foo Bar Baz")
        sp_artist = spotify.ffi.cast("sp_artist *", 42)
        artist = spotify.Artist(self.session, sp_artist=sp_artist)

        result = artist.name

        lib_mock.sp_artist_name.assert_called_once_with(sp_artist)
        self.assertEqual(result, "Foo Bar Baz")

    def test_name_is_none_if_unloaded(self, lib_mock):
        lib_mock.sp_artist_name.return_value = spotify.ffi.new("char[]", b"")
        sp_artist = spotify.ffi.cast("sp_artist *", 42)
        artist = spotify.Artist(self.session, sp_artist=sp_artist)

        result = artist.name

        lib_mock.sp_artist_name.assert_called_once_with(sp_artist)
        self.assertIsNone(result)

    def test_is_loaded(self, lib_mock):
        lib_mock.sp_artist_is_loaded.return_value = 1
        sp_artist = spotify.ffi.cast("sp_artist *", 42)
        artist = spotify.Artist(self.session, sp_artist=sp_artist)

        result = artist.is_loaded

        lib_mock.sp_artist_is_loaded.assert_called_once_with(sp_artist)
        self.assertTrue(result)

    @mock.patch("spotify.utils.load")
    def test_load(self, load_mock, lib_mock):
        sp_artist = spotify.ffi.cast("sp_artist *", 42)
        artist = spotify.Artist(self.session, sp_artist=sp_artist)

        artist.load(10)

        load_mock.assert_called_with(self.session, artist, timeout=10)

    @mock.patch("spotify.Image", spec=spotify.Image)
    def test_portrait(self, image_mock, lib_mock):
        sp_artist = spotify.ffi.cast("sp_artist *", 42)
        artist = spotify.Artist(self.session, sp_artist=sp_artist)
        sp_image_id = spotify.ffi.new("char[]", b"portrait-id")
        lib_mock.sp_artist_portrait.return_value = sp_image_id
        sp_image = spotify.ffi.cast("sp_image *", 43)
        lib_mock.sp_image_create.return_value = sp_image
        image_mock.return_value = mock.sentinel.image
        image_size = spotify.ImageSize.SMALL
        callback = mock.Mock()

        result = artist.portrait(image_size, callback=callback)

        self.assertIs(result, mock.sentinel.image)
        lib_mock.sp_artist_portrait.assert_called_with(sp_artist, int(image_size))
        lib_mock.sp_image_create.assert_called_with(
            self.session._sp_session, sp_image_id
        )

        # Since we *created* the sp_image, we already have a refcount of 1 and
        # shouldn't increase the refcount when wrapping this sp_image in an
        # Image object
        image_mock.assert_called_with(
            self.session, sp_image=sp_image, add_ref=False, callback=callback
        )

    @mock.patch("spotify.Image", spec=spotify.Image)
    def test_portrait_defaults_to_normal_size(self, image_mock, lib_mock):
        sp_image_id = spotify.ffi.new("char[]", b"portrait-id")
        lib_mock.sp_artist_portrait.return_value = sp_image_id
        sp_image = spotify.ffi.cast("sp_image *", 43)
        lib_mock.sp_image_create.return_value = sp_image
        sp_artist = spotify.ffi.cast("sp_artist *", 42)
        artist = spotify.Artist(self.session, sp_artist=sp_artist)

        artist.portrait()

        lib_mock.sp_artist_portrait.assert_called_with(
            sp_artist, int(spotify.ImageSize.NORMAL)
        )

    def test_portrait_is_none_if_null(self, lib_mock):
        lib_mock.sp_artist_portrait.return_value = spotify.ffi.NULL
        sp_artist = spotify.ffi.cast("sp_artist *", 42)
        artist = spotify.Artist(self.session, sp_artist=sp_artist)

        result = artist.portrait()

        lib_mock.sp_artist_portrait.assert_called_with(
            sp_artist, int(spotify.ImageSize.NORMAL)
        )
        self.assertIsNone(result)

    @mock.patch("spotify.Link", spec=spotify.Link)
    def test_portrait_link_creates_link_to_portrait(self, link_mock, lib_mock):
        sp_artist = spotify.ffi.cast("sp_artist *", 42)
        artist = spotify.Artist(self.session, sp_artist=sp_artist)
        sp_link = spotify.ffi.cast("sp_link *", 43)
        lib_mock.sp_link_create_from_artist_portrait.return_value = sp_link
        link_mock.return_value = mock.sentinel.link
        image_size = spotify.ImageSize.SMALL

        result = artist.portrait_link(image_size)

        lib_mock.sp_link_create_from_artist_portrait.assert_called_once_with(
            sp_artist, int(image_size)
        )
        link_mock.assert_called_once_with(self.session, sp_link=sp_link, add_ref=False)
        self.assertEqual(result, mock.sentinel.link)

    @mock.patch("spotify.Link", spec=spotify.Link)
    def test_portrait_link_defaults_to_normal_size(self, link_mock, lib_mock):
        sp_artist = spotify.ffi.cast("sp_artist *", 42)
        artist = spotify.Artist(self.session, sp_artist=sp_artist)
        sp_link = spotify.ffi.cast("sp_link *", 43)
        lib_mock.sp_link_create_from_artist_portrait.return_value = sp_link
        link_mock.return_value = mock.sentinel.link

        artist.portrait_link()

        lib_mock.sp_link_create_from_artist_portrait.assert_called_once_with(
            sp_artist, int(spotify.ImageSize.NORMAL)
        )

    @mock.patch("spotify.Link", spec=spotify.Link)
    def test_link_creates_link_to_artist(self, link_mock, lib_mock):
        sp_artist = spotify.ffi.cast("sp_artist *", 42)
        artist = spotify.Artist(self.session, sp_artist=sp_artist)
        sp_link = spotify.ffi.cast("sp_link *", 43)
        lib_mock.sp_link_create_from_artist.return_value = sp_link
        link_mock.return_value = mock.sentinel.link

        result = artist.link

        link_mock.assert_called_once_with(self.session, sp_link=sp_link, add_ref=False)
        self.assertEqual(result, mock.sentinel.link)


@mock.patch("spotify.artist.lib", spec=spotify.lib)
class ArtistBrowserTest(unittest.TestCase):
    def setUp(self):
        self.session = tests.create_session_mock()
        spotify._session_instance = self.session

    def tearDown(self):
        spotify._session_instance = None

    def test_create_without_artist_or_sp_artistbrowse_fails(self, lib_mock):
        with self.assertRaises(AssertionError):
            spotify.ArtistBrowser(self.session)

    def test_create_from_artist(self, lib_mock):
        sp_artist = spotify.ffi.cast("sp_artist *", 43)
        artist = spotify.Artist(self.session, sp_artist=sp_artist)
        sp_artistbrowse = spotify.ffi.cast("sp_artistbrowse *", 42)
        lib_mock.sp_artistbrowse_create.return_value = sp_artistbrowse

        result = artist.browse()

        lib_mock.sp_artistbrowse_create.assert_called_with(
            self.session._sp_session,
            sp_artist,
            int(spotify.ArtistBrowserType.FULL),
            mock.ANY,
            mock.ANY,
        )
        self.assertIsInstance(result, spotify.ArtistBrowser)

        artistbrowse_complete_cb = lib_mock.sp_artistbrowse_create.call_args[0][3]
        userdata = lib_mock.sp_artistbrowse_create.call_args[0][4]
        self.assertFalse(result.loaded_event.is_set())
        artistbrowse_complete_cb(sp_artistbrowse, userdata)
        self.assertTrue(result.loaded_event.is_set())

    def test_create_from_artist_with_type_and_callback(self, lib_mock):
        sp_artist = spotify.ffi.cast("sp_artist *", 43)
        artist = spotify.Artist(self.session, sp_artist=sp_artist)
        sp_artistbrowse = spotify.ffi.cast("sp_artistbrowse *", 42)
        lib_mock.sp_artistbrowse_create.return_value = sp_artistbrowse
        callback = mock.Mock()

        result = artist.browse(
            type=spotify.ArtistBrowserType.NO_TRACKS, callback=callback
        )

        lib_mock.sp_artistbrowse_create.assert_called_with(
            self.session._sp_session,
            sp_artist,
            int(spotify.ArtistBrowserType.NO_TRACKS),
            mock.ANY,
            mock.ANY,
        )
        artistbrowse_complete_cb = lib_mock.sp_artistbrowse_create.call_args[0][3]
        userdata = lib_mock.sp_artistbrowse_create.call_args[0][4]
        artistbrowse_complete_cb(sp_artistbrowse, userdata)

        result.loaded_event.wait(3)
        callback.assert_called_with(result)

    def test_browser_is_gone_before_callback_is_called(self, lib_mock):
        sp_artist = spotify.ffi.cast("sp_artist *", 43)
        artist = spotify.Artist(self.session, sp_artist=sp_artist)
        sp_artistbrowse = spotify.ffi.cast("sp_artistbrowse *", 42)
        lib_mock.sp_artistbrowse_create.return_value = sp_artistbrowse
        callback = mock.Mock()

        result = spotify.ArtistBrowser(self.session, artist=artist, callback=callback)
        loaded_event = result.loaded_event
        result = None  # noqa
        tests.gc_collect()

        # The mock keeps the handle/userdata alive, thus this test doesn't
        # really test that session._callback_handles keeps the handle alive.
        artistbrowse_complete_cb = lib_mock.sp_artistbrowse_create.call_args[0][3]
        userdata = lib_mock.sp_artistbrowse_create.call_args[0][4]
        artistbrowse_complete_cb(sp_artistbrowse, userdata)

        loaded_event.wait(3)
        self.assertEqual(callback.call_count, 1)
        self.assertEqual(callback.call_args[0][0]._sp_artistbrowse, sp_artistbrowse)

    def test_adds_ref_to_sp_artistbrowse_when_created(self, lib_mock):
        sp_artistbrowse = spotify.ffi.cast("sp_artistbrowse *", 42)

        spotify.ArtistBrowser(self.session, sp_artistbrowse=sp_artistbrowse)

        lib_mock.sp_artistbrowse_add_ref.assert_called_with(sp_artistbrowse)

    def test_releases_sp_artistbrowse_when_artist_dies(self, lib_mock):
        sp_artistbrowse = spotify.ffi.cast("sp_artistbrowse *", 42)

        browser = spotify.ArtistBrowser(self.session, sp_artistbrowse=sp_artistbrowse)
        browser = None  # noqa
        tests.gc_collect()

        lib_mock.sp_artistbrowse_release.assert_called_with(sp_artistbrowse)

    @mock.patch("spotify.Link", spec=spotify.Link)
    def test_repr(self, link_mock, lib_mock):
        sp_artistbrowse = spotify.ffi.cast("sp_artistbrowse *", 42)
        browser = spotify.ArtistBrowser(self.session, sp_artistbrowse=sp_artistbrowse)
        lib_mock.sp_artistbrowse_is_loaded.return_value = 1
        sp_artist = spotify.ffi.cast("sp_artist *", 42)
        lib_mock.sp_artistbrowse_artist.return_value = sp_artist
        link_instance_mock = link_mock.return_value
        link_instance_mock.uri = "foo"

        result = repr(browser)

        self.assertEqual(result, "ArtistBrowser(%r)" % "foo")

    def test_repr_if_unloaded(self, lib_mock):
        sp_artistbrowse = spotify.ffi.cast("sp_artistbrowse *", 42)
        browser = spotify.ArtistBrowser(self.session, sp_artistbrowse=sp_artistbrowse)
        lib_mock.sp_artistbrowse_is_loaded.return_value = 0

        result = repr(browser)

        self.assertEqual(result, "ArtistBrowser(<not loaded>)")

    def test_eq(self, lib_mock):
        sp_artistbrowse = spotify.ffi.cast("sp_artistbrowse *", 42)
        browser1 = spotify.ArtistBrowser(self.session, sp_artistbrowse=sp_artistbrowse)
        browser2 = spotify.ArtistBrowser(self.session, sp_artistbrowse=sp_artistbrowse)

        self.assertTrue(browser1 == browser2)
        self.assertFalse(browser1 == "foo")

    def test_ne(self, lib_mock):
        sp_artistbrowse = spotify.ffi.cast("sp_artistbrowse *", 42)
        browser1 = spotify.ArtistBrowser(self.session, sp_artistbrowse=sp_artistbrowse)
        browser2 = spotify.ArtistBrowser(self.session, sp_artistbrowse=sp_artistbrowse)

        self.assertFalse(browser1 != browser2)

    def test_hash(self, lib_mock):
        sp_artistbrowse = spotify.ffi.cast("sp_artistbrowse *", 42)
        browser1 = spotify.ArtistBrowser(self.session, sp_artistbrowse=sp_artistbrowse)
        browser2 = spotify.ArtistBrowser(self.session, sp_artistbrowse=sp_artistbrowse)

        self.assertEqual(hash(browser1), hash(browser2))

    def test_is_loaded(self, lib_mock):
        lib_mock.sp_artistbrowse_is_loaded.return_value = 1
        sp_artistbrowse = spotify.ffi.cast("sp_artistbrowse *", 42)
        browser = spotify.ArtistBrowser(self.session, sp_artistbrowse=sp_artistbrowse)

        result = browser.is_loaded

        lib_mock.sp_artistbrowse_is_loaded.assert_called_once_with(sp_artistbrowse)
        self.assertTrue(result)

    @mock.patch("spotify.utils.load")
    def test_load(self, load_mock, lib_mock):
        sp_artistbrowse = spotify.ffi.cast("sp_artistbrowse *", 42)
        browser = spotify.ArtistBrowser(self.session, sp_artistbrowse=sp_artistbrowse)

        browser.load(10)

        load_mock.assert_called_with(self.session, browser, timeout=10)

    def test_error(self, lib_mock):
        lib_mock.sp_artistbrowse_error.return_value = int(
            spotify.ErrorType.OTHER_PERMANENT
        )
        sp_artistbrowse = spotify.ffi.cast("sp_artistbrowse *", 42)
        browser = spotify.ArtistBrowser(self.session, sp_artistbrowse=sp_artistbrowse)

        result = browser.error

        lib_mock.sp_artistbrowse_error.assert_called_once_with(sp_artistbrowse)
        self.assertIs(result, spotify.ErrorType.OTHER_PERMANENT)

    def test_backend_request_duration(self, lib_mock):
        lib_mock.sp_artistbrowse_backend_request_duration.return_value = 137
        sp_artistbrowse = spotify.ffi.cast("sp_artistbrowse *", 42)
        browser = spotify.ArtistBrowser(self.session, sp_artistbrowse=sp_artistbrowse)

        result = browser.backend_request_duration

        lib_mock.sp_artistbrowse_backend_request_duration.assert_called_with(
            sp_artistbrowse
        )
        self.assertEqual(result, 137)

    def test_backend_request_duration_when_not_loaded(self, lib_mock):
        lib_mock.sp_artistbrowse_is_loaded.return_value = 0
        sp_artistbrowse = spotify.ffi.cast("sp_artistbrowse *", 42)
        browser = spotify.ArtistBrowser(self.session, sp_artistbrowse=sp_artistbrowse)

        result = browser.backend_request_duration

        lib_mock.sp_artistbrowse_is_loaded.assert_called_with(sp_artistbrowse)
        self.assertEqual(
            lib_mock.sp_artistbrowse_backend_request_duration.call_count, 0
        )
        self.assertIsNone(result)

    def test_artist(self, lib_mock):
        sp_artistbrowse = spotify.ffi.cast("sp_artistbrowse *", 42)
        browser = spotify.ArtistBrowser(self.session, sp_artistbrowse=sp_artistbrowse)
        sp_artist = spotify.ffi.cast("sp_artist *", 43)
        lib_mock.sp_artistbrowse_artist.return_value = sp_artist

        result = browser.artist

        self.assertIsInstance(result, spotify.Artist)
        self.assertEqual(result._sp_artist, sp_artist)

    def test_artist_when_not_loaded(self, lib_mock):
        sp_artistbrowse = spotify.ffi.cast("sp_artistbrowse *", 42)
        browser = spotify.ArtistBrowser(self.session, sp_artistbrowse=sp_artistbrowse)
        lib_mock.sp_artistbrowse_artist.return_value = spotify.ffi.NULL

        result = browser.artist

        lib_mock.sp_artistbrowse_artist.assert_called_with(sp_artistbrowse)
        self.assertIsNone(result)

    @mock.patch("spotify.Image", spec=spotify.Image)
    def test_portraits(self, image_mock, lib_mock):
        sp_artistbrowse = spotify.ffi.cast("sp_artistbrowse *", 42)
        browser = spotify.ArtistBrowser(self.session, sp_artistbrowse=sp_artistbrowse)
        lib_mock.sp_artistbrowse_num_portraits.return_value = 1
        image_id = spotify.ffi.new("char[]", b"image-id")
        lib_mock.sp_artistbrowse_portrait.return_value = image_id
        sp_image = spotify.ffi.cast("sp_image *", 43)
        lib_mock.sp_image_create.return_value = sp_image
        image_mock.return_value = mock.sentinel.image
        callback = mock.Mock()

        self.assertEqual(lib_mock.sp_artistbrowse_add_ref.call_count, 1)
        result = browser.portraits(callback=callback)
        self.assertEqual(lib_mock.sp_artistbrowse_add_ref.call_count, 2)

        self.assertEqual(len(result), 1)
        lib_mock.sp_artistbrowse_num_portraits.assert_called_with(sp_artistbrowse)

        item = result[0]
        self.assertIs(item, mock.sentinel.image)
        self.assertEqual(lib_mock.sp_artistbrowse_portrait.call_count, 1)
        lib_mock.sp_artistbrowse_portrait.assert_called_with(sp_artistbrowse, 0)

        # Since we *created* the sp_image, we already have a refcount of 1 and
        # shouldn't increase the refcount when wrapping this sp_image in an
        # Image object
        image_mock.assert_called_with(
            self.session, sp_image=sp_image, add_ref=False, callback=callback
        )

    def test_portraits_if_no_portraits(self, lib_mock):
        lib_mock.sp_artistbrowse_num_portraits.return_value = 0
        sp_artistbrowse = spotify.ffi.cast("sp_artistbrowse *", 42)
        browser = spotify.ArtistBrowser(self.session, sp_artistbrowse=sp_artistbrowse)

        result = browser.portraits()

        self.assertEqual(len(result), 0)
        lib_mock.sp_artistbrowse_num_portraits.assert_called_with(sp_artistbrowse)
        self.assertEqual(lib_mock.sp_artistbrowse_portrait.call_count, 0)

    def test_portraits_if_unloaded(self, lib_mock):
        lib_mock.sp_artistbrowse_is_loaded.return_value = 0
        sp_artistbrowse = spotify.ffi.cast("sp_artistbrowse *", 42)
        browser = spotify.ArtistBrowser(self.session, sp_artistbrowse=sp_artistbrowse)

        result = browser.portraits()

        lib_mock.sp_artistbrowse_is_loaded.assert_called_with(sp_artistbrowse)
        self.assertEqual(len(result), 0)

    @mock.patch("spotify.track.lib", spec=spotify.lib)
    def test_tracks(self, track_lib_mock, lib_mock):
        sp_track = spotify.ffi.cast("sp_track *", 43)
        lib_mock.sp_artistbrowse_num_tracks.return_value = 1
        lib_mock.sp_artistbrowse_track.return_value = sp_track
        sp_artistbrowse = spotify.ffi.cast("sp_artistbrowse *", 42)
        browser = spotify.ArtistBrowser(self.session, sp_artistbrowse=sp_artistbrowse)

        self.assertEqual(lib_mock.sp_artistbrowse_add_ref.call_count, 1)
        result = browser.tracks
        self.assertEqual(lib_mock.sp_artistbrowse_add_ref.call_count, 2)

        self.assertEqual(len(result), 1)
        lib_mock.sp_artistbrowse_num_tracks.assert_called_with(sp_artistbrowse)

        item = result[0]
        self.assertIsInstance(item, spotify.Track)
        self.assertEqual(item._sp_track, sp_track)
        self.assertEqual(lib_mock.sp_artistbrowse_track.call_count, 1)
        lib_mock.sp_artistbrowse_track.assert_called_with(sp_artistbrowse, 0)
        track_lib_mock.sp_track_add_ref.assert_called_with(sp_track)

    def test_tracks_if_no_tracks(self, lib_mock):
        lib_mock.sp_artistbrowse_num_tracks.return_value = 0
        sp_artistbrowse = spotify.ffi.cast("sp_artistbrowse *", 42)
        browser = spotify.ArtistBrowser(self.session, sp_artistbrowse=sp_artistbrowse)

        result = browser.tracks

        self.assertEqual(len(result), 0)
        lib_mock.sp_artistbrowse_num_tracks.assert_called_with(sp_artistbrowse)
        self.assertEqual(lib_mock.sp_artistbrowse_track.call_count, 0)

    def test_tracks_if_unloaded(self, lib_mock):
        lib_mock.sp_artistbrowse_is_loaded.return_value = 0
        sp_artistbrowse = spotify.ffi.cast("sp_artistbrowse *", 42)
        browser = spotify.ArtistBrowser(self.session, sp_artistbrowse=sp_artistbrowse)

        result = browser.tracks

        lib_mock.sp_artistbrowse_is_loaded.assert_called_with(sp_artistbrowse)
        self.assertEqual(len(result), 0)

    @mock.patch("spotify.track.lib", spec=spotify.lib)
    def test_tophit_tracks(self, track_lib_mock, lib_mock):
        sp_track = spotify.ffi.cast("sp_track *", 43)
        lib_mock.sp_artistbrowse_num_tophit_tracks.return_value = 1
        lib_mock.sp_artistbrowse_tophit_track.return_value = sp_track
        sp_artistbrowse = spotify.ffi.cast("sp_artistbrowse *", 42)
        browser = spotify.ArtistBrowser(self.session, sp_artistbrowse=sp_artistbrowse)

        self.assertEqual(lib_mock.sp_artistbrowse_add_ref.call_count, 1)
        result = browser.tophit_tracks
        self.assertEqual(lib_mock.sp_artistbrowse_add_ref.call_count, 2)

        self.assertEqual(len(result), 1)
        lib_mock.sp_artistbrowse_num_tophit_tracks.assert_called_with(sp_artistbrowse)

        item = result[0]
        self.assertIsInstance(item, spotify.Track)
        self.assertEqual(item._sp_track, sp_track)
        self.assertEqual(lib_mock.sp_artistbrowse_tophit_track.call_count, 1)
        lib_mock.sp_artistbrowse_tophit_track.assert_called_with(sp_artistbrowse, 0)
        track_lib_mock.sp_track_add_ref.assert_called_with(sp_track)

    def test_tophit_tracks_if_no_tracks(self, lib_mock):
        lib_mock.sp_artistbrowse_num_tophit_tracks.return_value = 0
        sp_artistbrowse = spotify.ffi.cast("sp_artistbrowse *", 42)
        browser = spotify.ArtistBrowser(self.session, sp_artistbrowse=sp_artistbrowse)

        result = browser.tophit_tracks

        self.assertEqual(len(result), 0)
        lib_mock.sp_artistbrowse_num_tophit_tracks.assert_called_with(sp_artistbrowse)
        self.assertEqual(lib_mock.sp_artistbrowse_track.call_count, 0)

    def test_tophit_tracks_if_unloaded(self, lib_mock):
        lib_mock.sp_artistbrowse_is_loaded.return_value = 0
        sp_artistbrowse = spotify.ffi.cast("sp_artistbrowse *", 42)
        browser = spotify.ArtistBrowser(self.session, sp_artistbrowse=sp_artistbrowse)

        result = browser.tophit_tracks

        lib_mock.sp_artistbrowse_is_loaded.assert_called_with(sp_artistbrowse)
        self.assertEqual(len(result), 0)

    @mock.patch("spotify.album.lib", spec=spotify.lib)
    def test_albums(self, album_lib_mock, lib_mock):
        sp_album = spotify.ffi.cast("sp_album *", 43)
        lib_mock.sp_artistbrowse_num_albums.return_value = 1
        lib_mock.sp_artistbrowse_album.return_value = sp_album
        sp_artistbrowse = spotify.ffi.cast("sp_artistbrowse *", 42)
        browser = spotify.ArtistBrowser(self.session, sp_artistbrowse=sp_artistbrowse)

        self.assertEqual(lib_mock.sp_artistbrowse_add_ref.call_count, 1)
        result = browser.albums
        self.assertEqual(lib_mock.sp_artistbrowse_add_ref.call_count, 2)

        self.assertEqual(len(result), 1)
        lib_mock.sp_artistbrowse_num_albums.assert_called_with(sp_artistbrowse)

        item = result[0]
        self.assertIsInstance(item, spotify.Album)
        self.assertEqual(item._sp_album, sp_album)
        self.assertEqual(lib_mock.sp_artistbrowse_album.call_count, 1)
        lib_mock.sp_artistbrowse_album.assert_called_with(sp_artistbrowse, 0)
        album_lib_mock.sp_album_add_ref.assert_called_with(sp_album)

    def test_albums_if_no_albums(self, lib_mock):
        lib_mock.sp_artistbrowse_num_albums.return_value = 0
        sp_artistbrowse = spotify.ffi.cast("sp_artistbrowse *", 42)
        browser = spotify.ArtistBrowser(self.session, sp_artistbrowse=sp_artistbrowse)

        result = browser.albums

        self.assertEqual(len(result), 0)
        lib_mock.sp_artistbrowse_num_albums.assert_called_with(sp_artistbrowse)
        self.assertEqual(lib_mock.sp_artistbrowse_album.call_count, 0)

    def test_albums_if_unloaded(self, lib_mock):
        lib_mock.sp_artistbrowse_is_loaded.return_value = 0
        sp_artistbrowse = spotify.ffi.cast("sp_artistbrowse *", 42)
        browser = spotify.ArtistBrowser(self.session, sp_artistbrowse=sp_artistbrowse)

        result = browser.albums

        lib_mock.sp_artistbrowse_is_loaded.assert_called_with(sp_artistbrowse)
        self.assertEqual(len(result), 0)

    def test_similar_artists(self, lib_mock):
        sp_artist = spotify.ffi.cast("sp_artist *", 43)
        lib_mock.sp_artistbrowse_num_similar_artists.return_value = 1
        lib_mock.sp_artistbrowse_similar_artist.return_value = sp_artist
        sp_artistbrowse = spotify.ffi.cast("sp_artistbrowse *", 42)
        browser = spotify.ArtistBrowser(self.session, sp_artistbrowse=sp_artistbrowse)

        self.assertEqual(lib_mock.sp_artistbrowse_add_ref.call_count, 1)
        result = browser.similar_artists
        self.assertEqual(lib_mock.sp_artistbrowse_add_ref.call_count, 2)

        self.assertEqual(len(result), 1)
        lib_mock.sp_artistbrowse_num_similar_artists.assert_called_with(sp_artistbrowse)

        item = result[0]
        self.assertIsInstance(item, spotify.Artist)
        self.assertEqual(item._sp_artist, sp_artist)
        self.assertEqual(lib_mock.sp_artistbrowse_similar_artist.call_count, 1)
        lib_mock.sp_artistbrowse_similar_artist.assert_called_with(sp_artistbrowse, 0)
        lib_mock.sp_artist_add_ref.assert_called_with(sp_artist)

    def test_similar_artists_if_no_artists(self, lib_mock):
        lib_mock.sp_artistbrowse_num_similar_artists.return_value = 0
        sp_artistbrowse = spotify.ffi.cast("sp_artistbrowse *", 42)
        browser = spotify.ArtistBrowser(self.session, sp_artistbrowse=sp_artistbrowse)

        result = browser.similar_artists

        self.assertEqual(len(result), 0)
        lib_mock.sp_artistbrowse_num_similar_artists.assert_called_with(sp_artistbrowse)
        self.assertEqual(lib_mock.sp_artistbrowse_similar_artist.call_count, 0)

    def test_similar_artists_if_unloaded(self, lib_mock):
        lib_mock.sp_artistbrowse_is_loaded.return_value = 0
        sp_artistbrowse = spotify.ffi.cast("sp_artistbrowse *", 42)
        browser = spotify.ArtistBrowser(self.session, sp_artistbrowse=sp_artistbrowse)

        result = browser.similar_artists

        lib_mock.sp_artistbrowse_is_loaded.assert_called_with(sp_artistbrowse)
        self.assertEqual(len(result), 0)

    def test_biography(self, lib_mock):
        sp_artistbrowse = spotify.ffi.cast("sp_artistbrowse *", 42)
        browser = spotify.ArtistBrowser(self.session, sp_artistbrowse=sp_artistbrowse)
        biography = spotify.ffi.new("char[]", b"Lived, played, and died")
        lib_mock.sp_artistbrowse_biography.return_value = biography

        result = browser.biography

        self.assertIsInstance(result, compat.text_type)
        self.assertEqual(result, "Lived, played, and died")


class ArtistBrowserTypeTest(unittest.TestCase):
    def test_has_constants(self):
        self.assertEqual(spotify.ArtistBrowserType.FULL, 0)
        self.assertEqual(spotify.ArtistBrowserType.NO_TRACKS, 1)
        self.assertEqual(spotify.ArtistBrowserType.NO_ALBUMS, 2)
