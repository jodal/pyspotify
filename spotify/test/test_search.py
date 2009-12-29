
import unittest
from spotify._mockspotify import mock_session

class TestSearch(unittest.TestCase):
    
    def test_search_is_loaded(self):
        global is_loaded
        session = mock_session()
        is_loaded = None
        def _(results,  userdata):
            global is_loaded
            is_loaded = results.is_loaded()
        session.search("!loaded", _)
        self.assertEqual(is_loaded, False)
        session.search("loaded", _)
        self.assertEqual(is_loaded, True)
    