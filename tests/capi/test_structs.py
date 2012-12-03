import ctypes
import unittest

from spotify import capi

class CAPIStructsTest(unittest.TestCase):
    def assertHasStruct(self, struct_name):
        self.assert_(hasattr(capi, struct_name),
            'spotify.capi should have %s struct' % struct_name)

    def test_sp_uint64_is_a_ctypes_c_uint64(self):
        self.assertEqual(capi.sp_uint64, ctypes.c_uint64)

    def test_sp_bool_is_a_ctypes_c_ubyte(self):
        self.assertEqual(capi.sp_bool, ctypes.c_ubyte)

    def test_has_sp_session_struct(self):
        self.assertHasStruct('sp_session')

    def test_has_sp_track_struct(self):
        self.assertHasStruct('sp_track')

    def test_has_sp_album_struct(self):
        self.assertHasStruct('sp_album')

    def test_has_sp_artist_struct(self):
        self.assertHasStruct('sp_artist')

    def test_has_sp_artistbrowse_struct(self):
        self.assertHasStruct('sp_artistbrowse')

    def test_has_sp_albumbrowse_struct(self):
        self.assertHasStruct('sp_albumbrowse')

    def test_has_sp_toplistbrowse_struct(self):
        self.assertHasStruct('sp_toplistbrowse')

    def test_has_sp_search_struct(self):
        self.assertHasStruct('sp_search')

    def test_has_sp_link_struct(self):
        self.assertHasStruct('sp_link')

    def test_has_sp_image_struct(self):
        self.assertHasStruct('sp_image')

    def test_has_sp_user_struct(self):
        self.assertHasStruct('sp_user')

    def test_has_sp_playlist_struct(self):
        self.assertHasStruct('sp_playlist')

    def test_has_sp_playlistcontainer_struct(self):
        self.assertHasStruct('sp_playlistcontainer')

    def test_has_sp_inbox_struct(self):
        self.assertHasStruct('sp_inbox')
