# encoding: utf-8

from __future__ import unicode_literals

import unittest
from distutils.version import StrictVersion as SV

import spotify
from tests import mock


class VersionTest(unittest.TestCase):
    def test_version_is_a_valid_pep_386_strict_version(self):
        SV(spotify.__version__)

    def test_version_is_grater_than_all_1_x_versions(self):
        self.assertLess(SV("1.999"), SV(spotify.__version__))


@mock.patch("spotify.version.lib", spec=spotify.lib)
class LibspotifyVersionTest(unittest.TestCase):
    def test_libspotify_api_version(self, lib_mock):
        lib_mock.SPOTIFY_API_VERSION = 73

        result = spotify.get_libspotify_api_version()

        self.assertEqual(result, 73)

    def test_libspotify_build_id(self, lib_mock):
        build_id = spotify.ffi.new("char []", "12.1.51.foobaræøå".encode("utf-8"))
        lib_mock.sp_build_id.return_value = build_id

        result = spotify.get_libspotify_build_id()

        self.assertEqual(result, "12.1.51.foobaræøå")
