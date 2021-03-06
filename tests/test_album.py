from __future__ import unicode_literals

import unittest

import spotify
import tests
from spotify import compat
from tests import mock


@mock.patch("spotify.album.lib", spec=spotify.lib)
class AlbumTest(unittest.TestCase):
    def setUp(self):
        self.session = tests.create_session_mock()

    def test_create_without_uri_or_sp_album_fails(self, lib_mock):
        with self.assertRaises(AssertionError):
            spotify.Album(self.session)

    @mock.patch("spotify.Link", spec=spotify.Link)
    def test_create_from_uri(self, link_mock, lib_mock):
        sp_album = spotify.ffi.cast("sp_album *", 42)
        link_instance_mock = link_mock.return_value
        link_instance_mock.as_album.return_value = spotify.Album(
            self.session, sp_album=sp_album
        )
        uri = "spotify:album:foo"

        result = spotify.Album(self.session, uri=uri)

        link_mock.assert_called_with(self.session, uri=uri)
        link_instance_mock.as_album.assert_called_with()
        lib_mock.sp_album_add_ref.assert_called_with(sp_album)
        self.assertEqual(result._sp_album, sp_album)

    @mock.patch("spotify.Link", spec=spotify.Link)
    def test_create_from_uri_fail_raises_error(self, link_mock, lib_mock):
        link_instance_mock = link_mock.return_value
        link_instance_mock.as_album.return_value = None
        uri = "spotify:album:foo"

        with self.assertRaises(ValueError):
            spotify.Album(self.session, uri=uri)

    def test_adds_ref_to_sp_album_when_created(self, lib_mock):
        sp_album = spotify.ffi.cast("sp_album *", 42)

        spotify.Album(self.session, sp_album=sp_album)

        lib_mock.sp_album_add_ref.assert_called_with(sp_album)

    def test_releases_sp_album_when_album_dies(self, lib_mock):
        sp_album = spotify.ffi.cast("sp_album *", 42)

        album = spotify.Album(self.session, sp_album=sp_album)
        album = None  # noqa
        tests.gc_collect()

        lib_mock.sp_album_release.assert_called_with(sp_album)

    @mock.patch("spotify.Link", spec=spotify.Link)
    def test_repr(self, link_mock, lib_mock):
        link_instance_mock = link_mock.return_value
        link_instance_mock.uri = "foo"
        sp_album = spotify.ffi.cast("sp_album *", 42)
        album = spotify.Album(self.session, sp_album=sp_album)

        result = repr(album)

        self.assertEqual(result, "Album(%r)" % "foo")

    def test_eq(self, lib_mock):
        sp_album = spotify.ffi.cast("sp_album *", 42)
        album1 = spotify.Album(self.session, sp_album=sp_album)
        album2 = spotify.Album(self.session, sp_album=sp_album)

        self.assertTrue(album1 == album2)
        self.assertFalse(album1 == "foo")

    def test_ne(self, lib_mock):
        sp_album = spotify.ffi.cast("sp_album *", 42)
        album1 = spotify.Album(self.session, sp_album=sp_album)
        album2 = spotify.Album(self.session, sp_album=sp_album)

        self.assertFalse(album1 != album2)

    def test_hash(self, lib_mock):
        sp_album = spotify.ffi.cast("sp_album *", 42)
        album1 = spotify.Album(self.session, sp_album=sp_album)
        album2 = spotify.Album(self.session, sp_album=sp_album)

        self.assertEqual(hash(album1), hash(album2))

    def test_is_loaded(self, lib_mock):
        lib_mock.sp_album_is_loaded.return_value = 1
        sp_album = spotify.ffi.cast("sp_album *", 42)
        album = spotify.Album(self.session, sp_album=sp_album)

        result = album.is_loaded

        lib_mock.sp_album_is_loaded.assert_called_once_with(sp_album)
        self.assertTrue(result)

    @mock.patch("spotify.utils.load")
    def test_load(self, load_mock, lib_mock):
        sp_album = spotify.ffi.cast("sp_album *", 42)
        album = spotify.Album(self.session, sp_album=sp_album)

        album.load(10)

        load_mock.assert_called_with(self.session, album, timeout=10)

    def test_is_available(self, lib_mock):
        lib_mock.sp_album_is_available.return_value = 1
        sp_album = spotify.ffi.cast("sp_album *", 42)
        album = spotify.Album(self.session, sp_album=sp_album)

        result = album.is_available

        lib_mock.sp_album_is_available.assert_called_once_with(sp_album)
        self.assertTrue(result)

    def test_is_available_is_none_if_unloaded(self, lib_mock):
        lib_mock.sp_album_is_loaded.return_value = 0
        sp_album = spotify.ffi.cast("sp_album *", 42)
        album = spotify.Album(self.session, sp_album=sp_album)

        result = album.is_available

        lib_mock.sp_album_is_loaded.assert_called_once_with(sp_album)
        self.assertIsNone(result)

    @mock.patch("spotify.artist.lib", spec=spotify.lib)
    def test_artist(self, artist_lib_mock, lib_mock):
        sp_artist = spotify.ffi.cast("sp_artist *", 43)
        lib_mock.sp_album_artist.return_value = sp_artist
        sp_album = spotify.ffi.cast("sp_album *", 42)
        album = spotify.Album(self.session, sp_album=sp_album)

        result = album.artist

        lib_mock.sp_album_artist.assert_called_with(sp_album)
        self.assertEqual(artist_lib_mock.sp_artist_add_ref.call_count, 1)
        self.assertIsInstance(result, spotify.Artist)
        self.assertEqual(result._sp_artist, sp_artist)

    @mock.patch("spotify.artist.lib", spec=spotify.lib)
    def test_artist_if_unloaded(self, artist_lib_mock, lib_mock):
        lib_mock.sp_album_artist.return_value = spotify.ffi.NULL
        sp_album = spotify.ffi.cast("sp_album *", 42)
        album = spotify.Album(self.session, sp_album=sp_album)

        result = album.artist

        lib_mock.sp_album_artist.assert_called_with(sp_album)
        self.assertIsNone(result)

    @mock.patch("spotify.Image", spec=spotify.Image)
    def test_cover(self, image_mock, lib_mock):
        sp_album = spotify.ffi.cast("sp_album *", 42)
        album = spotify.Album(self.session, sp_album=sp_album)
        sp_image_id = spotify.ffi.new("char[]", b"cover-id")
        lib_mock.sp_album_cover.return_value = sp_image_id
        sp_image = spotify.ffi.cast("sp_image *", 43)
        lib_mock.sp_image_create.return_value = sp_image
        image_mock.return_value = mock.sentinel.image
        image_size = spotify.ImageSize.SMALL
        callback = mock.Mock()

        result = album.cover(image_size, callback=callback)

        self.assertIs(result, mock.sentinel.image)
        lib_mock.sp_album_cover.assert_called_with(sp_album, int(image_size))
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
    def test_cover_defaults_to_normal_size(self, image_mock, lib_mock):
        sp_image_id = spotify.ffi.new("char[]", b"cover-id")
        lib_mock.sp_album_cover.return_value = sp_image_id
        sp_image = spotify.ffi.cast("sp_image *", 43)
        lib_mock.sp_image_create.return_value = sp_image
        sp_album = spotify.ffi.cast("sp_album *", 42)
        album = spotify.Album(self.session, sp_album=sp_album)

        album.cover()

        lib_mock.sp_album_cover.assert_called_with(
            sp_album, int(spotify.ImageSize.NORMAL)
        )

    def test_cover_is_none_if_null(self, lib_mock):
        lib_mock.sp_album_cover.return_value = spotify.ffi.NULL
        sp_album = spotify.ffi.cast("sp_album *", 42)
        album = spotify.Album(self.session, sp_album=sp_album)

        result = album.cover()

        lib_mock.sp_album_cover.assert_called_with(
            sp_album, int(spotify.ImageSize.NORMAL)
        )
        self.assertIsNone(result)

    @mock.patch("spotify.Link", spec=spotify.Link)
    def test_cover_link_creates_link_to_cover(self, link_mock, lib_mock):
        sp_album = spotify.ffi.cast("sp_album *", 42)
        album = spotify.Album(self.session, sp_album=sp_album)
        sp_link = spotify.ffi.cast("sp_link *", 43)
        lib_mock.sp_link_create_from_album_cover.return_value = sp_link
        link_mock.return_value = mock.sentinel.link
        image_size = spotify.ImageSize.SMALL

        result = album.cover_link(image_size)

        lib_mock.sp_link_create_from_album_cover.assert_called_once_with(
            sp_album, int(image_size)
        )
        link_mock.assert_called_once_with(self.session, sp_link=sp_link, add_ref=False)
        self.assertEqual(result, mock.sentinel.link)

    @mock.patch("spotify.Link", spec=spotify.Link)
    def test_cover_link_defaults_to_normal_size(self, link_mock, lib_mock):
        sp_album = spotify.ffi.cast("sp_album *", 42)
        album = spotify.Album(self.session, sp_album=sp_album)
        sp_link = spotify.ffi.cast("sp_link *", 43)
        lib_mock.sp_link_create_from_album_cover.return_value = sp_link
        link_mock.return_value = mock.sentinel.link

        album.cover_link()

        lib_mock.sp_link_create_from_album_cover.assert_called_once_with(
            sp_album, int(spotify.ImageSize.NORMAL)
        )

    def test_name(self, lib_mock):
        lib_mock.sp_album_name.return_value = spotify.ffi.new("char[]", b"Foo Bar Baz")
        sp_album = spotify.ffi.cast("sp_album *", 42)
        album = spotify.Album(self.session, sp_album=sp_album)

        result = album.name

        lib_mock.sp_album_name.assert_called_once_with(sp_album)
        self.assertEqual(result, "Foo Bar Baz")

    def test_name_is_none_if_unloaded(self, lib_mock):
        lib_mock.sp_album_name.return_value = spotify.ffi.new("char[]", b"")
        sp_album = spotify.ffi.cast("sp_album *", 42)
        album = spotify.Album(self.session, sp_album=sp_album)

        result = album.name

        lib_mock.sp_album_name.assert_called_once_with(sp_album)
        self.assertIsNone(result)

    def test_year(self, lib_mock):
        lib_mock.sp_album_year.return_value = 2013
        sp_album = spotify.ffi.cast("sp_album *", 42)
        album = spotify.Album(self.session, sp_album=sp_album)

        result = album.year

        lib_mock.sp_album_year.assert_called_once_with(sp_album)
        self.assertEqual(result, 2013)

    def test_year_is_none_if_unloaded(self, lib_mock):
        lib_mock.sp_album_is_loaded.return_value = 0
        sp_album = spotify.ffi.cast("sp_album *", 42)
        album = spotify.Album(self.session, sp_album=sp_album)

        result = album.year

        lib_mock.sp_album_is_loaded.assert_called_once_with(sp_album)
        self.assertIsNone(result)

    def test_type(self, lib_mock):
        lib_mock.sp_album_type.return_value = int(spotify.AlbumType.SINGLE)
        sp_album = spotify.ffi.cast("sp_album *", 42)
        album = spotify.Album(self.session, sp_album=sp_album)

        result = album.type

        lib_mock.sp_album_type.assert_called_once_with(sp_album)
        self.assertIs(result, spotify.AlbumType.SINGLE)

    def test_type_is_none_if_unloaded(self, lib_mock):
        lib_mock.sp_album_is_loaded.return_value = 0
        sp_album = spotify.ffi.cast("sp_album *", 42)
        album = spotify.Album(self.session, sp_album=sp_album)

        result = album.type

        lib_mock.sp_album_is_loaded.assert_called_once_with(sp_album)
        self.assertIsNone(result)

    @mock.patch("spotify.Link", spec=spotify.Link)
    def test_link_creates_link_to_album(self, link_mock, lib_mock):
        sp_album = spotify.ffi.cast("sp_album *", 42)
        album = spotify.Album(self.session, sp_album=sp_album)
        sp_link = spotify.ffi.cast("sp_link *", 43)
        lib_mock.sp_link_create_from_album.return_value = sp_link
        link_mock.return_value = mock.sentinel.link

        result = album.link

        link_mock.assert_called_once_with(self.session, sp_link=sp_link, add_ref=False)
        self.assertEqual(result, mock.sentinel.link)


@mock.patch("spotify.album.lib", spec=spotify.lib)
class AlbumBrowserTest(unittest.TestCase):
    def setUp(self):
        self.session = tests.create_session_mock()
        spotify._session_instance = self.session

    def tearDown(self):
        spotify._session_instance = None

    def test_create_without_album_or_sp_albumbrowse_fails(self, lib_mock):
        with self.assertRaises(AssertionError):
            spotify.AlbumBrowser(self.session)

    def test_create_from_album(self, lib_mock):
        sp_album = spotify.ffi.cast("sp_album *", 43)
        album = spotify.Album(self.session, sp_album=sp_album)
        sp_albumbrowse = spotify.ffi.cast("sp_albumbrowse *", 42)
        lib_mock.sp_albumbrowse_create.return_value = sp_albumbrowse

        result = album.browse()

        lib_mock.sp_albumbrowse_create.assert_called_with(
            self.session._sp_session, sp_album, mock.ANY, mock.ANY
        )
        self.assertIsInstance(result, spotify.AlbumBrowser)

        albumbrowse_complete_cb = lib_mock.sp_albumbrowse_create.call_args[0][2]
        userdata = lib_mock.sp_albumbrowse_create.call_args[0][3]
        self.assertFalse(result.loaded_event.is_set())
        albumbrowse_complete_cb(sp_albumbrowse, userdata)
        self.assertTrue(result.loaded_event.is_set())

    def test_create_from_album_with_callback(self, lib_mock):
        sp_album = spotify.ffi.cast("sp_album *", 43)
        album = spotify.Album(self.session, sp_album=sp_album)
        sp_albumbrowse = spotify.ffi.cast("sp_albumbrowse *", 42)
        lib_mock.sp_albumbrowse_create.return_value = sp_albumbrowse
        callback = mock.Mock()

        result = album.browse(callback)

        lib_mock.sp_albumbrowse_create.assert_called_with(
            self.session._sp_session, sp_album, mock.ANY, mock.ANY
        )
        albumbrowse_complete_cb = lib_mock.sp_albumbrowse_create.call_args[0][2]
        userdata = lib_mock.sp_albumbrowse_create.call_args[0][3]
        albumbrowse_complete_cb(sp_albumbrowse, userdata)

        result.loaded_event.wait(3)
        callback.assert_called_with(result)

    def test_browser_is_gone_before_callback_is_called(self, lib_mock):
        sp_album = spotify.ffi.cast("sp_album *", 43)
        album = spotify.Album(self.session, sp_album=sp_album)
        sp_albumbrowse = spotify.ffi.cast("sp_albumbrowse *", 42)
        lib_mock.sp_albumbrowse_create.return_value = sp_albumbrowse
        callback = mock.Mock()

        result = spotify.AlbumBrowser(self.session, album=album, callback=callback)
        loaded_event = result.loaded_event
        result = None  # noqa
        tests.gc_collect()

        # The mock keeps the handle/userdata alive, thus this test doesn't
        # really test that session._callback_handles keeps the handle alive.
        albumbrowse_complete_cb = lib_mock.sp_albumbrowse_create.call_args[0][2]
        userdata = lib_mock.sp_albumbrowse_create.call_args[0][3]
        albumbrowse_complete_cb(sp_albumbrowse, userdata)

        loaded_event.wait(3)
        self.assertEqual(callback.call_count, 1)
        self.assertEqual(callback.call_args[0][0]._sp_albumbrowse, sp_albumbrowse)

    def test_adds_ref_to_sp_albumbrowse_when_created(self, lib_mock):
        session = tests.create_session_mock()
        sp_albumbrowse = spotify.ffi.cast("sp_albumbrowse *", 42)

        spotify.AlbumBrowser(session, sp_albumbrowse=sp_albumbrowse)

        lib_mock.sp_albumbrowse_add_ref.assert_called_with(sp_albumbrowse)

    def test_releases_sp_albumbrowse_when_album_dies(self, lib_mock):
        sp_albumbrowse = spotify.ffi.cast("sp_albumbrowse *", 42)

        browser = spotify.AlbumBrowser(self.session, sp_albumbrowse=sp_albumbrowse)
        browser = None  # noqa
        tests.gc_collect()

        lib_mock.sp_albumbrowse_release.assert_called_with(sp_albumbrowse)

    @mock.patch("spotify.Link", spec=spotify.Link)
    def test_repr(self, link_mock, lib_mock):
        sp_albumbrowse = spotify.ffi.cast("sp_albumbrowse *", 42)
        browser = spotify.AlbumBrowser(self.session, sp_albumbrowse=sp_albumbrowse)
        lib_mock.sp_albumbrowse_is_loaded.return_value = 1
        sp_album = spotify.ffi.cast("sp_album *", 43)
        lib_mock.sp_albumbrowse_album.return_value = sp_album
        link_instance_mock = link_mock.return_value
        link_instance_mock.uri = "foo"

        result = repr(browser)

        self.assertEqual(result, "AlbumBrowser(%r)" % "foo")

    def test_repr_if_unloaded(self, lib_mock):
        sp_albumbrowse = spotify.ffi.cast("sp_albumbrowse *", 42)
        browser = spotify.AlbumBrowser(self.session, sp_albumbrowse=sp_albumbrowse)
        lib_mock.sp_albumbrowse_is_loaded.return_value = 0

        result = repr(browser)

        self.assertEqual(result, "AlbumBrowser(<not loaded>)")

    def test_eq(self, lib_mock):
        sp_albumbrowse = spotify.ffi.cast("sp_albumbrowse *", 42)
        browser1 = spotify.AlbumBrowser(self.session, sp_albumbrowse=sp_albumbrowse)
        browser2 = spotify.AlbumBrowser(self.session, sp_albumbrowse=sp_albumbrowse)

        self.assertTrue(browser1 == browser2)
        self.assertFalse(browser1 == "foo")

    def test_ne(self, lib_mock):
        sp_albumbrowse = spotify.ffi.cast("sp_albumbrowse *", 42)
        browser1 = spotify.AlbumBrowser(self.session, sp_albumbrowse=sp_albumbrowse)
        browser2 = spotify.AlbumBrowser(self.session, sp_albumbrowse=sp_albumbrowse)

        self.assertFalse(browser1 != browser2)

    def test_hash(self, lib_mock):
        sp_albumbrowse = spotify.ffi.cast("sp_albumbrowse *", 42)
        browser1 = spotify.AlbumBrowser(self.session, sp_albumbrowse=sp_albumbrowse)
        browser2 = spotify.AlbumBrowser(self.session, sp_albumbrowse=sp_albumbrowse)

        self.assertEqual(hash(browser1), hash(browser2))

    def test_is_loaded(self, lib_mock):
        lib_mock.sp_albumbrowse_is_loaded.return_value = 1
        sp_albumbrowse = spotify.ffi.cast("sp_albumbrowse *", 42)
        browser = spotify.AlbumBrowser(self.session, sp_albumbrowse=sp_albumbrowse)

        result = browser.is_loaded

        lib_mock.sp_albumbrowse_is_loaded.assert_called_once_with(sp_albumbrowse)
        self.assertTrue(result)

    @mock.patch("spotify.utils.load")
    def test_load(self, load_mock, lib_mock):
        sp_albumbrowse = spotify.ffi.cast("sp_albumbrowse *", 42)
        browser = spotify.AlbumBrowser(self.session, sp_albumbrowse=sp_albumbrowse)

        browser.load(10)

        load_mock.assert_called_with(self.session, browser, timeout=10)

    def test_error(self, lib_mock):
        lib_mock.sp_albumbrowse_error.return_value = int(
            spotify.ErrorType.OTHER_PERMANENT
        )
        sp_albumbrowse = spotify.ffi.cast("sp_albumbrowse *", 42)
        browser = spotify.AlbumBrowser(self.session, sp_albumbrowse=sp_albumbrowse)

        result = browser.error

        lib_mock.sp_albumbrowse_error.assert_called_once_with(sp_albumbrowse)
        self.assertIs(result, spotify.ErrorType.OTHER_PERMANENT)

    def test_backend_request_duration(self, lib_mock):
        lib_mock.sp_albumbrowse_backend_request_duration.return_value = 137
        sp_albumbrowse = spotify.ffi.cast("sp_albumbrowse *", 42)
        browser = spotify.AlbumBrowser(self.session, sp_albumbrowse=sp_albumbrowse)

        result = browser.backend_request_duration

        lib_mock.sp_albumbrowse_backend_request_duration.assert_called_with(
            sp_albumbrowse
        )
        self.assertEqual(result, 137)

    def test_backend_request_duration_when_not_loaded(self, lib_mock):
        lib_mock.sp_albumbrowse_is_loaded.return_value = 0
        sp_albumbrowse = spotify.ffi.cast("sp_albumbrowse *", 42)
        browser = spotify.AlbumBrowser(self.session, sp_albumbrowse=sp_albumbrowse)

        result = browser.backend_request_duration

        lib_mock.sp_albumbrowse_is_loaded.assert_called_with(sp_albumbrowse)
        self.assertEqual(lib_mock.sp_albumbrowse_backend_request_duration.call_count, 0)
        self.assertIsNone(result)

    def test_album(self, lib_mock):
        sp_albumbrowse = spotify.ffi.cast("sp_albumbrowse *", 42)
        browser = spotify.AlbumBrowser(self.session, sp_albumbrowse=sp_albumbrowse)
        sp_album = spotify.ffi.cast("sp_album *", 43)
        lib_mock.sp_albumbrowse_album.return_value = sp_album

        result = browser.album

        self.assertIsInstance(result, spotify.Album)
        self.assertEqual(result._sp_album, sp_album)

    def test_album_when_not_loaded(self, lib_mock):
        sp_albumbrowse = spotify.ffi.cast("sp_albumbrowse *", 42)
        browser = spotify.AlbumBrowser(self.session, sp_albumbrowse=sp_albumbrowse)
        lib_mock.sp_albumbrowse_album.return_value = spotify.ffi.NULL

        result = browser.album

        lib_mock.sp_albumbrowse_album.assert_called_with(sp_albumbrowse)
        self.assertIsNone(result)

    @mock.patch("spotify.artist.lib", spec=spotify.lib)
    def test_artist(self, artist_lib_mock, lib_mock):
        sp_albumbrowse = spotify.ffi.cast("sp_albumbrowse *", 42)
        browser = spotify.AlbumBrowser(self.session, sp_albumbrowse=sp_albumbrowse)
        sp_artist = spotify.ffi.cast("sp_artist *", 43)
        lib_mock.sp_albumbrowse_artist.return_value = sp_artist

        result = browser.artist

        self.assertIsInstance(result, spotify.Artist)
        self.assertEqual(result._sp_artist, sp_artist)

    def test_artist_when_not_loaded(self, lib_mock):
        sp_albumbrowse = spotify.ffi.cast("sp_albumbrowse *", 42)
        browser = spotify.AlbumBrowser(self.session, sp_albumbrowse=sp_albumbrowse)
        lib_mock.sp_albumbrowse_artist.return_value = spotify.ffi.NULL

        result = browser.artist

        lib_mock.sp_albumbrowse_artist.assert_called_with(sp_albumbrowse)
        self.assertIsNone(result)

    def test_copyrights(self, lib_mock):
        copyright = spotify.ffi.new("char[]", b"Apple Records 1973")
        lib_mock.sp_albumbrowse_num_copyrights.return_value = 1
        lib_mock.sp_albumbrowse_copyright.return_value = copyright
        sp_albumbrowse = spotify.ffi.cast("sp_albumbrowse *", 42)
        browser = spotify.AlbumBrowser(self.session, sp_albumbrowse=sp_albumbrowse)

        self.assertEqual(lib_mock.sp_albumbrowse_add_ref.call_count, 1)
        result = browser.copyrights
        self.assertEqual(lib_mock.sp_albumbrowse_add_ref.call_count, 2)

        self.assertEqual(len(result), 1)
        lib_mock.sp_albumbrowse_num_copyrights.assert_called_with(sp_albumbrowse)

        item = result[0]
        self.assertIsInstance(item, compat.text_type)
        self.assertEqual(item, "Apple Records 1973")
        self.assertEqual(lib_mock.sp_albumbrowse_copyright.call_count, 1)
        lib_mock.sp_albumbrowse_copyright.assert_called_with(sp_albumbrowse, 0)

    def test_copyrights_if_no_copyrights(self, lib_mock):
        lib_mock.sp_albumbrowse_num_copyrights.return_value = 0
        sp_albumbrowse = spotify.ffi.cast("sp_albumbrowse *", 42)
        browser = spotify.AlbumBrowser(self.session, sp_albumbrowse=sp_albumbrowse)

        result = browser.copyrights

        self.assertEqual(len(result), 0)
        lib_mock.sp_albumbrowse_num_copyrights.assert_called_with(sp_albumbrowse)
        self.assertEqual(lib_mock.sp_albumbrowse_copyright.call_count, 0)

    def test_copyrights_if_unloaded(self, lib_mock):
        lib_mock.sp_albumbrowse_is_loaded.return_value = 0
        sp_albumbrowse = spotify.ffi.cast("sp_albumbrowse *", 42)
        browser = spotify.AlbumBrowser(self.session, sp_albumbrowse=sp_albumbrowse)

        result = browser.copyrights

        lib_mock.sp_albumbrowse_is_loaded.assert_called_with(sp_albumbrowse)
        self.assertEqual(len(result), 0)

    @mock.patch("spotify.track.lib", spec=spotify.lib)
    def test_tracks(self, track_lib_mock, lib_mock):
        sp_track = spotify.ffi.cast("sp_track *", 43)
        lib_mock.sp_albumbrowse_num_tracks.return_value = 1
        lib_mock.sp_albumbrowse_track.return_value = sp_track
        sp_albumbrowse = spotify.ffi.cast("sp_albumbrowse *", 42)
        browser = spotify.AlbumBrowser(self.session, sp_albumbrowse=sp_albumbrowse)

        self.assertEqual(lib_mock.sp_albumbrowse_add_ref.call_count, 1)
        result = browser.tracks
        self.assertEqual(lib_mock.sp_albumbrowse_add_ref.call_count, 2)

        self.assertEqual(len(result), 1)
        lib_mock.sp_albumbrowse_num_tracks.assert_called_with(sp_albumbrowse)

        item = result[0]
        self.assertIsInstance(item, spotify.Track)
        self.assertEqual(item._sp_track, sp_track)
        self.assertEqual(lib_mock.sp_albumbrowse_track.call_count, 1)
        lib_mock.sp_albumbrowse_track.assert_called_with(sp_albumbrowse, 0)
        track_lib_mock.sp_track_add_ref.assert_called_with(sp_track)

    def test_tracks_if_no_tracks(self, lib_mock):
        lib_mock.sp_albumbrowse_num_tracks.return_value = 0
        sp_albumbrowse = spotify.ffi.cast("sp_albumbrowse *", 42)
        browser = spotify.AlbumBrowser(self.session, sp_albumbrowse=sp_albumbrowse)

        result = browser.tracks

        self.assertEqual(len(result), 0)
        lib_mock.sp_albumbrowse_num_tracks.assert_called_with(sp_albumbrowse)
        self.assertEqual(lib_mock.sp_albumbrowse_track.call_count, 0)

    def test_tracks_if_unloaded(self, lib_mock):
        lib_mock.sp_albumbrowse_is_loaded.return_value = 0
        sp_albumbrowse = spotify.ffi.cast("sp_albumbrowse *", 42)
        browser = spotify.AlbumBrowser(self.session, sp_albumbrowse=sp_albumbrowse)

        result = browser.tracks

        lib_mock.sp_albumbrowse_is_loaded.assert_called_with(sp_albumbrowse)
        self.assertEqual(len(result), 0)

    def test_review(self, lib_mock):
        sp_albumbrowse = spotify.ffi.cast("sp_albumbrowse *", 42)
        browser = spotify.AlbumBrowser(self.session, sp_albumbrowse=sp_albumbrowse)
        review = spotify.ffi.new("char[]", b"A nice album")
        lib_mock.sp_albumbrowse_review.return_value = review

        result = browser.review

        self.assertIsInstance(result, compat.text_type)
        self.assertEqual(result, "A nice album")


class AlbumTypeTest(unittest.TestCase):
    def test_has_constants(self):
        self.assertEqual(spotify.AlbumType.ALBUM, 0)
        self.assertEqual(spotify.AlbumType.SINGLE, 1)
