import unittest
from spotify._mockspotify import mock_playlist, mock_event_trigger
from spotify._mockspotify import mock_album, mock_artist, mock_user, mock_track
from spotify.manager import SpotifyPlaylistManager
from spotify._mockspotify import User, Playlist

callback_called = None

class MyPlaylistManager(SpotifyPlaylistManager):

    def tracks_added(*args):
        global callback_called
        callback_called = 'tracks_added', args

    def tracks_moved(*args):
        global callback_called
        callback_called = 'tracks_moved', args

    def tracks_removed(*args):
        global callback_called
        callback_called = 'tracks_removed', args

    def playlist_renamed(*args):
        global callback_called
        callback_called = 'playlist_renamed', args

    def playlist_state_changed(*args):
        global callback_called
        callback_called = 'playlist_state_changed', args

    def playlist_update_in_progress(*args):
        global callback_called
        callback_called = 'playlist_update_in_progress', args

    def playlist_metadata_updated(*args):
        global callback_called
        callback_called = 'playlist_metadata_updated', args

    def track_created_changed(*args):
        global callback_called
        callback_called = 'track_created_changed', args

    def track_message_changed(*args):
        global callback_called
        callback_called = 'track_message_changed', args

    def track_seen_changed(*args):
        global callback_called
        callback_called = 'track_seen_changed', args

    def description_changed(*args):
        global callback_called
        callback_called = 'description_changed', args

    def subscribers_changed(*args):
        global callback_called
        callback_called = 'subscribers_changed', args

    def image_changed(*args):
        global callback_called
        callback_called = 'image_changed', args

class TestPlaylistManager(unittest.TestCase):

    artist = mock_artist('artist')
    album = mock_album('album', artist)
    owner = mock_user('owner')
    tracks = [
        (mock_track('track1', [artist], album), owner, 1320961109),
        (mock_track('track2', [artist], album), owner, 1320961109),
        (mock_track('track3', [artist], album), owner, 1320961109),
    ]
    pure_tracks = [t[0] for t in tracks]
    description = 'description'
    num_subscribers = 42
    subscribers = ['sub1', 'sub2', 'sub3']
    image = '01234567890123456789'
    playlist = mock_playlist('foo_', [], owner, subscribers, num_subscribers,
                             description, image)
    def setUp(self):
        global callback_called
        self.manager = MyPlaylistManager()
        callback_called = None

    def test_tracks_added(self):
        global callback_called
        callback = self.manager.tracks_added
        self.playlist.add_tracks_added_callback(callback, self.manager)
        mock_event_trigger(20, self.playlist)

        self.assertNotEqual(callback_called, None)
        name, args = callback_called
        self.assertEqual(name,"tracks_added")
        self.assertEqual(len(args), 5)
        self.assertEqual(args[0], self.manager)
        self.assertEqual(type(args[1]), Playlist)
        self.assertEqual(args[1].name(), self.playlist.name())
        self.assertEqual(type(args[2]), list)
        self.assertEqual(len(args[2]), 3)
        self.assertEqual(map(lambda x: x.name(), args[2]), ['foo', 'bar', 'baz'])
        self.assertEqual(type(args[3]), int)

    def test_tracks_moved(self):
        global callback_called
        callback = self.manager.tracks_moved
        self.playlist.add_tracks_moved_callback(callback, self.manager)
        mock_event_trigger(21, self.playlist)

        self.assertNotEqual(callback_called, None)
        name, args = callback_called
        self.assertEqual(name, "tracks_moved")
        self.assertEqual(len(args), 5)
        self.assertEqual(args[0], self.manager)
        self.assertEqual(type(args[1]), Playlist)
        self.assertEqual(args[1].name(), self.playlist.name())
        self.assertEqual(type(args[2]), list)
        self.assertEqual(len(args[2]), 3)
        self.assertEqual(args[2], [0, 1, 2])
        self.assertEqual(type(args[3]), int)

    def test_tracks_removed(self):
        global callback_called
        callback = self.manager.tracks_removed
        self.playlist.add_tracks_removed_callback(callback, self.manager)
        mock_event_trigger(22, self.playlist)

        self.assertNotEqual(callback_called, None)
        name, args = callback_called
        self.assertEqual(name, "tracks_removed")
        self.assertEqual(len(args), 4)
        self.assertEqual(args[0], self.manager)
        self.assertEqual(type(args[1]), Playlist)
        self.assertEqual(args[1].name(), self.playlist.name())
        self.assertEqual(type(args[2]), list)
        self.assertEqual(len(args[2]), 3)
        self.assertEqual(args[2], [0, 1, 2])

    def test_playlist_renamed(self):
        global callback_called
        callback = self.manager.playlist_renamed
        self.playlist.add_playlist_renamed_callback(callback, self.manager)
        mock_event_trigger(23, self.playlist)

        self.assertNotEqual(callback_called, None)
        name, args = callback_called
        self.assertEqual(name, "playlist_renamed")
        self.assertEqual(len(args), 3)
        self.assertEqual(args[0], self.manager)
        self.assertEqual(type(args[1]), Playlist)
        self.assertEqual(args[1].name(), self.playlist.name())

    def test_playlist_state_changed(self):
        global callback_called
        callback = self.manager.playlist_state_changed
        self.playlist.add_playlist_state_changed_callback(callback, self.manager)
        mock_event_trigger(24, self.playlist)

        self.assertNotEqual(callback_called, None)
        name, args = callback_called
        self.assertEqual(name, "playlist_state_changed")
        self.assertEqual(len(args), 3)
        self.assertEqual(args[0], self.manager)
        self.assertEqual(type(args[1]), Playlist)
        self.assertEqual(args[1].name(), self.playlist.name())

    def test_playlist_update_in_progress(self):
        global callback_called
        callback = self.manager.playlist_update_in_progress
        self.playlist.add_playlist_update_in_progress_callback(callback, self.manager)
        mock_event_trigger(25, self.playlist)

        self.assertNotEqual(callback_called, None)
        name, args = callback_called
        self.assertEqual(name, "playlist_update_in_progress")
        self.assertEqual(len(args), 4)
        self.assertEqual(args[0], self.manager)
        self.assertEqual(type(args[1]), Playlist)
        self.assertEqual(args[1].name(), self.playlist.name())
        self.assertEqual(type(args[2]), bool)
        self.assertEqual(args[2], True)

    def test_playlist_metadata_updated(self):
        global callback_called
        callback = self.manager.playlist_metadata_updated
        self.playlist.add_playlist_metadata_updated_callback(callback, self.manager)
        mock_event_trigger(26, self.playlist)

        self.assertNotEqual(callback_called, None)
        name, args = callback_called
        self.assertEqual(name, "playlist_metadata_updated")
        self.assertEqual(len(args), 3)
        self.assertEqual(args[0], self.manager)
        self.assertEqual(type(args[1]), Playlist)
        self.assertEqual(args[1].name(), self.playlist.name())

    def test_track_created_changed(self):
        global callback_called
        callback = self.manager.track_created_changed
        self.playlist.add_track_created_changed_callback(callback, self.manager)
        mock_event_trigger(27, self.playlist)

        self.assertNotEqual(callback_called, None)
        name, args = callback_called
        self.assertEqual(name, "track_created_changed")
        self.assertEqual(len(args), 6)
        self.assertEqual(args[0], self.manager)
        self.assertEqual(type(args[1]), Playlist)
        self.assertEqual(args[1].name(), self.playlist.name())
        self.assertEqual(type(args[2]), int)
        self.assertEqual(args[2], 1)
        self.assertEqual(type(args[3]), User)
        self.assertEqual(args[3].canonical_name(), u'foo')
        self.assertEqual(type(args[4]), int)
        self.assertEqual(args[4], 123)

    def test_track_message_changed(self):
        global callback_called
        callback = self.manager.track_message_changed
        self.playlist.add_track_message_changed_callback(callback, self.manager)
        mock_event_trigger(28, self.playlist)

        self.assertNotEqual(callback_called, None)
        name, args = callback_called
        self.assertEqual(name, "track_message_changed")
        self.assertEqual(len(args), 5)
        self.assertEqual(args[0], self.manager)
        self.assertEqual(type(args[1]), Playlist)
        self.assertEqual(args[1].name(), self.playlist.name())
        self.assertEqual(type(args[2]), int)
        self.assertEqual(args[2], 1)
        self.assertEqual(type(args[3]), unicode)
        self.assertEqual(args[3], u'foo')

    def test_track_seen_changed(self):
        global callback_called
        callback = self.manager.track_seen_changed
        self.playlist.add_track_seen_changed_callback(callback, self.manager)
        mock_event_trigger(29, self.playlist)

        self.assertNotEqual(callback_called, None)
        name, args = callback_called
        self.assertEqual(name, "track_seen_changed")
        self.assertEqual(len(args), 5)
        self.assertEqual(args[0], self.manager)
        self.assertEqual(type(args[1]), Playlist)
        self.assertEqual(args[1].name(), self.playlist.name())
        self.assertEqual(type(args[2]), int)
        self.assertEqual(args[2], 1)
        self.assertEqual(type(args[3]), bool)
        self.assertEqual(args[3], False)

    def test_description_changed(self):
        global callback_called
        callback = self.manager.description_changed
        self.playlist.add_description_changed_callback(callback, self.manager)
        mock_event_trigger(30, self.playlist)

        self.assertNotEqual(callback_called, None)
        name, args = callback_called
        self.assertEqual(name, "description_changed")
        self.assertEqual(len(args), 4)
        self.assertEqual(args[0], self.manager)
        self.assertEqual(type(args[1]), Playlist)
        self.assertEqual(args[1].name(), self.playlist.name())
        self.assertEqual(type(args[2]), unicode)
        self.assertEqual(args[2], u'foo')

    def test_subscribers_changed(self):
        global callback_called
        callback = self.manager.subscribers_changed
        self.playlist.add_subscribers_changed_callback(callback, self.manager)
        mock_event_trigger(31, self.playlist)

        self.assertNotEqual(callback_called, None)
        name, args = callback_called
        self.assertEqual(name, "subscribers_changed")
        self.assertEqual(len(args), 3)
        self.assertEqual(args[0], self.manager)
        self.assertEqual(type(args[1]), Playlist)
        self.assertEqual(args[1].name(), self.playlist.name())

    def test_image_changed(self):
        global callback_called
        callback = self.manager.image_changed
        self.playlist.add_image_changed_callback(callback, self.manager)
        mock_event_trigger(32, self.playlist)

        self.assertNotEqual(callback_called, None)
        name, args = callback_called
        self.assertEqual(name, "image_changed")
        self.assertEqual(len(args), 4)
        self.assertEqual(args[0], self.manager)
        self.assertEqual(type(args[1]), Playlist)
        self.assertEqual(args[1].name(), self.playlist.name())
        self.assertEqual(type(args[2]), bytes)
        self.assertEqual(args[2], '01234567890123456789')
