# encoding: utf-8

import unittest
from nose.tools import raises

from spotify import _mockspotify
from spotify._mockspotify import mock_album, mock_artist, mock_track, mock_playlist
from spotify import Album

class TestPlaylistContainer(unittest.TestCase):

    def test_len(self):
        p1 = _mockspotify.mock_playlist("foo", [])
        p2 = _mockspotify.mock_playlist("bar", [])
        pc = _mockspotify.mock_playlistcontainer([p1, p2])
        self.assertEqual(len(pc), 2)

    def test_sq_item(self):
        p1 = _mockspotify.mock_playlist("foo", [])
        p2 = _mockspotify.mock_playlist("bar", [])
        pc = _mockspotify.mock_playlistcontainer([p1, p2])
        self.assertEqual(pc[0].name(), "foo")
        self.assertEqual(pc[1].name(), "bar")

    def test_sq_item_exception(self):
        p1 = _mockspotify.mock_playlist("foo", [])
        p2 = _mockspotify.mock_playlist("bar", [])
        pc = _mockspotify.mock_playlistcontainer([p1, p2])
        def _():
            return pc[2]
        self.assertRaises(IndexError, _)

    def test_add_new_playlist(self):
        pc = _mockspotify.mock_playlistcontainer([])
        pc.add_new_playlist('foo');
        pc.add_new_playlist(u'bȧr');
        self.assertRaises(ValueError, pc.add_new_playlist, 'foo' * 100)

class TestPlaylist(unittest.TestCase):

    def _mock_track(self, name):
        return mock_track(name, 0, mock_album("foo", mock_artist("bar", 1),
                                2006, "01234567890123456789", Album.ALBUM, 1, 1),
                                0, 0, 0, 0, 0, 1)

    def test_name(self):
        p1 = _mockspotify.mock_playlist("foo", [])
        self.assertEqual(p1.name(), "foo")

    def test_name_unicode(self):
        p1 = _mockspotify.mock_playlist(u'æâ€êþÿ', [])
        self.assertEqual(p1.name(), u'æâ€êþÿ')

    def test_rename(self):
        p1 = _mockspotify.mock_playlist(u'foo', [])
        p1.rename(u'bar')
        self.assertEqual(p1.name(), u'bar')

    def test_rename_unicode(self):
        p1 = _mockspotify.mock_playlist(u'foo', [])
        p1.rename(u'bąr')
        self.assertEqual(p1.name(), u'bąr')

    @raises(ValueError)
    def test_rename_too_long(self):
        p1 = _mockspotify.mock_playlist(u'foo', [])
        p1.rename(u'bar' * 100)

    def test_len(self):
        p1 = self._mock_track("foo")
        p2 = self._mock_track("bar")
        pc = _mockspotify.mock_playlist("foobar", [p1, p2])
        self.assertEqual(len(pc), 2)

    def test_sq_item(self):
        p1 = self._mock_track("foo")
        p2 = self._mock_track("bar")
        pc = _mockspotify.mock_playlist("foobar", [p1, p2])
        self.assertEqual(pc[0].name(), "foo")
        self.assertEqual(pc[1].name(), "bar")

    def test_add_tracks_ok(self):
        p1 = self._mock_track("foo")
        p2 = self._mock_track("bar")
        pl = mock_playlist("foobar", [p1])
        pl.add_tracks(0, [p2])

    @raises(IndexError)
    def test_add_tracks_wrong_position(self):
        p1 = self._mock_track("foo")
        p2 = self._mock_track("bar")
        pl = mock_playlist("foobar", [p1])
        pl.add_tracks(99, [p2])

    def test_add_tracks_wrong_types(self):
        p1 = self._mock_track("foo")
        pl = mock_playlist("foobar", [p1])
        self.assertRaises(TypeError, pl.add_tracks, 0, True)
        self.assertRaises(TypeError, pl.add_tracks, [False])
