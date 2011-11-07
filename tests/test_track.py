# encoding: utf-8

import unittest
from spotify._mockspotify import mock_track, mock_album, mock_artist, mock_session

class TestTrack(unittest.TestCase):

    track = mock_track(u'æâ€êþÿ', 3, mock_album("bar", mock_artist("baz", 1), 0, "",
                                            0, 1, 1), 10, 20, 30, 40, 0, 1)

    def test_artists(self):
        self.assertEqual([x.name() for x in self.track.artists()], ["a1", "a2", "a3"])

    def test_album(self):
        self.assertEqual(self.track.album().name(), "bar")

    def test_name(self):
        self.assertEqual(self.track.name(), u'æâ€êþÿ')

    def test_duration(self):
        self.assertEqual(self.track.duration(), 10)

    def test_popularity(self):
        self.assertEqual(self.track.popularity(), 20)

    def test_disc(self):
        self.assertEqual(self.track.disc(), 30)

    def test_index(self):
        self.assertEqual(self.track.index(), 40)

    def test_error(self):
        self.assertEqual(self.track.error(), 0)

    def test_is_loaded(self):
        self.assertEqual(self.track.is_loaded(), 1)

    def test_starred(self):
        session = mock_session()
        self.assertEqual(self.track.starred(session), False)
        self.track.starred(session, set=True)
        self.assertEqual(self.track.starred(session), True)
        self.track.starred(session, set=False)
        self.assertEqual(self.track.starred(session), False)

    def test_availability(self):
        self.assertEqual(self.track.availability(), 1)

    def test_is_local(self):
        self.assertFalse(self.track.is_local())
