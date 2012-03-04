import unittest
from spotify._mockspotify import ArtistBrowser
from spotify._mockspotify import mock_artistbrowse, mock_artist, mock_album, mock_track
from spotify._mockspotify import registry_add, registry_clean
from tests import SkipTest

callback_called = False
callback_userdata = None

class TestArtistbrowser(unittest.TestCase):

    artist = mock_artist("foo")
    similar_artists = [
        mock_artist('artist1'),
        mock_artist('artist2'),
        mock_artist('artist3'),
    ]
    albums = [
        mock_album("album1", artist),
        mock_album("album2", artist),
        mock_album("album3", artist),
    ]
    tracks = [
        mock_track('track1', [artist], albums[0]),
        mock_track('track2', [artist], albums[0]),
        mock_track('track3', [artist], albums[0]),
    ]
    browser = mock_artistbrowse(artist, tracks, albums, similar_artists, 0)

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
        self.assertEqual([a.name() for a in self.browser],
                        ['track1', 'track2', 'track3'])

    def test_albums(self):
        self.assertEqual([a.name() for a in self.browser.albums()],
                        ['album1', 'album2', 'album3'])

    def test_artists(self):
        self.assertEqual([a.name() for a in self.browser.similar_artists()],
                        ['artist1', 'artist2', 'artist3'])

    def test_tracks(self):
        self.assertEqual([a.name() for a in self.browser.tracks()],
                        ['track1', 'track2', 'track3'])

    def test_browser(self):
        browser = ArtistBrowser(self.artist)

    def test_browser_with_callback(self):
        global callback_called
        global callback_userdata
        callback_called = False

        browser = ArtistBrowser(self.artist, 'full', self.callback, self)
        self.assertTrue(callback_called)
        self.assertEqual(callback_userdata, self)
