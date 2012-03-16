import ctypes as _ctypes

SPOTIFY_API_VERSION = 10

_libspotify = _ctypes.CDLL('libspotify.so.%s' % SPOTIFY_API_VERSION)


### Spotify types & structs

sp_uint64 = _ctypes.c_uint64
sp_bool = _ctypes.c_ubyte

class sp_session(_ctypes.Structure):
    pass

class sp_track(_ctypes.Structure):
    pass

class sp_album(_ctypes.Structure):
    pass

class sp_artist(_ctypes.Structure):
    pass

class sp_artistbrowse(_ctypes.Structure):
    pass

class sp_albumbrowse(_ctypes.Structure):
    pass

class sp_toplistbrowse(_ctypes.Structure):
    pass

class sp_search(_ctypes.Structure):
    pass

class sp_link(_ctypes.Structure):
    pass

class sp_image(_ctypes.Structure):
    pass

class sp_user(_ctypes.Structure):
    pass

class sp_playlist(_ctypes.Structure):
    pass

class sp_playlistcontainer(_ctypes.Structure):
    pass

class sp_inbox(_ctypes.Structure):
    pass


### Error handling

sp_error = _ctypes.c_uint

SP_ERROR_OK = 0
SP_ERROR_BAD_API_VERSION = 1
SP_ERROR_API_INITIALIZATION_FAILED = 2
SP_ERROR_TRACK_NOT_PLAYABLE = 3
SP_ERROR_BAD_APPLICATION_KEY = 5
SP_ERROR_BAD_USERNAME_OR_PASSWORD = 6
SP_ERROR_USER_BANNED = 7
SP_ERROR_UNABLE_TO_CONTACT_SERVER = 8
SP_ERROR_CLIENT_TOO_OLD = 9
SP_ERROR_OTHER_PERMANENT = 10
SP_ERROR_BAD_USER_AGENT = 11
SP_ERROR_MISSING_CALLBACK = 12
SP_ERROR_INVALID_INDATA = 13
SP_ERROR_INDEX_OUT_OF_RANGE = 14
SP_ERROR_USER_NEEDS_PREMIUM = 15
SP_ERROR_OTHER_TRANSIENT = 16
SP_ERROR_IS_LOADING = 17
SP_ERROR_NO_STREAM_AVAILABLE = 18
SP_ERROR_PERMISSION_DENIED = 19
SP_ERROR_INBOX_IS_FULL = 20
SP_ERROR_NO_CACHE = 21
SP_ERROR_NO_SUCH_USER = 22
SP_ERROR_NO_CREDENTIALS = 23
SP_ERROR_NETWORK_DISABLED = 24
SP_ERROR_INVALID_DEVICE_ID = 25
SP_ERROR_CANT_OPEN_TRACE_FILE = 26
SP_ERROR_APPLICATION_BANNED = 27
SP_ERROR_OFFLINE_TOO_MANY_TRACKS = 31
SP_ERROR_OFFLINE_DISK_CACHE = 32
SP_ERROR_OFFLINE_EXPIRED = 33
SP_ERROR_OFFLINE_NOT_ALLOWED = 34
SP_ERROR_OFFLINE_LICENSE_LOST = 35
SP_ERROR_OFFLINE_LICENSE_ERROR = 36

_sp_error_message = _libspotify.sp_error_message
_sp_error_message.argtypes = [sp_error]
_sp_error_message.restype = _ctypes.c_char_p

def sp_error_message(error):
    return _sp_error_message(error).decode('utf-8')
