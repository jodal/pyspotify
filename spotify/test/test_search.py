
import unittest
from spotify._mockspotify import mock_session

class TestSearch(unittest.TestCase):
    
    def test_search_is_loaded(self):
        session = mock_session()
        def _(results,  userdata):
            print "Callback called"
            pass
            #self.assertEqual(results.is_loaded(), False)
        session.search("!loaded", _)
        