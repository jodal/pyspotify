import unittest
from spotify._mockspotify import Link, mock_artist, mock_track, mock_album
from spotify._mockspotify import mock_playlist, mock_search, mock_user
from spotify._mockspotify import registry_add, registry_clean
from spotify import SpotifyError

class TestLink(unittest.TestCase):

    user = mock_user('user')
    artist = mock_artist('artist')
    album = mock_album('album', artist)
    playlist = mock_playlist('playlist', [], user)
    search = mock_search('query', [], [], [])
    track = mock_track('track', [artist], album)

    def setUp(self):
        registry_add('spotify:artist:test_artist', self.artist)
        registry_add('spotify:album:test_album', self.album)
        registry_add('spotify:playlist:test_playlist', self.playlist)
        registry_add('spotify:track:test_track', self.track)

    def tearDown(self):
        registry_clean()

    def test_from_string(self):
        s = "spotify:artist:test"
        l = Link.from_string(s)
        self.assertEqual(str(l), "spotify:artist:test")

    def test_from_track(self):
        l2 = Link.from_track(self.track, 42 * 1000)
        self.assertEqual(str(l2), "spotify:track:test_track#00:42")

    def test_from_album(self):
        l2 = Link.from_album(self.album)
        self.assertEqual(str(l2), "spotify:album:test_album")

    def test_from_artist(self):
        l = Link.from_artist(self.artist)
        self.assertEqual(str(l), "spotify:artist:test_artist")

    def test_from_search(self):
        l2 = Link.from_search(self.search)
        self.assertEqual(str(l2), "spotify:search:query")

    def test_from_playlist(self):
        l = Link.from_playlist(self.playlist)
        self.assertEqual(str(l), "spotify:playlist:test_playlist")

    def test_type(self):
        l = Link.from_track(self.track, 0)
        self.assertEqual(l.type(), Link.LINK_TRACK)

    def test_badlink(self):
        self.assertRaises(SpotifyError, Link.from_string, "BADLINK");

    def test_as_track(self):
        l = Link.from_string("spotify:track:test_track")
        t = l.as_track()
        self.assertEqual(str(t), "track")

    def test_as_album(self):
        l = Link.from_string("spotify:album:test_album")
        t = l.as_album()
        self.assertEqual(str(t), "album")

    def test_as_artist(self):
        l = Link.from_string("spotify:artist:test_artist")
        a = l.as_artist()
        self.assertEqual(str(a), "artist")

    def test_as_string(self):
        s = "spotify:track:str_test"
        l = Link.from_string(s)
        self.assertEqual(str(l), "spotify:track:str_test")
