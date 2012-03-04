import unittest
from spotify._mockspotify import mock_artist, mock_album, mock_search, mock_track

class TestSearch(unittest.TestCase):

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
    search = mock_search('query', tracks, albums, artists, 6, 2, 2, 'query2', 0)

    def test_search_is_loaded(self):
        self.assertEqual(self.search.is_loaded(), True)

    def test_artists(self):
        self.assertEqual([a.name() for a in self.search.artists()],
                        ['artist1', 'artist2'])

    def test_albums(self):
        self.assertEqual([a.name() for a in self.search.albums()],
                        ['album1', 'album2'])

    def test_tracks(self):
        self.assertEqual([t.name() for t in self.search.tracks()],
                        ['track11', 'track12', 'track13',
                         'track21', 'track22', 'track23'])

    def test_query(self):
        self.assertEqual(self.search.query(), "query")

    def test_error(self):
        self.assertEqual(self.search.error(), 0)

    def test_did_you_mean(self):
        self.assertEqual(self.search.did_you_mean(), "query2")

    def test_totals(self):
        self.assertEqual(self.search.total_albums(), 2)
        self.assertEqual(self.search.total_artists(), 2)
        self.assertEqual(self.search.total_tracks(), 6)

