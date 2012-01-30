import unittest
from spotify._mockspotify import mock_albumbrowse, mock_album, mock_artist, \
                                 mock_track
from spotify._mockspotify import Album, AlbumBrowser
from spotify._mockspotify import registry_add, registry_clean

callback_called = False
callback_userdata = None

class TestAlbumbrowser(unittest.TestCase):

    artist = mock_artist("foo")
    album = mock_album("bar", artist)
    tracks = [
        mock_track("baz1", [artist], album),
        mock_track("baz2", [artist], album),
        mock_track("baz3", [artist], album),
    ]
    browser = mock_albumbrowse(album, tracks, artist=artist, error=0)

    def callback(self, browser, userdata):
        global callback_called
        global callback_userdata
        callback_called = True
        callback_userdata = userdata

    def setUp(self):
        registry_add('spotify:album:1234', self.album)
        registry_add('spotify:albumbrowse:1234', self.browser)

    def tearDown(self):
        registry_clean()

    def test_is_loaded(self):
        assert self.browser.is_loaded()

    def test_sequence(self):
        assert len(self.browser) == 3
        assert self.browser[0].name() == 'baz1'
        assert self.browser[1].name() == 'baz2'
        assert self.browser[2].name() == 'baz3'

    def test_browser(self):
        browser = AlbumBrowser(self.album)

    def test_browser_with_callback(self):
        global callback_called
        global callback_userdata
        callback_called = False

        browser = AlbumBrowser(self.album, self.callback, self)
        self.assertTrue(callback_called)
        self.assertEqual(callback_userdata, self)
