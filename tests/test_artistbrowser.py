#
# Copyright 2011 Antoine Pierlot-Garcin
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
from spotify._mockspotify import mock_artistbrowse, mock_artist, mock_session

callback_called = False
callback_userdata = None

class TestAlbumbrowser(unittest.TestCase):

    session = mock_session()
    artist = mock_artist("foo0", 1)

    def callback(browser, userdata):
        callback_called = True
        callback_userdata = userdata

    def test_is_loaded(self):
        browser = mock_artistbrowse(self.session, self.artist, 1, self.callback)
        assert browser.is_loaded()

    def test_is_not_loaded(self):
        browser = mock_artistbrowse(self.session, self.artist, 0, self.callback)
        assert not browser.is_loaded()

    def test_sequence(self):
        browser = mock_artistbrowse(self.session, self.artist, 1, self.callback)
        assert len(browser) == 3
        assert browser[0].name() == 'foo'
        assert browser[1].name() == 'bar'
        assert browser[2].name() == 'baz'

    def test_callback(self):
        callback_called = False
        browser = mock_artistbrowse(self.session, self.artist, 0, self.callback,
                                   self)
        assert callback_called
        assert userdata is self
