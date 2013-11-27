from __future__ import unicode_literals

import mock
import unittest

import spotify
import tests


@mock.patch('spotify.toplist.lib', spec=spotify.lib)
class ToplistTest(unittest.TestCase):

    def create_session(self, lib_mock):
        session = mock.sentinel.session
        session._sp_session = mock.sentinel.sp_session
        spotify.session_instance = session
        return session

    def test_create_without_type_or_region_or_sp_toplistbrowse_fails(
            self, lib_mock):
        self.assertRaises(AssertionError, spotify.Toplist)

    def test_create_from_type_and_current_user_region(self, lib_mock):
        session = self.create_session(lib_mock)
        sp_toplistbrowse = spotify.ffi.new('int *')
        lib_mock.sp_toplistbrowse_create.return_value = sp_toplistbrowse

        result = spotify.Toplist(
            type=spotify.ToplistType.TRACKS, region=spotify.ToplistRegion.USER)

        lib_mock.sp_toplistbrowse_create.assert_called_with(
            session._sp_session, int(spotify.ToplistType.TRACKS),
            int(spotify.ToplistRegion.USER), spotify.ffi.NULL,
            mock.ANY, mock.ANY)
        self.assertEqual(lib_mock.sp_toplistbrowse_add_ref.call_count, 0)
        self.assertEqual(result._sp_toplistbrowse, sp_toplistbrowse)

    def test_create_from_type_and_specific_user_region(self, lib_mock):
        session = self.create_session(lib_mock)
        sp_toplistbrowse = spotify.ffi.new('int *')
        lib_mock.sp_toplistbrowse_create.return_value = sp_toplistbrowse

        spotify.Toplist(
            type=spotify.ToplistType.TRACKS, region=spotify.ToplistRegion.USER,
            canonical_username='alice')

        lib_mock.sp_toplistbrowse_create.assert_called_with(
            session._sp_session, int(spotify.ToplistType.TRACKS),
            int(spotify.ToplistRegion.USER), mock.ANY, mock.ANY, mock.ANY)
        self.assertEqual(
            spotify.ffi.string(
                lib_mock.sp_toplistbrowse_create.call_args[0][3]),
            b'alice')

    def test_create_from_type_and_country(self, lib_mock):
        session = self.create_session(lib_mock)
        sp_toplistbrowse = spotify.ffi.new('int *')
        lib_mock.sp_toplistbrowse_create.return_value = sp_toplistbrowse

        spotify.Toplist(
            type=spotify.ToplistType.TRACKS, region='NO')

        lib_mock.sp_toplistbrowse_create.assert_called_with(
            session._sp_session, int(spotify.ToplistType.TRACKS),
            20047, spotify.ffi.NULL, mock.ANY, mock.ANY)

    def test_create_with_callback(self, lib_mock):
        self.create_session(lib_mock)
        sp_toplistbrowse = spotify.ffi.cast(
            'sp_toplistbrowse *', spotify.ffi.new('int *'))
        lib_mock.sp_toplistbrowse_create.return_value = sp_toplistbrowse
        callback = mock.Mock()

        result = spotify.Toplist(
            type=spotify.ToplistType.TRACKS, region=spotify.ToplistRegion.USER,
            callback=callback)

        toplistbrowse_complete_cb = (
            lib_mock.sp_toplistbrowse_create.call_args[0][4])
        userdata = lib_mock.sp_toplistbrowse_create.call_args[0][5]
        toplistbrowse_complete_cb(sp_toplistbrowse, userdata)

        result.complete_event.wait(3)
        callback.assert_called_with(result)

    def test_toplist_is_gone_before_callback_is_called(self, lib_mock):
        self.create_session(lib_mock)
        sp_toplistbrowse = spotify.ffi.cast(
            'sp_toplistbrowse *', spotify.ffi.new('int *'))
        lib_mock.sp_toplistbrowse_create.return_value = sp_toplistbrowse
        callback = mock.Mock()

        result = spotify.Toplist(
            type=spotify.ToplistType.TRACKS, region=spotify.ToplistRegion.USER,
            callback=callback)
        complete_event = result.complete_event
        result = None  # noqa
        tests.gc_collect()

        # FIXME The mock keeps the handle/userdata alive, thus the toplist is
        # kept alive, and this test doesn't test what it is intended to test.
        toplistbrowse_complete_cb = (
            lib_mock.sp_toplistbrowse_create.call_args[0][4])
        userdata = lib_mock.sp_toplistbrowse_create.call_args[0][5]
        toplistbrowse_complete_cb(sp_toplistbrowse, userdata)

        complete_event.wait(3)
        self.assertEqual(callback.call_count, 1)
        self.assertEqual(
            callback.call_args[0][0]._sp_toplistbrowse, sp_toplistbrowse)

    def test_adds_ref_to_sp_toplistbrowse_when_created(self, lib_mock):
        sp_toplistbrowse = spotify.ffi.new('int *')

        spotify.Toplist(sp_toplistbrowse=sp_toplistbrowse)

        lib_mock.sp_toplistbrowse_add_ref.assert_called_once_with(
            sp_toplistbrowse)

    def test_releases_sp_toplistbrowse_when_toplist_dies(self, lib_mock):
        sp_toplistbrowse = spotify.ffi.new('int *')

        toplist = spotify.Toplist(sp_toplistbrowse=sp_toplistbrowse)
        toplist = None  # noqa
        tests.gc_collect()

        lib_mock.sp_toplistbrowse_release.assert_called_with(sp_toplistbrowse)

    def test_repr(self, lib_mock):
        pass  # TODO

    def test_is_loaded(self, lib_mock):
        lib_mock.sp_toplistbrowse_is_loaded.return_value = 1
        sp_toplistbrowse = spotify.ffi.new('int *')
        toplist = spotify.Toplist(sp_toplistbrowse=sp_toplistbrowse)

        result = toplist.is_loaded

        lib_mock.sp_toplistbrowse_is_loaded.assert_called_once_with(
            sp_toplistbrowse)
        self.assertTrue(result)

    @mock.patch('spotify.utils.load')
    def test_load(self, load_mock, lib_mock):
        sp_toplistbrowse = spotify.ffi.new('int *')
        toplist = spotify.Toplist(sp_toplistbrowse=sp_toplistbrowse)

        toplist.load(10)

        load_mock.assert_called_with(toplist, timeout=10)


class ToplistRegionTest(unittest.TestCase):

    def test_has_toplist_region_constants(self):
        self.assertEqual(spotify.ToplistRegion.EVERYWHERE, 0)
        self.assertEqual(spotify.ToplistRegion.USER, 1)


class ToplistTypeTest(unittest.TestCase):

    def test_has_toplist_type_constants(self):
        self.assertEqual(spotify.ToplistType.ARTISTS, 0)
        self.assertEqual(spotify.ToplistType.ALBUMS, 1)
        self.assertEqual(spotify.ToplistType.TRACKS, 2)
