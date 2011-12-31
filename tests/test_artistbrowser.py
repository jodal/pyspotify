import unittest
from spotify._mockspotify import ArtistBrowser
from spotify._mockspotify import mock_artistbrowse, mock_artist, mock_album
from spotify._mockspotify import registry_add, registry_clean
from tests import SkipTest

callback_called = False
callback_userdata = None

class TestArtistbrowser(unittest.TestCase):

    artist = mock_artist("foo")
    albums = [
        mock_album("album1", artist),
        mock_album("album2", artist),
        mock_album("album3", artist),
    ]
    browser = mock_artistbrowse(artist, [], albums, [], 0)

    def callback(self, browser, userdata):
        global callback_called
        global callback_userdata
        callback_called = True
        callback_userdata = userdata

    def setUp(self):
        registry_add('spotify:artist:foo', self.artist)
        registry_add('spotify:artistbrowse:foo', self.browser)

    def tearDown(self):
        registry_clean()

    def test_is_loaded(self):
        self.assertTrue(self.browser.is_loaded())

    def test_sequence(self):
        self.assertEqual(len(self.browser), 3)
        self.assertEqual(self.browser[0].name(), 'album1')
        self.assertEqual(self.browser[1].name(), 'album2')
        self.assertEqual(self.browser[2].name(), 'album3')

    def test_browser(self):
        browser = ArtistBrowser(self.artist)

    def test_browser_with_callback(self):
        global callback_called
        global callback_userdata
        callback_called = False

        browser = ArtistBrowser(self.artist, self.callback, self)
        self.assertTrue(callback_called)
        self.assertEqual(callback_userdata, self)
