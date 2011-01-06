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
from spotify._mockspotify import mock_session

session = mock_session()

class TestSearch(unittest.TestCase):
    
    def test_search_is_loaded(self):
        global is_loaded
        is_loaded = None
        def _(results,  userdata):
            global is_loaded
            is_loaded = results.is_loaded()
        session.search("!loaded", _)
        self.assertEqual(is_loaded, False)
        session.search("loaded", _)
        self.assertEqual(is_loaded, True)
        
    def test_artists(self):
        global artists
        artists = None
        def _(results, userdata):
            global artists
            artists = results.artists()
        session.search("", _)
        self.assertEqual(artists[0].name(), "foo")
        self.assertEqual(artists[1].name(), "bar")
        
    def test_albums(self):
        global result
        result = None
        def _(search, userdata):
            global result
            result = search.albums()
        session.search("", _)
        self.assertEqual(result[0].name(), "baz")
        self.assertEqual(result[1].name(), "qux")
        self.assertEqual(result[2].name(), "quux")

    def test_tracks(self):
        global result
        result = None
        def _(search, userdata):
            global result
            result = search.tracks()
        session.search("", _)
        self.assertEqual(result[0].name(), "corge")
        self.assertEqual(result[1].name(), "grault")
        self.assertEqual(result[2].name(), "garply")
        self.assertEqual(result[3].name(), "waldo")

    def test_query(self):
        global result
        result = None
        def _(search, userdata):
            global result
            result = search.query()
        session.search("foo", _)
        self.assertEqual(result, "foo")
       
    def test_error(self):
        global result
        result = None
        def _(search, userdata):
            global result
            result = search.error()
        session.search("foo", _)
        self.assertEqual(result, 3)

    def test_did_you_mean(self):
        global result
        result = None
        def _(search, userdata):
            global result
            result = search.did_you_mean()
        session.search("foo", _)
        self.assertEqual(result, "did_you_mean")

    def test_total_tracks(self):
        global result
        result = None
        def _(search, userdata):
            global result
            result = search.total_tracks()
        session.search("foo", _)
        self.assertEqual(result, 24)
        