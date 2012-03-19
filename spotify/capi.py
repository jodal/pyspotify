import os as _os
import ctypes as _ctypes

SPOTIFY_API_VERSION = 10

if _os.environ.get('USE_LIBMOCKSPOTIFY'):
    _libspotify = _ctypes.CDLL('libmockspotify.so.0')
else:
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

sp_error = _ctypes.c_int

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


### Session handling

SP_CONNECTION_STATE_LOGGED_OUT = 0
SP_CONNECTION_STATE_LOGGED_IN = 1
SP_CONNECTION_STATE_DISCONNECTED = 2
SP_CONNECTION_STATE_UNDEFINED = 3
SP_CONNECTION_STATE_OFFLINE = 4

sp_sampletype = _ctypes.c_int

SP_SAMPLETYPE_INT16_NATIVE_ENDIAN = 0

class sp_audioformat(_ctypes.Structure):
    _fields_ = [
        ('sample_type', sp_sampletype),
        ('sample_rate', _ctypes.c_int),
        ('channels', _ctypes.c_int),
    ]

SP_BITRATE_160k = 0
SP_BITRATE_320k = 1
SP_BITRATE_96k = 2

SP_PLAYLIST_TYPE_PLAYLIST = 0
SP_PLAYLIST_TYPE_START_FOLDER = 1
SP_PLAYLIST_TYPE_END_FOLDER = 2
SP_PLAYLIST_TYPE_PLACEHOLDER = 3

SP_PLAYLIST_OFFLINE_STATUS_NO = 0
SP_PLAYLIST_OFFLINE_STATUS_YES = 1
SP_PLAYLIST_OFFLINE_STATUS_DOWNLOADING = 2
SP_PLAYLIST_OFFLINE_STATUS_WAITING = 3

SP_TRACK_AVAILABILITY_UNAVAILABLE = 0
SP_TRACK_AVAILABILITY_AVAILABLE = 1
SP_TRACK_AVAILABILITY_NOT_STREAMABLE = 2
SP_TRACK_AVAILABILITY_BANNED_BY_ARTIST = 3

SP_TRACK_OFFLINE_NO = 0
SP_TRACK_OFFLINE_WAITING = 1
SP_TRACK_OFFLINE_DOWNLOADING = 2
SP_TRACK_OFFLINE_DONE = 3
SP_TRACK_OFFLINE_ERROR = 4
SP_TRACK_OFFLINE_DONE_EXPIRED = 5
SP_TRACK_OFFLINE_LIMIT_EXCEEDED = 6
SP_TRACK_OFFLINE_DONE_RESYNC = 7

class sp_audio_buffer_stats(_ctypes.Structure):
    _fields_ = [
        ('samples', _ctypes.c_int),
        ('stutter', _ctypes.c_int),
    ]

class sp_subscribers(_ctypes.Structure):
    pass # XXX Add field spec?

SP_CONNECTION_TYPE_UNKNOWN = 0
SP_CONNECTION_TYPE_NONE = 1
SP_CONNECTION_TYPE_MOBILE = 2
SP_CONNECTION_TYPE_MOBILE_ROAMING = 3
SP_CONNECTION_TYPE_WIFI = 4
SP_CONNECTION_TYPE_WIRED = 5

SP_CONNECTION_RULE_NETWORK = 0x1
SP_CONNECTION_RULE_NETWORK_IF_ROAMING = 0x2
SP_CONNECTION_RULE_ALLOW_SYNC_OVER_MOBILE = 0x4
SP_CONNECTION_RULE_ALLOW_SYNC_OVER_WIFI = 0x8

SP_ARTISTBROWSE_FULL = 0
SP_ARTISTBROWSE_NO_TRACKS = 1
SP_ARTISTBROWSE_NO_ALBUMS = 2

class sp_offline_sync_status(_ctypes.Structure):
    _fields_ = [
        ('queued_tracks', _ctypes.c_int),
        ('queued_bytes', _ctypes.c_ulonglong),
        ('done_tracks', _ctypes.c_int),
        ('done_bytes', _ctypes.c_ulonglong),
        ('copied_tracks', _ctypes.c_int),
        ('copied_bytes', _ctypes.c_ulonglong),
        ('willnotcopy_tracks', _ctypes.c_int),
        ('error_tracks', _ctypes.c_int),
        ('syncing', sp_bool),
    ]

SP_SESSION_LOGGED_IN_FUNC = _ctypes.CFUNCTYPE(None,
    _ctypes.POINTER(sp_session), sp_error)

SP_SESSION_LOGGED_OUT_FUNC = _ctypes.CFUNCTYPE(None,
    _ctypes.POINTER(sp_session))

SP_SESSION_METADATA_UPDATED_FUNC = _ctypes.CFUNCTYPE(None,
    _ctypes.POINTER(sp_session))

SP_SESSION_CONNECTION_ERROR_FUNC = _ctypes.CFUNCTYPE(None,
    _ctypes.POINTER(sp_session), sp_error)

SP_SESSION_MESSAGE_TO_USER_FUNC = _ctypes.CFUNCTYPE(None,
    _ctypes.POINTER(sp_session), _ctypes.c_char_p)

SP_SESSION_NOTIFY_MAIN_THREAD_FUNC = _ctypes.CFUNCTYPE(None,
    _ctypes.POINTER(sp_session))

SP_SESSION_MUSIC_DELIVERY_FUNC = _ctypes.CFUNCTYPE(_ctypes.c_int,
    _ctypes.POINTER(sp_session), _ctypes.POINTER(sp_audioformat),
    _ctypes.c_void_p, _ctypes.c_int)

SP_SESSION_PLAY_TOKEN_LOST_FUNC = _ctypes.CFUNCTYPE(None,
    _ctypes.POINTER(sp_session))

SP_SESSION_LOG_MESSAGE_FUNC = _ctypes.CFUNCTYPE(None,
    _ctypes.POINTER(sp_session), _ctypes.c_char_p)

SP_SESSION_END_OF_TRACK_FUNC = _ctypes.CFUNCTYPE(None,
    _ctypes.POINTER(sp_session))

SP_SESSION_STREAMING_ERROR_FUNC = _ctypes.CFUNCTYPE(None,
    _ctypes.POINTER(sp_session), sp_error)

SP_SESSION_USERINFO_UPDATED_FUNC = _ctypes.CFUNCTYPE(None,
    _ctypes.POINTER(sp_session))

SP_SESSION_START_PLAYBACK_FUNC = _ctypes.CFUNCTYPE(None,
    _ctypes.POINTER(sp_session))

SP_SESSION_STOP_PLAYBACK_FUNC = _ctypes.CFUNCTYPE(None,
    _ctypes.POINTER(sp_session))

SP_SESSION_GET_AUDIO_BUFFER_STATS_FUNC = _ctypes.CFUNCTYPE(None,
    _ctypes.POINTER(sp_session), _ctypes.POINTER(sp_audio_buffer_stats))

SP_SESSION_OFFLINE_STATUS_UPDATED_FUNC = _ctypes.CFUNCTYPE(None,
    _ctypes.POINTER(sp_session))

SP_SESSION_OFFLINE_ERROR_FUNC = _ctypes.CFUNCTYPE(None,
    _ctypes.POINTER(sp_session), sp_error)

class sp_session_callbacks(_ctypes.Structure):
    _fields_ = [
        ('logged_in', SP_SESSION_LOGGED_IN_FUNC),
        ('logged_out', SP_SESSION_LOGGED_OUT_FUNC),
        ('metadata_updated', SP_SESSION_METADATA_UPDATED_FUNC),
        ('connection_error', SP_SESSION_CONNECTION_ERROR_FUNC),
        ('message_to_user', SP_SESSION_MESSAGE_TO_USER_FUNC),
        ('notify_main_thread', SP_SESSION_NOTIFY_MAIN_THREAD_FUNC),
        ('music_delivery', SP_SESSION_MUSIC_DELIVERY_FUNC),
        ('play_token_lost', SP_SESSION_PLAY_TOKEN_LOST_FUNC),
        ('log_message', SP_SESSION_LOG_MESSAGE_FUNC),
        ('end_of_track', SP_SESSION_END_OF_TRACK_FUNC),
        ('streaming_error', SP_SESSION_STREAMING_ERROR_FUNC),
        ('userinfo_updated', SP_SESSION_USERINFO_UPDATED_FUNC),
        ('start_playback', SP_SESSION_START_PLAYBACK_FUNC),
        ('stop_playback', SP_SESSION_STOP_PLAYBACK_FUNC),
        ('get_audio_buffer_stats', SP_SESSION_GET_AUDIO_BUFFER_STATS_FUNC),
        ('offline_status_updated', SP_SESSION_OFFLINE_STATUS_UPDATED_FUNC),
        ('offline_error', SP_SESSION_OFFLINE_ERROR_FUNC),
    ]

class sp_session_config(_ctypes.Structure):
    _fields_ = [
        ('api_version', _ctypes.c_int),
        ('cache_location', _ctypes.c_char_p),
        ('settings_location', _ctypes.c_char_p),
        ('application_key', _ctypes.c_void_p),
        ('application_key_size', _ctypes.c_size_t),
        ('user_agent', _ctypes.c_char_p),
        ('callbacks', _ctypes.POINTER(sp_session_callbacks)),
        ('compress_playlists', sp_bool),
        ('dont_save_metadata_for_playlists', sp_bool),
        ('initially_unload_playlists', sp_bool),
        ('device_id', _ctypes.c_char_p),
        ('tracefile', _ctypes.c_char_p),
    ]
