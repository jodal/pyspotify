# $Id$
#
# Copyright 2009 Doug Winter
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at 
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
from spotify._mockspotify import mock_album, mock_artist, Album

class TestAlbum(unittest.TestCase):

    album = mock_album("foo", mock_artist("bar", 1), 2006, "01234567890123456789", Album.ALBUM, 1)

    def test_is_loaded(self):
        self.assertEqual(self.album.is_loaded(), 1)

    def test_name(self):
        self.assertEqual(self.album.name(), "foo")

    def test_artist(self):
        self.assertEqual(self.album.artist().name(), "bar")

    def test_year(self):
        self.assertEqual(self.album.year(), 2006)

    def test_cover(self):
        self.assertEqual(self.album.cover(), "01234567890123456789")

    def test_type(self):
        self.assertEqual(self.album.type(), Album.ALBUM)

