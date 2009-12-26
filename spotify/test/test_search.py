
import unittest
from spotify._mockspotify import mock_session

class TestSearch(unittest.TestCase):
    
    def test_search_is_loaded(self):
        session = mock_session()
        def _(results,  userdata):
            pass
            #self.assertEqual(results.is_loaded(), False)
        session.search("!loaded", _)
        

"""

def _cb(results):
    for a in results.artists():
        print a.name()
    for a in results.albums():
        print a.name()
        
self.search("year:2003 never", _cb)

"""