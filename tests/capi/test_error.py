import ctypes
import unittest

from spotify import capi

class CAPIErrorTest(unittest.TestCase):
    def test_sp_error_enum_has_correct_enumeration(self):
        self.assertEqual(capi.SP_ERROR_OK, 0)
        self.assertEqual(capi.SP_ERROR_BAD_API_VERSION, 1)
        self.assertEqual(capi.SP_ERROR_API_INITIALIZATION_FAILED, 2)
        self.assertEqual(capi.SP_ERROR_TRACK_NOT_PLAYABLE, 3)
        self.assertEqual(capi.SP_ERROR_BAD_APPLICATION_KEY, 5)
        self.assertEqual(capi.SP_ERROR_BAD_USERNAME_OR_PASSWORD, 6)
        self.assertEqual(capi.SP_ERROR_USER_BANNED, 7)
        self.assertEqual(capi.SP_ERROR_UNABLE_TO_CONTACT_SERVER, 8)
        self.assertEqual(capi.SP_ERROR_CLIENT_TOO_OLD, 9)
        self.assertEqual(capi.SP_ERROR_OTHER_PERMANENT, 10)
        self.assertEqual(capi.SP_ERROR_BAD_USER_AGENT, 11)
        self.assertEqual(capi.SP_ERROR_MISSING_CALLBACK, 12)
        self.assertEqual(capi.SP_ERROR_INVALID_INDATA, 13)
        self.assertEqual(capi.SP_ERROR_INDEX_OUT_OF_RANGE, 14)
        self.assertEqual(capi.SP_ERROR_USER_NEEDS_PREMIUM, 15)
        self.assertEqual(capi.SP_ERROR_OTHER_TRANSIENT, 16)
        self.assertEqual(capi.SP_ERROR_IS_LOADING, 17)
        self.assertEqual(capi.SP_ERROR_NO_STREAM_AVAILABLE, 18)
        self.assertEqual(capi.SP_ERROR_PERMISSION_DENIED, 19)
        self.assertEqual(capi.SP_ERROR_INBOX_IS_FULL, 20)
        self.assertEqual(capi.SP_ERROR_NO_CACHE, 21)
        self.assertEqual(capi.SP_ERROR_NO_SUCH_USER, 22)
        self.assertEqual(capi.SP_ERROR_NO_CREDENTIALS, 23)
        self.assertEqual(capi.SP_ERROR_NETWORK_DISABLED, 24)
        self.assertEqual(capi.SP_ERROR_INVALID_DEVICE_ID, 25)
        self.assertEqual(capi.SP_ERROR_CANT_OPEN_TRACE_FILE, 26)
        self.assertEqual(capi.SP_ERROR_APPLICATION_BANNED, 27)
        self.assertEqual(capi.SP_ERROR_OFFLINE_TOO_MANY_TRACKS, 31)
        self.assertEqual(capi.SP_ERROR_OFFLINE_DISK_CACHE, 32)
        self.assertEqual(capi.SP_ERROR_OFFLINE_EXPIRED, 33)
        self.assertEqual(capi.SP_ERROR_OFFLINE_NOT_ALLOWED, 34)
        self.assertEqual(capi.SP_ERROR_OFFLINE_LICENSE_LOST, 35)
        self.assertEqual(capi.SP_ERROR_OFFLINE_LICENSE_ERROR, 36)

    def test_sp_error_message_returns_error_message_as_unicode(self):
        msg = capi.sp_error_message(capi.SP_ERROR_OK)
        self.assertEqual(msg, u'No error')
        self.assertIsInstance(msg, unicode)

    def test_sp_error_message_returns_error_message_for_unknown_error_no(self):
        msg = capi.sp_error_message(999)
        self.assertEqual(msg, u'invalid error code')

    def test_sp_error_message_raises_exc_on_wrong_arg_type(self):
        self.assertRaises(ctypes.ArgumentError, capi.sp_error_message, 'a string')
