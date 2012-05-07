import ctypes
import threading
import unittest

from spotify import capi

class CAPISessionEnumAndStructTest(unittest.TestCase):
    def test_sp_connectionstate_enum_has_correct_enumeration(self):
        self.assertEqual(capi.SP_CONNECTION_STATE_LOGGED_OUT, 0)
        self.assertEqual(capi.SP_CONNECTION_STATE_LOGGED_IN, 1)
        self.assertEqual(capi.SP_CONNECTION_STATE_DISCONNECTED, 2)
        self.assertEqual(capi.SP_CONNECTION_STATE_UNDEFINED, 3)
        self.assertEqual(capi.SP_CONNECTION_STATE_OFFLINE, 4)

    def test_sp_sampletype_is_ctypes_c_uint(self):
        self.assertEqual(capi.sp_sampletype, ctypes.c_int)

    def test_sp_sampletype_enum_has_correct_enumeration(self):
        self.assertEqual(capi.SP_SAMPLETYPE_INT16_NATIVE_ENDIAN, 0)

    def test_sp_audioformat_struct_can_be_created_and_read_from(self):
        audioformat = capi.sp_audioformat(
            sample_type=capi.SP_SAMPLETYPE_INT16_NATIVE_ENDIAN,
            sample_rate=44100,
            channels=2)
        self.assertEqual(audioformat.sample_type,
            capi.SP_SAMPLETYPE_INT16_NATIVE_ENDIAN)
        self.assertEqual(audioformat.sample_rate, 44100)
        self.assertEqual(audioformat.channels, 2)

    def test_sp_bitrate_enum_has_correct_enumeration(self):
        self.assertEqual(capi.SP_BITRATE_160k, 0)
        self.assertEqual(capi.SP_BITRATE_320k, 1)
        self.assertEqual(capi.SP_BITRATE_96k, 2)

    def test_sp_playlist_type_enum_has_correct_enumeration(self):
        self.assertEqual(capi.SP_PLAYLIST_TYPE_PLAYLIST, 0)
        self.assertEqual(capi.SP_PLAYLIST_TYPE_START_FOLDER, 1)
        self.assertEqual(capi.SP_PLAYLIST_TYPE_END_FOLDER, 2)
        self.assertEqual(capi.SP_PLAYLIST_TYPE_PLACEHOLDER, 3)

    def test_sp_playlist_offline_status_enum_has_correct_enumeration(self):
        self.assertEqual(capi.SP_PLAYLIST_OFFLINE_STATUS_NO, 0)
        self.assertEqual(capi.SP_PLAYLIST_OFFLINE_STATUS_YES, 1)
        self.assertEqual(capi.SP_PLAYLIST_OFFLINE_STATUS_DOWNLOADING, 2)
        self.assertEqual(capi.SP_PLAYLIST_OFFLINE_STATUS_WAITING, 3)

    def test_sp_availability_enum_has_correct_enumeration(self):
        self.assertEqual(capi.SP_TRACK_AVAILABILITY_UNAVAILABLE, 0)
        self.assertEqual(capi.SP_TRACK_AVAILABILITY_AVAILABLE, 1)
        self.assertEqual(capi.SP_TRACK_AVAILABILITY_NOT_STREAMABLE, 2)
        self.assertEqual(capi.SP_TRACK_AVAILABILITY_BANNED_BY_ARTIST, 3)

    def test_sp_track_offline_status_enum_has_correct_enumeration(self):
        self.assertEqual(capi.SP_TRACK_OFFLINE_NO, 0)
        self.assertEqual(capi.SP_TRACK_OFFLINE_WAITING, 1)
        self.assertEqual(capi.SP_TRACK_OFFLINE_DOWNLOADING, 2)
        self.assertEqual(capi.SP_TRACK_OFFLINE_DONE, 3)
        self.assertEqual(capi.SP_TRACK_OFFLINE_ERROR, 4)
        self.assertEqual(capi.SP_TRACK_OFFLINE_DONE_EXPIRED, 5)
        self.assertEqual(capi.SP_TRACK_OFFLINE_LIMIT_EXCEEDED, 6)
        self.assertEqual(capi.SP_TRACK_OFFLINE_DONE_RESYNC, 7)

    def test_sp_audio_buffer_stats_struct_can_be_created_and_read_from(self):
        stats = capi.sp_audio_buffer_stats(samples=100, stutter=0)
        self.assertEqual(stats.samples, 100)
        self.assertEqual(stats.stutter, 0)

    def test_sp_subscribers_struct_can_be_created_and_read_from(self):
        users = ['foo', 'bar', 'baz']
        subscribers = capi.sp_subscribers(count=len(users),
            subscribers=(ctypes.c_char_p * len(users))(*users))
        self.assertEqual(subscribers.count, 3)
        self.assertItemsEqual(subscribers.subscribers, ['foo', 'bar', 'baz'])

    def test_sp_connection_type_enum_has_correct_enumeration(self):
        self.assertEqual(capi.SP_CONNECTION_TYPE_UNKNOWN, 0)
        self.assertEqual(capi.SP_CONNECTION_TYPE_NONE, 1)
        self.assertEqual(capi.SP_CONNECTION_TYPE_MOBILE, 2)
        self.assertEqual(capi.SP_CONNECTION_TYPE_MOBILE_ROAMING, 3)
        self.assertEqual(capi.SP_CONNECTION_TYPE_WIFI, 4)
        self.assertEqual(capi.SP_CONNECTION_TYPE_WIRED, 5)

    def test_sp_connection_rules_enum_has_correct_enumeration(self):
        self.assertEqual(capi.SP_CONNECTION_RULE_NETWORK, 0x1)
        self.assertEqual(capi.SP_CONNECTION_RULE_NETWORK_IF_ROAMING, 0x2)
        self.assertEqual(capi.SP_CONNECTION_RULE_ALLOW_SYNC_OVER_MOBILE, 0x4)
        self.assertEqual(capi.SP_CONNECTION_RULE_ALLOW_SYNC_OVER_WIFI, 0x8)

    def test_sp_artistbrowse_type_enum_has_correct_enumeration(self):
        self.assertEqual(capi.SP_ARTISTBROWSE_FULL, 0)
        self.assertEqual(capi.SP_ARTISTBROWSE_NO_TRACKS, 1)
        self.assertEqual(capi.SP_ARTISTBROWSE_NO_ALBUMS, 2)

    def test_sp_offline_sync_status_can_be_created_and_read_from(self):
        status = capi.sp_offline_sync_status(
            queued_tracks=7,
            queued_bytes=64000,
            done_tracks=101,
            done_bytes=564000,
            copied_tracks=13,
            copied_bytes=143000,
            willnotcopy_tracks=1,
            error_tracks=2,
            syncing=True,
        )
        self.assertEqual(status.queued_tracks, 7)
        self.assertEqual(status.queued_bytes, 64000)
        self.assertEqual(status.done_tracks, 101)
        self.assertEqual(status.done_bytes, 564000)
        self.assertEqual(status.copied_tracks, 13)
        self.assertEqual(status.copied_bytes, 143000)
        self.assertEqual(status.willnotcopy_tracks, 1)
        self.assertEqual(status.error_tracks, 2)
        self.assertEqual(status.syncing, True)

    def test_sp_offline_sync_status_raises_exc_on_wrong_arg_types(self):
        self.assertRaises(TypeError, capi.sp_offline_sync_status,
            queued_tracks='not an integer')
        self.assertRaises(TypeError, capi.sp_offline_sync_status,
            queued_bytes='not an integer')
        self.assertRaises(TypeError, capi.sp_offline_sync_status,
            done_tracks='not an integer')
        self.assertRaises(TypeError, capi.sp_offline_sync_status,
            done_bytes='not an integer')
        self.assertRaises(TypeError, capi.sp_offline_sync_status,
            copied_tracks='not an integer')
        self.assertRaises(TypeError, capi.sp_offline_sync_status,
            willnotcopy_tracks='not an integer')
        self.assertRaises(TypeError, capi.sp_offline_sync_status,
            error_tracks='not an integer')
        self.assertRaises(TypeError, capi.sp_offline_sync_status,
            syncing='not an integer')


class CAPISessionCallbackTest(unittest.TestCase):
    def test_SP_SESSION_LOGGED_IN_FUNC_can_wrap_callback(self):
        callback = capi.SP_SESSION_LOGGED_IN_FUNC(lambda session, error: None)
        self.assertEqual(callback(None, 0), None)

    def test_SP_SESSION_LOGGED_OUT_FUNC_can_wrap_callback(self):
        callback = capi.SP_SESSION_LOGGED_OUT_FUNC(lambda session: None)
        self.assertEqual(callback(None), None)

    def test_SP_SESSION_METADATA_UPDATED_FUNC_can_wrap_callback(self):
        callback = capi.SP_SESSION_METADATA_UPDATED_FUNC(lambda session: None)
        self.assertEqual(callback(None), None)

    def test_SP_SESSION_CONNECTION_ERROR_FUNC_can_wrap_callback(self):
        callback = capi.SP_SESSION_CONNECTION_ERROR_FUNC(
            lambda session, error: None)
        self.assertEqual(callback(None, 0), None)

    def test_SP_SESSION_MESSAGE_TO_USER_FUNC_can_wrap_callback(self):
        callback = capi.SP_SESSION_MESSAGE_TO_USER_FUNC(
            lambda session, message: None)
        self.assertEqual(callback(None, 'msg'), None)

    def test_SP_SESSION_NOTIFY_MAIN_THREAD_FUNC_can_wrap_callback(self):
        callback = capi.SP_SESSION_NOTIFY_MAIN_THREAD_FUNC(lambda session: None)
        self.assertEqual(callback(None), None)

    def test_SP_SESSION_MUSIC_DELIVERY_FUNC_can_wrap_callback(self):
        callback = capi.SP_SESSION_MUSIC_DELIVERY_FUNC(lambda session,
            audioformat, frames, num_frames: 7)
        self.assertEqual(callback(None, None, None, 10), 7)

    def test_SP_SESSION_PLAY_TOKEN_LOST_FUNC_can_wrap_callback(self):
        callback = capi.SP_SESSION_PLAY_TOKEN_LOST_FUNC(lambda session: None)
        self.assertEqual(callback(None), None)

    def test_SP_SESSION_LOG_MESSAGE_FUNC_can_wrap_callback(self):
        callback = capi.SP_SESSION_LOG_MESSAGE_FUNC(lambda session, data: None)
        self.assertEqual(callback(None, 'msg'), None)

    def test_SP_SESSION_END_OF_TRACK_FUNC_can_wrap_callback(self):
        callback = capi.SP_SESSION_END_OF_TRACK_FUNC(lambda session: None)
        self.assertEqual(callback(None), None)

    def test_SP_SESSION_STREAMING_ERROR_FUNC_can_wrap_callback(self):
        callback = capi.SP_SESSION_STREAMING_ERROR_FUNC(
            lambda session, error: None)
        self.assertEqual(callback(None, 0), None)

    def test_SP_SESSION_USERINFO_UPDATED_FUNC_can_wrap_callback(self):
        callback = capi.SP_SESSION_USERINFO_UPDATED_FUNC(lambda session: None)
        self.assertEqual(callback(None), None)

    def test_SP_SESSION_START_PLAYBACK_FUNC_can_wrap_callback(self):
        callback = capi.SP_SESSION_START_PLAYBACK_FUNC(lambda session: None)
        self.assertEqual(callback(None), None)

    def test_SP_SESSION_STOP_PLAYBACK_FUNC_can_wrap_callback(self):
        callback = capi.SP_SESSION_STOP_PLAYBACK_FUNC(lambda session: None)
        self.assertEqual(callback(None), None)

    def test_SP_SESSION_GET_AUDIO_BUFFER_STATS_FUNC_can_wrap_callback(self):
        callback = capi.SP_SESSION_GET_AUDIO_BUFFER_STATS_FUNC(
            lambda session, stats: None)
        self.assertEqual(callback(None, None), None)

    def test_SP_SESSION_OFFLINE_STATUS_UPDATED_FUNC_can_wrap_callback(self):
        callback = capi.SP_SESSION_OFFLINE_STATUS_UPDATED_FUNC(lambda session: None)
        self.assertEqual(callback(None), None)

    def test_SP_SESSION_OFFLINE_ERROR_FUNC_can_wrap_callback(self):
        callback = capi.SP_SESSION_OFFLINE_ERROR_FUNC(lambda session, error: None)
        self.assertEqual(callback(None, 0), None)

    def test_sp_session_callbacks_can_be_created_and_read_from(self):
        callbacks = capi.sp_session_callbacks(
            logged_in=capi.SP_SESSION_LOGGED_IN_FUNC(lambda *args: None),
            logged_out=capi.SP_SESSION_LOGGED_OUT_FUNC(lambda *args: None),
            metadata_updated=capi.SP_SESSION_METADATA_UPDATED_FUNC(
                lambda *args: None),
            connection_error=capi.SP_SESSION_CONNECTION_ERROR_FUNC(
                lambda *args: None),
            message_to_user=capi.SP_SESSION_MESSAGE_TO_USER_FUNC(
                lambda *args: None),
            notify_main_thread=capi.SP_SESSION_NOTIFY_MAIN_THREAD_FUNC(
                lambda *args: None),
            music_delivery=capi.SP_SESSION_MUSIC_DELIVERY_FUNC(
                lambda *args: 7),
            play_token_lost=capi.SP_SESSION_PLAY_TOKEN_LOST_FUNC(
                lambda *args: None),
            log_message=capi.SP_SESSION_LOG_MESSAGE_FUNC(
                lambda *args: None),
            end_of_track=capi.SP_SESSION_END_OF_TRACK_FUNC(
                lambda *args: None),
            streaming_error=capi.SP_SESSION_STREAMING_ERROR_FUNC(
                lambda *args: None),
            userinfo_updated=capi.SP_SESSION_USERINFO_UPDATED_FUNC(
                lambda *args: None),
            start_playback=capi.SP_SESSION_START_PLAYBACK_FUNC(
                lambda *args: None),
            stop_playback=capi.SP_SESSION_STOP_PLAYBACK_FUNC(
                lambda *args: None),
            get_audio_buffer_stats=capi.SP_SESSION_GET_AUDIO_BUFFER_STATS_FUNC(
                lambda *args: None),
            offline_status_updated=capi.SP_SESSION_OFFLINE_STATUS_UPDATED_FUNC(
                lambda *args: None),
            offline_error=capi.SP_SESSION_OFFLINE_ERROR_FUNC(
                lambda *args: None),
        )
        self.assertEqual(callbacks.logged_in(None, 0), None)
        self.assertEqual(callbacks.logged_out(None), None)
        self.assertEqual(callbacks.metadata_updated(None), None)
        self.assertEqual(callbacks.connection_error(None, 0), None)
        self.assertEqual(callbacks.message_to_user(None, 'msg'), None)
        self.assertEqual(callbacks.notify_main_thread(None), None)
        self.assertEqual(callbacks.music_delivery(None, None, None, 0), 7)
        self.assertEqual(callbacks.play_token_lost(None), None)
        self.assertEqual(callbacks.log_message(None, 'msg'), None)
        self.assertEqual(callbacks.end_of_track(None), None)
        self.assertEqual(callbacks.streaming_error(None, 0), None)
        self.assertEqual(callbacks.userinfo_updated(None), None)
        self.assertEqual(callbacks.start_playback(None), None)
        self.assertEqual(callbacks.stop_playback(None), None)
        self.assertEqual(callbacks.get_audio_buffer_stats(None, None), None)
        self.assertEqual(callbacks.offline_status_updated(None), None)
        self.assertEqual(callbacks.offline_error(None, 0), None)

    def test_sp_session_callbacks_raises_exc_on_wrong_arg_types(self):
        self.assertRaises(TypeError, capi.sp_session_callbacks,
            logged_in='not a function')
        self.assertRaises(TypeError, capi.sp_session_callbacks,
            logged_out='not a function')
        self.assertRaises(TypeError, capi.sp_session_callbacks,
            metadata_updated='not a function')
        self.assertRaises(TypeError, capi.sp_session_callbacks,
            connection_error='not a function')
        self.assertRaises(TypeError, capi.sp_session_callbacks,
            message_to_user='not a function')
        self.assertRaises(TypeError, capi.sp_session_callbacks,
            notify_main_thread='not a function')
        self.assertRaises(TypeError, capi.sp_session_callbacks,
            music_delivery='not a function')
        self.assertRaises(TypeError, capi.sp_session_callbacks,
            play_token_lost='not a function')
        self.assertRaises(TypeError, capi.sp_session_callbacks,
            log_message='not a function')
        self.assertRaises(TypeError, capi.sp_session_callbacks,
            end_of_track='not a function')
        self.assertRaises(TypeError, capi.sp_session_callbacks,
            streaming_error='not a function')
        self.assertRaises(TypeError, capi.sp_session_callbacks,
            userinfo_updated='not a function')
        self.assertRaises(TypeError, capi.sp_session_callbacks,
            start_playback='not a function')
        self.assertRaises(TypeError, capi.sp_session_callbacks,
            stop_playback='not a function')
        self.assertRaises(TypeError, capi.sp_session_callbacks,
            get_audio_buffer_stats='not a function')
        self.assertRaises(TypeError, capi.sp_session_callbacks,
            offline_status_updated='not a function')
        self.assertRaises(TypeError, capi.sp_session_callbacks,
            offline_error='not a function')


class CAPISessionConfigTest(unittest.TestCase):
    def test_sp_session_config_can_be_created_and_read_from(self):
        callbacks = capi.sp_session_callbacks()
        config = capi.sp_session_config(
            api_version=10,
            cache_location='foo',
            settings_location='bar',
            application_key=None,
            application_key_size=0,
            user_agent='baz',
            callbacks=ctypes.pointer(callbacks),
            compress_playlists=True,
            dont_save_metadata_for_playlists=True,
            initially_unload_playlists=True,
            device_id='qux',
            tracefile='quux',
        )
        self.assertEqual(config.api_version, 10)
        self.assertEqual(config.cache_location, 'foo')
        self.assertEqual(config.settings_location, 'bar')
        self.assertEqual(config.application_key, None)
        self.assertEqual(config.application_key_size, 0)
        self.assertEqual(config.user_agent, 'baz')
        self.assertEqual(type(config.callbacks[0]), type(callbacks))
        self.assertEqual(config.compress_playlists, True)
        self.assertEqual(config.dont_save_metadata_for_playlists, True)
        self.assertEqual(config.initially_unload_playlists, True)
        self.assertEqual(config.device_id, 'qux')
        self.assertEqual(config.tracefile, 'quux')

    def test_sp_session_config_raises_exc_on_wrong_arg_types(self):
        self.assertRaises(TypeError, capi.sp_session_config,
            api_version='not an integer')
        self.assertRaises(TypeError, capi.sp_session_config,
            cache_location=1.0)
        self.assertRaises(TypeError, capi.sp_session_config,
            settings_location=1.0)
        self.assertRaises(TypeError, capi.sp_session_config,
            application_key=1.0)
        self.assertRaises(TypeError, capi.sp_session_config,
            application_key_size='not an integer')
        self.assertRaises(TypeError, capi.sp_session_config,
            user_agent=1.0)
        self.assertRaises(TypeError, capi.sp_session_config,
            callbacks='not a sp_session_callbacks pointer')
        self.assertRaises(TypeError, capi.sp_session_config,
            compress_playlists='not a bool')
        self.assertRaises(TypeError, capi.sp_session_config,
            dont_save_metadata_for_playlists='not a bool')
        self.assertRaises(TypeError, capi.sp_session_config,
            initially_unload_playlists='not a bool')
        self.assertRaises(TypeError, capi.sp_session_config,
            device_id=1.0)
        self.assertRaises(TypeError, capi.sp_session_config,
            tracefile=1.0)


class CAPISessionCreationTest(unittest.TestCase):
    def test_sp_session_create(self):
        application_key = b'appkey_good'
        config = capi.sp_session_config(
            application_key=application_key,
            application_key_size=len(application_key))
        callbacks = capi.sp_session_callbacks()
        session = capi.sp_session_create(config, callbacks)
        self.assertEqual(type(session), ctypes.POINTER(capi.sp_session))

    def test_sp_session_create_fails_with_invalid_app_key(self):
        application_key = b'appkey_bad'
        config = capi.sp_session_config(
            application_key=application_key,
            application_key_size=len(application_key))
        callbacks = capi.sp_session_callbacks()
        self.assertRaises(capi.SpError,
            capi.sp_session_create, config, callbacks)

    def test_sp_session_create_fails_with_invalid_arg_count(self):
        self.assertRaises(TypeError, capi.sp_session_create)

    def test_sp_session_create_fails_with_invalid_arg_type(self):
        self.assertRaises(TypeError, capi.sp_session_create, 1.0, None)


class CAPISessionLoginTest(unittest.TestCase):
    def test_sp_session_login(self):
        self.logged_in_called = threading.Event()
        application_key = b'appkey_good'
        config = capi.sp_session_config(
            application_key=application_key,
            application_key_size=len(application_key))
        callbacks = capi.sp_session_callbacks(
            logged_in=capi.SP_SESSION_LOGGED_IN_FUNC(
                lambda *a: self.logged_in_called.set())
        )
        session = capi.sp_session_create(config, callbacks)

        capi.sp_session_login(session,
            username='alice', password='secret', remember_me=False, blob=None)

        self.logged_in_called.wait(1)
        self.assert_(self.logged_in_called.is_set())


class CAPISessionProcessEventsTest(unittest.TestCase):
    def test_sp_session_process_events(self):
        application_key = b'appkey_good'
        config = capi.sp_session_config(
            application_key=application_key,
            application_key_size=len(application_key))
        callbacks = capi.sp_session_callbacks(
            logged_in=capi.SP_SESSION_LOGGED_IN_FUNC(
                lambda *a: self.logged_in_called.set())
        )
        session = capi.sp_session_create(config, callbacks)

        next_timeout = capi.sp_session_process_events(session)

        self.assertEquals(next_timeout, 1)
