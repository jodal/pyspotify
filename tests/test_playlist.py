# encoding: utf-8

import unittest
from nose.tools import raises

from spotify._mockspotify import mock_album, mock_artist, mock_track, mock_playlist
from spotify._mockspotify import mock_playlistcontainer, mock_user, Album
from spotify._mockspotify import mock_session, mock_set_current_session
from spotify._mockspotify import mock_playlistfolder

class TestPlaylistContainer(unittest.TestCase):

    owner = mock_user('owner')
    p1 = mock_playlist('foo', [], owner)
    p2 = mock_playlist('bar', [], owner)

    def test_len(self):
        pc = mock_playlistcontainer(self.owner, [self.p1, self.p2])
        self.assertEqual(len(pc), 2)

    def test_sq_item(self):
        pc = mock_playlistcontainer(self.owner, [self.p1, self.p2])
        self.assertEqual(pc[0].name(), "foo")
        self.assertEqual(pc[1].name(), "bar")

    def test_sq_item_exception(self):
        pc = mock_playlistcontainer(self.owner, [self.p1, self.p2])
        def _():
            return pc[2]
        self.assertRaises(IndexError, _)

    def test_add_new_playlist(self):
        pc = mock_playlistcontainer(self.owner, [])
        pc.add_new_playlist('foo');
        self.assertRaises(ValueError, pc.add_new_playlist, 'foo' * 100)

    def test_playlistfolder(self):
        p1 = mock_playlistfolder("folder_start", "foo", folder_id=42)
        p2 = mock_playlistfolder("folder_end", "")
        pc = mock_playlistcontainer(self.owner, [p1, p2])
        f1,f2  = pc[0],pc[1]
        self.assertEqual(f1.name(), u'foo')
        self.assertEqual(f1.type(), 'folder_start')
        self.assertEqual(f2.type(), 'folder_end')
        self.assertEqual(f1.id(), 42)
        self.assertTrue(f1.is_loaded())

class TestPlaylist(unittest.TestCase):

    artist = mock_artist('artist')
    album = mock_album('album', artist)
    owner = mock_user('owner')
    tracks = [
        (mock_track('track1', [artist], album), owner, 1320961109),
        (mock_track('track2', [artist], album), owner, 1320961109),
        (mock_track('track3', [artist], album), owner, 1320961109),
    ]
    pure_tracks = [t[0] for t in tracks]
    session = mock_session()

    def setUp(self):
        mock_set_current_session(self.session)

    def tearDown(self):
        mock_set_current_session(None)

    def test_name(self):
        playlist = mock_playlist('playlist', [], self.owner)
        self.assertEqual(playlist.name(), 'playlist')

    def test_name_unicode(self):
        playlist = mock_playlist(u'plåylïst', [], self.owner)
        self.assertEqual(playlist.name(), u'plåylïst')

    def test_rename(self):
        playlist = mock_playlist(u'foo', [], self.owner)
        playlist.rename(u'bar')
        self.assertEqual(playlist.name(), u'bar')

    def test_rename_unicode(self):
        playlist = mock_playlist(u'foo', [], self.owner)
        playlist.rename(u'bąr')
        self.assertEqual(playlist.name(), u'bąr')

    @raises(ValueError)
    def test_rename_too_long(self):
        playlist = mock_playlist(u'foo', [], self.owner)
        playlist.rename(u'bar' * 100)

    def test_len(self):
        playlist = mock_playlist(u'foo', self.tracks, self.owner)
        self.assertEqual(len(playlist), 3)

    def test_sq_item(self):
        playlist = mock_playlist(u'foo', self.tracks, self.owner)
        self.assertEqual(playlist[0].name(), 'track1')
        self.assertEqual(playlist[1].name(), 'track2')
        self.assertEqual(playlist[2].name(), 'track3')

    def test_num_subscribers(self):
        playlist = mock_playlist('foo', [], self.owner, num_subscribers=42)
        self.assertEqual(playlist.num_subscribers(), 42)

    def test_subscribers(self):
        playlist = mock_playlist(u'foo', [], self.owner,
                                 subscribers=['foo', 'bar', 'baz'])
        self.assertEqual(playlist.subscribers(), [u'foo', u'bar', u'baz'])

    def test_add_tracks_ok(self):
        playlist = mock_playlist(u'foo', [], self.owner)
        playlist.add_tracks(0, self.pure_tracks)

    @raises(IndexError)
    def test_add_tracks_wrong_position(self):
        playlist = mock_playlist('foo', [], self.owner)
        playlist.add_tracks(99, self.pure_tracks)

    def test_add_tracks_wrong_types(self):
        playlist = mock_playlist('foo', [], self.owner)
        self.assertRaises(TypeError, playlist.add_tracks, 0, True)
        self.assertRaises(TypeError, playlist.add_tracks, [False])

    def test_track_create_time(self):
        playlist = mock_playlist('foo', self.tracks, self.owner)
        self.assertEqual(playlist.track_create_time(0), 1320961109)

    def test_owner(self):
        playlist = mock_playlist('foo', [], self.owner)
        self.assertEqual(playlist.owner().canonical_name(),
                         self.owner.canonical_name())
