import unittest
from spotify._mockspotify import Link

class TestLink(unittest.TestCase):

    def test_from_string(self):
        s = "from_string_test"
        l = Link.from_string(s)
        self.assertEqual(str(l), "link:" + s)



