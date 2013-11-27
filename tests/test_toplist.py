from __future__ import unicode_literals

import unittest

import spotify


class ToplistRegionTest(unittest.TestCase):

    def test_has_toplist_region_constants(self):
        self.assertEqual(spotify.ToplistRegion.EVERYWHERE, 0)
        self.assertEqual(spotify.ToplistRegion.USER, 1)


class ToplistTypeTest(unittest.TestCase):

    def test_has_toplist_type_constants(self):
        self.assertEqual(spotify.ToplistType.ARTISTS, 0)
        self.assertEqual(spotify.ToplistType.ALBUMS, 1)
        self.assertEqual(spotify.ToplistType.TRACKS, 2)
