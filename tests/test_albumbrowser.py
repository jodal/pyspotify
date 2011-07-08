import unittest
from spotify._mockspotify import mock_albumbrowse, mock_album, mock_artist
from spotify._mockspotify import mock_session
from spotify import Album

callback_called = False
callback_userdata = None

class TestAlbumbrowser(unittest.TestCase):

    session = mock_session()
    album = mock_album("foo0", mock_artist("bar0", 1), 2006,
                               "01234567890123456789", Album.ALBUM, 1, 1)

    def callback(self, browser, userdata):
        global callback_called
        global callback_userdata
        callback_called = True
        callback_userdata = userdata

    def test_is_loaded(self):
        browser = mock_albumbrowse(self.session, self.album, 1, self.callback)
        assert browser.is_loaded()

    def test_is_not_loaded(self):
        browser = mock_albumbrowse(self.session, self.album, 0, self.callback)
        assert not browser.is_loaded()

    def test_sequence(self):
        browser = mock_albumbrowse(self.session, self.album, 1, self.callback)
        assert len(browser) == 3
        assert browser[0].name() == 'foo'
        assert browser[1].name() == 'bar'
        assert browser[2].name() == 'baz'

    def test_callback(self):
        global callback_called
        global callback_userdata
        callback_called = False
        browser = mock_albumbrowse(self.session, self.album, 0, self.callback,
                                   self)
        self.assertTrue(callback_called)
        self.assertEqual(callback_userdata, self)
