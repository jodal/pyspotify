from __future__ import unicode_literals

import unittest

import spotify


class LibTest(unittest.TestCase):
    def test_sp_error_message(self):
        self.assertEqual(
            spotify.ffi.string(spotify.lib.sp_error_message(0)),
            b'No error')
