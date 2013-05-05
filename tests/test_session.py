from __future__ import unicode_literals

import mock
import unittest

import spotify


class SessionCallbacksTest(unittest.TestCase):
    def setUp(self):
        self.callbacks = spotify.SessionCallbacks()
        self.sp_session = spotify.ffi.new('sp_session **')[0]
        self.sp_error = 1

    def test_logged_in_callback(self):
        self.callbacks.logged_in = mock.Mock()

        self.callbacks._logged_in(self.sp_session, self.sp_error)

        self.callbacks.logged_in.assert_called_once_with(
            spotify.Session(self.sp_session), spotify.Error(self.sp_error))

    def test_logged_out_callback(self):
        self.callbacks.logged_out = mock.Mock()

        self.callbacks._logged_out(self.sp_session)

        self.callbacks.logged_out.assert_called_once_with(
            spotify.Session(self.sp_session))

    def test_metadata_updated_callback(self):
        self.callbacks.metadata_updated = mock.Mock()

        self.callbacks._metadata_updated(self.sp_session)

        self.callbacks.metadata_updated.assert_called_once_with(
            spotify.Session(self.sp_session))

    def test_connection_error_callback(self):
        self.callbacks.connection_error = mock.Mock()

        self.callbacks._connection_error(self.sp_session, self.sp_error)

        self.callbacks.connection_error.assert_called_once_with(
            spotify.Session(self.sp_session), spotify.Error(self.sp_error))

    def test_notify_main_thread_callback(self):
        self.callbacks.notify_main_thread = mock.Mock()

        self.callbacks._notify_main_thread(self.sp_session)

        self.callbacks.notify_main_thread.assert_called_once_with(
            spotify.Session(self.sp_session))

    def test_log_message_callback(self):
        self.callbacks.log_message = mock.Mock()
        data = spotify.ffi.new('char[]', b'a log message\n')

        self.callbacks._log_message(self.sp_session, data)

        self.callbacks.log_message.assert_called_once_with(
            spotify.Session(self.sp_session), u'a log message')

    def test_offline_status_updated_callback(self):
        self.callbacks.offline_status_updated = mock.Mock()

        self.callbacks._offline_status_updated(self.sp_session)

        self.callbacks.offline_status_updated.assert_called_once_with(
            spotify.Session(self.sp_session))

    def test_credentials_blob_updated_callback(self):
        self.callbacks.credentials_blob_updated = mock.Mock()
        data = spotify.ffi.new('char[]', b'a credentials blob')

        self.callbacks._credentials_blob_updated(self.sp_session, data)

        self.callbacks.credentials_blob_updated.assert_called_once_with(
            spotify.Session(self.sp_session), b'a credentials blob')
