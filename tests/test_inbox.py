from __future__ import unicode_literals

import mock
import unittest

import spotify
import tests


@mock.patch('spotify.inbox.lib', spec=spotify.lib)
class InboxPostResultTest(unittest.TestCase):

    def test_adds_ref_to_sp_inbox_when_created(self, lib_mock):
        sp_inbox = spotify.ffi.new('int *')

        spotify.InboxPostResult(sp_inbox=sp_inbox)

        lib_mock.sp_inbox_add_ref.assert_called_with(sp_inbox)

    def test_releases_sp_inbox_when_result_dies(self, lib_mock):
        sp_inbox = spotify.ffi.new('int *')

        inbox_post_result = spotify.InboxPostResult(sp_inbox=sp_inbox)
        inbox_post_result = None  # noqa
        tests.gc_collect()

        lib_mock.sp_inbox_release.assert_called_with(sp_inbox)

    def test_error(self, lib_mock):
        lib_mock.sp_inbox_error.return_value = int(
            spotify.ErrorType.INBOX_IS_FULL)
        sp_inbox = spotify.ffi.new('int *')
        inbox_post_result = spotify.InboxPostResult(sp_inbox=sp_inbox)

        result = inbox_post_result.error

        lib_mock.sp_inbox_error.assert_called_once_with(sp_inbox)
        self.assertIs(result, spotify.ErrorType.INBOX_IS_FULL)
