import unittest
from spotify._mockspotify import ToplistBrowser
from spotify._mockspotify import mock_album, mock_artist, mock_track, mock_toplistbrowse
from spotify._mockspotify import registry_add, registry_clean

callback_called = False
callback_userdata = None

def callback(toplist, userdata):
    global callback_called
    global callback_userdata
    callback_called = True
    callback_userdata = userdata

class TestToplist(unittest.TestCase):

    artist1 = mock_artist('artist1')
    album1  = mock_album('album1', artist1)
    tracks1 = [
        mock_track('track11', [artist1], album1),
        mock_track('track12', [artist1], album1),
        mock_track('track13', [artist1], album1),
    ]
    artist2 = mock_artist('artist2')
    album2  = mock_album('album2', artist2)
    tracks2 = [
        mock_track('track21', [artist2], album2),
        mock_track('track22', [artist2], album2),
        mock_track('track23', [artist2], album2),
    ]
    albums = [album1, album2]
    artists = [artist1, artist2]
    tracks = tracks1 + tracks2
    browser_albums  = mock_toplistbrowse(albums, [], []);
    browser_artists = mock_toplistbrowse([], artists, []);
    browser_tracks  = mock_toplistbrowse([], [], tracks);

    def setUp(self):
        registry_add('spotify:toplist:albums:FR', self.browser_albums)
        registry_add('spotify:toplist:artists:FR', self.browser_artists)
        registry_add('spotify:toplist:tracks:FR', self.browser_tracks)

    def tearDown(self):
        registry_clean()

    def test_is_loaded(self):
        browser = ToplistBrowser('tracks', 'FR')
        self.assertTrue(browser.is_loaded())

    def test_sequence_albums(self):
        browser = ToplistBrowser('albums', 'FR')
        self.assertEqual([a.name() for a in browser],
                        ['album1', 'album2'])

    def test_sequence_artists(self):
        browser = ToplistBrowser('artists', 'FR')
        self.assertEqual([a.name() for a in browser],
                        ['artist1', 'artist2'])

    def test_sequence_tracks(self):
        browser = ToplistBrowser('tracks', 'FR')
        self.assertEqual([t.name() for t in browser],
                        ['track11', 'track12', 'track13',
                         'track21', 'track22', 'track23'])

    def test_callback(self):
        global callback_called
        global callback_userdata
        callback_called = False
        browser = ToplistBrowser('tracks', 'FR', callback, self)
        self.assertTrue(callback_called)
        self.assertEqual(callback_userdata, self)
