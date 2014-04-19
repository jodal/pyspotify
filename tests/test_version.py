from __future__ import unicode_literals

from distutils.version import StrictVersion as SV
import unittest

import spotify


class VersionTest(unittest.TestCase):

    def test_version_is_a_valid_pep_386_strict_version(self):
        SV(spotify.__version__)

    def test_version_is_grater_than_all_1_x_versions(self):
        self.assertLess(SV('1.999'), SV(spotify.__version__))
