# encoding: utf-8

from __future__ import unicode_literals

import platform
import tempfile
import unittest

import spotify
from tests import mock


class ConfigTest(unittest.TestCase):
    def setUp(self):
        self.config = spotify.Config()

    def test_api_version(self):
        self.config.api_version = 71

        self.assertEqual(self.config._sp_session_config.api_version, 71)
        self.assertEqual(self.config.api_version, 71)

    def test_api_version_defaults_to_current_lib_version(self):
        self.assertEqual(self.config.api_version, spotify.lib.SPOTIFY_API_VERSION)

    def test_cache_location(self):
        self.config.cache_location = b"/cache"

        self.assertEqual(
            spotify.ffi.string(self.config._sp_session_config.cache_location),
            b"/cache",
        )
        self.assertEqual(self.config.cache_location, b"/cache")

    def test_cache_location_defaults_to_tmp_in_cwd(self):
        self.assertEqual(self.config.cache_location, b"tmp")

    def test_cache_location_converts_none_to_empty_string(self):
        self.config.cache_location = None

        self.assertEqual(
            spotify.ffi.string(self.config._sp_session_config.cache_location),
            b"",
        )
        self.assertEqual(self.config.cache_location, b"")

    def test_settings_location(self):
        self.config.settings_location = b"/settings"

        self.assertEqual(
            spotify.ffi.string(self.config._sp_session_config.settings_location),
            b"/settings",
        )
        self.assertEqual(self.config.settings_location, b"/settings")

    def test_settings_location_defaults_to_tmp_in_cwd(self):
        self.assertEqual(self.config.settings_location, b"tmp")

    def test_settings_location_converts_none_to_empty_string(self):
        self.config.settings_location = None

        self.assertEqual(
            spotify.ffi.string(self.config._sp_session_config.settings_location),
            b"",
        )
        self.assertEqual(self.config.settings_location, b"")

    def test_application_key(self):
        self.config.application_key = b"\x02" * 321

        self.assertEqual(
            spotify.ffi.string(
                spotify.ffi.cast(
                    "char *", self.config._sp_session_config.application_key
                )
            ),
            b"\x02" * 321,
        )
        self.assertEqual(self.config.application_key, b"\x02" * 321)

    def test_application_key_is_unknown(self):
        self.assertIsNone(self.config.application_key)

    def test_applicaton_key_size_is_zero_by_default(self):
        self.assertEqual(self.config._sp_session_config.application_key_size, 0)

    def test_application_key_size_is_calculated_correctly(self):
        self.config.application_key = b"\x01" * 321

        self.assertEqual(self.config._sp_session_config.application_key_size, 321)

    def test_application_key_can_be_reset_to_none(self):
        self.config.application_key = None

        self.assertIsNone(self.config.application_key)
        self.assertEqual(self.config._sp_session_config.application_key_size, 0)

    def test_application_key_fails_if_invalid_key(self):
        with self.assertRaises(AssertionError):
            self.config.application_key = "way too short key"

    def test_load_application_key_file_can_load_key_from_file(self):
        self.config.application_key = None
        filename = tempfile.mkstemp()[1]
        with open(filename, "wb") as f:
            f.write(b"\x03" * 321)

        self.config.load_application_key_file(filename)

        self.assertEqual(self.config.application_key, b"\x03" * 321)

    def test_load_application_key_file_defaults_to_a_file_in_cwd(self):
        open_mock = mock.mock_open(read_data="\x04" * 321)
        with mock.patch("spotify.config.open", open_mock, create=True) as m:
            self.config.load_application_key_file()

        m.assert_called_once_with(b"spotify_appkey.key", "rb")
        self.assertEqual(self.config.application_key, b"\x04" * 321)

    def test_load_application_key_file_fails_if_no_key_found(self):
        with self.assertRaises(EnvironmentError):
            self.config.load_application_key_file(b"/nonexistant")

    def test_user_agent(self):
        self.config.user_agent = "an agent"

        self.assertEqual(
            spotify.ffi.string(self.config._sp_session_config.user_agent),
            b"an agent",
        )
        self.assertEqual(self.config.user_agent, "an agent")

    def test_user_agent_defaults_to_pyspotify_with_version_number(self):
        self.assertEqual(self.config.user_agent, "pyspotify %s" % spotify.__version__)

    def test_user_agent_location_converts_none_to_empty_string(self):
        self.config.user_agent = None

        self.assertEqual(
            spotify.ffi.string(self.config._sp_session_config.user_agent), b""
        )
        self.assertEqual(self.config.user_agent, "")

    def test_compress_playlists(self):
        self.config.compress_playlists = True

        self.assertEqual(self.config._sp_session_config.compress_playlists, 1)
        self.assertEqual(self.config.compress_playlists, True)

    def test_compress_playlists_defaults_to_false(self):
        self.assertFalse(self.config.compress_playlists)

    def test_dont_save_metadata_for_playlists(self):
        self.config.dont_save_metadata_for_playlists = True

        self.assertEqual(
            self.config._sp_session_config.dont_save_metadata_for_playlists, 1
        )
        self.assertEqual(self.config.dont_save_metadata_for_playlists, True)

    def test_dont_save_metadata_for_playlists_defaults_to_false(self):
        self.assertFalse(self.config.dont_save_metadata_for_playlists)

    def test_initially_unload_playlists(self):
        self.config.initially_unload_playlists = True

        self.assertEqual(self.config._sp_session_config.initially_unload_playlists, 1)
        self.assertEqual(self.config.initially_unload_playlists, True)

    def test_initially_unload_playlists_defaults_to_false(self):
        self.assertFalse(self.config.initially_unload_playlists)

    def test_device_id(self):
        self.config.device_id = "123abc"

        self.assertEqual(
            spotify.ffi.string(self.config._sp_session_config.device_id),
            b"123abc",
        )
        self.assertEqual(self.config.device_id, "123abc")

    def test_device_id_defaults_to_none(self):
        self.assertIsNone(self.config.device_id)

    def test_device_id_converts_empty_string_to_none(self):
        self.config.device_id = ""

        self.assertEqual(self.config._sp_session_config.device_id, spotify.ffi.NULL)
        self.assertIsNone(self.config.device_id)

    def test_proxy(self):
        self.config.proxy = "123abc"

        self.assertEqual(
            spotify.ffi.string(self.config._sp_session_config.proxy), b"123abc"
        )
        self.assertEqual(self.config.proxy, "123abc")

    def test_proxy_defaults_to_none(self):
        self.assertIsNone(self.config.proxy)

    def test_proxy_converts_none_to_empty_string_and_back(self):
        self.config.proxy = None

        self.assertEqual(spotify.ffi.string(self.config._sp_session_config.proxy), b"")
        self.assertIsNone(self.config.proxy)

    def test_proxy_username(self):
        self.config.proxy_username = "123abc"

        self.assertEqual(
            spotify.ffi.string(self.config._sp_session_config.proxy_username),
            b"123abc",
        )
        self.assertEqual(self.config.proxy_username, "123abc")

    def test_proxy_username_defaults_to_none(self):
        self.assertIsNone(self.config.proxy_username)

    def test_proxy_username_converts_none_to_empty_string_and_back(self):
        self.config.proxy_username = None

        self.assertEqual(
            spotify.ffi.string(self.config._sp_session_config.proxy_username),
            b"",
        )
        self.assertIsNone(self.config.proxy_username)

    def test_proxy_password(self):
        self.config.proxy_password = "123abc"

        self.assertEqual(
            spotify.ffi.string(self.config._sp_session_config.proxy_password),
            b"123abc",
        )
        self.assertEqual(self.config.proxy_password, "123abc")

    def test_proxy_password_defaults_to_none(self):
        self.assertIsNone(self.config.proxy_password)

    def test_proxy_password_converts_none_to_empty_string_and_back(self):
        self.config.proxy_password = None

        self.assertEqual(
            spotify.ffi.string(self.config._sp_session_config.proxy_password),
            b"",
        )
        self.assertIsNone(self.config.proxy_password)

    @unittest.skipIf(
        platform.system() == "Darwin",
        "The struct field does not exist in libspotify for macOS",
    )
    def test_ca_certs_filename(self):
        self.config.ca_certs_filename = b"ca.crt"

        self.assertEqual(
            spotify.ffi.string(self.config._get_ca_certs_filename_ptr()[0]),
            b"ca.crt",
        )
        self.assertEqual(self.config.ca_certs_filename, b"ca.crt")

    @unittest.skipIf(
        platform.system() == "Darwin",
        "The struct field does not exist in libspotify for macOS",
    )
    def test_ca_certs_filename_defaults_to_none(self):
        self.assertIsNone(self.config.ca_certs_filename)

    @unittest.skipIf(
        platform.system() != "Darwin", "Not supported on this operating system"
    )
    def test_ca_certs_filename_is_a_noop_on_os_x(self):
        self.assertIsNone(self.config.ca_certs_filename)

        self.config.ca_certs_filename = b"ca.crt"

        self.assertIsNone(self.config.ca_certs_filename)

    def test_tracefile(self):
        self.config.tracefile = b"123abc"

        self.assertEqual(
            spotify.ffi.string(self.config._sp_session_config.tracefile),
            b"123abc",
        )
        self.assertEqual(self.config.tracefile, b"123abc")

    def test_tracefile_defaults_to_none(self):
        self.assertIsNone(self.config.tracefile)

    def test_tracefile_converts_empty_string_to_none(self):
        self.config.tracefile = ""

        self.assertEqual(self.config._sp_session_config.tracefile, spotify.ffi.NULL)
        self.assertIsNone(self.config.tracefile)

    def test_sp_session_config_has_unicode_encoded_as_utf8(self):
        self.config.device_id = "æ device_id"
        self.config.proxy = "æ proxy"
        self.config.proxy_username = "æ proxy_username"
        self.config.proxy_password = "æ proxy_password"
        self.config.tracefile = "æ tracefile".encode("utf-8")

        self.assertEqual(
            spotify.ffi.string(self.config._sp_session_config.device_id),
            b"\xc3\xa6 device_id",
        )
        self.assertEqual(
            spotify.ffi.string(self.config._sp_session_config.proxy),
            b"\xc3\xa6 proxy",
        )
        self.assertEqual(
            spotify.ffi.string(self.config._sp_session_config.proxy_username),
            b"\xc3\xa6 proxy_username",
        )
        self.assertEqual(
            spotify.ffi.string(self.config._sp_session_config.proxy_password),
            b"\xc3\xa6 proxy_password",
        )
        self.assertEqual(
            spotify.ffi.string(self.config._sp_session_config.tracefile),
            b"\xc3\xa6 tracefile",
        )

    @unittest.skipIf(
        platform.system() == "Darwin",
        "The struct field does not exist in libspotify for macOS",
    )
    def test_sp_session_config_ca_certs_filename_has_unicode_encoded_as_utf8(
        self,
    ):

        self.config.ca_certs_filename = "æ ca_certs_filename"

        self.assertEqual(
            spotify.ffi.string(self.config._get_ca_certs_filename_ptr()[0]),
            b"\xc3\xa6 ca_certs_filename",
        )
