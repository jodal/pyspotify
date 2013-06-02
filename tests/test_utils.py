# encoding: utf-8

from __future__ import unicode_literals

import unittest

from spotify import utils


class ToBytesTest(unittest.TestCase):

    def test_unicode_to_bytes_is_encoded_as_utf8(self):
        self.assertEqual(utils.to_bytes('æøå'), 'æøå'.encode('utf-8'))

    def test_bytes_to_bytes_is_passed_through(self):
        self.assertEqual(
            utils.to_bytes('æøå'.encode('utf-8')), 'æøå'.encode('utf-8'))

    def test_anything_else_to_bytes_fails(self):
        self.assertRaises(ValueError, utils.to_bytes, [])
        self.assertRaises(ValueError, utils.to_bytes, 123)
