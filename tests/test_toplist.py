import unittest
from spotify._mockspotify import ToplistBrowser

callback_called = False
callback_userdata = None

def callback(toplist, userdata):
    global callback_called
    global callback_userdata
    callback_called = True
    callback_userdata = userdata

class TestToplist(unittest.TestCase):

    def test_is_loaded(self):
        browser = ToplistBrowser('tracks', 'FR')
        self.assertTrue(browser.is_loaded())

    def test_sequence_albums(self):
        browser = ToplistBrowser('albums', 'FR')
        self.assertEqual(len(browser),3)
        self.assertEqual(browser[0].name(), 'foo')
        self.assertEqual(browser[1].name(), 'bar')
        self.assertEqual(browser[2].name(), 'baz')

    def test_sequence_artists(self):
        browser = ToplistBrowser('artists', 'FR')
        self.assertEqual(len(browser),3)
        self.assertEqual(browser[0].name(), 'foo')
        self.assertEqual(browser[1].name(), 'bar')
        self.assertEqual(browser[2].name(), 'baz')

    def test_sequence_tracks(self):
        browser = ToplistBrowser('tracks', 'FR')
        self.assertEqual(len(browser),3)
        self.assertEqual(browser[0].name(), 'foo')
        self.assertEqual(browser[1].name(), 'bar')
        self.assertEqual(browser[2].name(), 'baz')

    def test_callback(self):
        global callback_called
        global callback_userdata
        callback_called = False
        browser = ToplistBrowser('tracks', 'FR', callback, self)
        self.assertTrue(callback_called)
        self.assertEqual(callback_userdata, self)
