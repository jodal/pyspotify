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
from spotify._mockspotify import Artist, mock_artist

class TestArtist(unittest.TestCase):

    def test_str(self):
        artist = mock_artist("test_name", 1)
        self.assertEqual(str(artist), "test_name")


    def test_is_loaded(self):
        artist = mock_artist("test_name", 1)
        self.assertEqual(artist.is_loaded(), 1)
        artist = mock_artist("test_name", 0)
        self.assertEqual(artist.is_loaded(), 0)

    def test_name(self):
        artist = mock_artist("test_name", 1)
        self.assertEqual(artist.name(), "test_name")

