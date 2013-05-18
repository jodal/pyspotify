from __future__ import unicode_literals

import logging

import spotify
from spotify import Error, ffi, lib, User
from spotify.utils import get_with_growing_buffer, to_bytes, to_unicode


__all__ = [
    'SessionCallbacks',
    'SessionConfig',
    'Session',
]

logger = logging.getLogger(__name__)


class SessionCallbacks(object):
    logged_in = None
    logged_out = None
    metadata_updated = None
    connection_error = None
    message_to_user = None
    notify_main_thread = None
    music_delivery = None
    log_message = None
    offline_status_updated = None
    credentials_blob_updated = None

    def __init__(self):
        # If we use @ffi.callback as a decorator on the methods they'll expect
        # to get passed self from the C library, so we have to defer the
        # wrapping in ffi.callback() from class loading time to class
        # instantation time so that the methods can be bound to self before
        # they are wrapped in ffi.callback().
        self._logged_in = ffi.callback(
            'void(sp_session *, sp_error)', self._logged_in)
        self._logged_out = ffi.callback(
            'void(sp_session *)', self._logged_out)
        self._metadata_updated = ffi.callback(
            'void(sp_session *)', self._metadata_updated)
        self._connection_error = ffi.callback(
            'void(sp_session *, sp_error)', self._connection_error)
        self._message_to_user = ffi.callback(
            'void(sp_session *, const char *)', self._message_to_user)
        self._notify_main_thread = ffi.callback(
            'void(sp_session *)', self._notify_main_thread)
        self._music_delivery = ffi.callback(
            'int(sp_session *, const sp_audioformat *, const void *, int)',
            self._music_delivery)
        self._log_message = ffi.callback(
            'void(sp_session *, const char *)', self._log_message)
        self._offline_status_updated = ffi.callback(
            'void(sp_session *)', self._offline_status_updated)
        self._credentials_blob_updated = ffi.callback(
            'void(sp_session *, const char *)', self._credentials_blob_updated)

    def _logged_in(self, sp_session, sp_error):
        if not spotify.session_instance:
            return
        if sp_error == Error.OK:
            logger.info('Logged in')
        else:
            logger.error('Login error: %s', Error(sp_error))
        if self.logged_in is not None:
            self.logged_in(spotify.session_instance, Error(sp_error))

    def _logged_out(self, sp_session):
        if not spotify.session_instance:
            return
        logger.info('Logged out')
        if self.logged_out is not None:
            self.logged_out(spotify.session_instance)

    def _metadata_updated(self, sp_session):
        if not spotify.session_instance:
            return
        logger.debug('Metadata updated')
        if self.metadata_updated is not None:
            self.metadata_updated(spotify.session_instance)

    def _connection_error(self, sp_session, sp_error):
        if not spotify.session_instance:
            return
        error = Error(sp_error)
        logger.error('Connection error: %s', error)
        if self.connection_error is not None:
            self.connection_error(spotify.session_instance, error)

    def _message_to_user(self, sp_session, data):
        if not spotify.session_instance:
            return
        data = to_unicode(data).strip()
        logger.debug('Message to user: %s', data)
        if self.message_to_user is not None:
            self.message_to_user(spotify.session_instance, data)

    def _notify_main_thread(self, sp_session):
        if not spotify.session_instance:
            return
        logger.debug('Notify main thread')
        if self.notify_main_thread is not None:
            self.notify_main_thread(spotify.session_instance)

    def _music_delivery(self, sp_session, sp_audioformat, frames, num_frames):
        if not spotify.session_instance:
            return 0
        logger.debug('Music delivery')
        if self.music_delivery is not None:
            audio_format = spotify.AudioFormat(sp_audioformat)
            buffer_ = spotify.ffi.buffer(
                frames, audio_format.frame_size() * num_frames)
            # TODO Decide if we should make a copy of the buffer out of
            # libspotify's memory and into Python land, by:
            #    our_bytes = buffer_[:]
            return self.music_delivery(
                spotify.session_instance, audio_format, buffer_, num_frames)
        else:
            return 0

    def _log_message(self, sp_session, data):
        if not spotify.session_instance:
            return
        data = to_unicode(data).strip()
        logger.debug('Log message from Spotify: %s', data)
        if self.log_message is not None:
            self.log_message(spotify.session_instance, data)

    def _offline_status_updated(self, sp_session):
        if not spotify.session_instance:
            return
        logger.debug('Offline status updated')
        if self.offline_status_updated is not None:
            self.offline_status_updated(spotify.session_instance)

    def _credentials_blob_updated(self, sp_session, data):
        if not spotify.session_instance:
            return
        data = ffi.string(data)
        logger.debug('Credentials blob updated: %r', data)
        if self.credentials_blob_updated is not None:
            self.credentials_blob_updated(spotify.session_instance, data)

    def make_sp_session_callbacks(self):
        # TODO Add remaining callbacks

        return ffi.new('sp_session_callbacks *', {
            'logged_in': self._logged_in,
            'logged_out': self._logged_out,
            'metadata_updated': self._metadata_updated,
            'connection_error': self._connection_error,
            'message_to_user': self._message_to_user,
            'notify_main_thread': self._notify_main_thread,
            'music_delivery': self._music_delivery,
            'log_message': self._log_message,
            'offline_status_updated': self._offline_status_updated,
            'credentials_blob_updated': self._credentials_blob_updated,
        })


class SessionConfig(object):
    api_version = lib.SPOTIFY_API_VERSION
    cache_location = b'tmp'
    settings_location = b'tmp'
    application_key = None
    application_key_filename = b'spotify_appkey.key'
    user_agent = b'pyspotify'
    callbacks = None

    def get_application_key(self):
        if self.application_key is None:
            return open(self.application_key_filename, 'rb').read()
        else:
            return self.application_key

    def get_callbacks(self):
        if self.callbacks is None:
            return SessionCallbacks()
        else:
            return self.callbacks

    def make_sp_session_config(self):
        cache_location = ffi.new('char[]', self.cache_location)
        settings_location = ffi.new('char[]', self.settings_location)
        application_key_bytes = self.get_application_key()
        application_key = ffi.new('char[]', application_key_bytes)
        user_agent = ffi.new('char[]', self.user_agent)
        callbacks = self.get_callbacks()

        # TODO Add remaining config values
        sp_session_config = ffi.new('sp_session_config *', {
            'api_version': self.api_version,
            'cache_location': cache_location,
            'settings_location': settings_location,
            'application_key': ffi.cast('void *', application_key),
            'application_key_size': len(application_key_bytes),
            'user_agent': user_agent,
            'callbacks': callbacks.make_sp_session_callbacks(),
        })

        spotify.weak_key_dict[sp_session_config] = [
            cache_location,
            settings_location,
            application_key,
            user_agent,
            callbacks,
        ]

        return sp_session_config


class Session(object):
    def __init__(self, sp_session=None, config=None):
        if spotify.session_instance is not None:
            raise RuntimeError('Session has already been initialized')

        if config is None:
            config = SessionConfig()

        sp_session_config = config.make_sp_session_config()
        sp_session_ptr = ffi.new('sp_session **')

        err = lib.sp_session_create(sp_session_config, sp_session_ptr)
        if err != Error.OK:
            raise Error(err)

        self.sp_session = ffi.gc(sp_session_ptr[0], lib.sp_session_release)

        spotify.weak_key_dict[self.sp_session] = [sp_session_config]

        spotify.session_instance = self

    def login(self, username, password=None, remember_me=False, blob=None):
        username = ffi.new('char[]', to_bytes(username))

        if password is not None:
            password = ffi.new('char[]', to_bytes(password)) or ffi.NULL
            blob = ffi.NULL
        elif blob is not None:
            password = ffi.NULL
            blob = ffi.new('char[]', to_bytes(blob))
        else:
            raise AttributeError('password or blob is required to login')

        err = lib.sp_session_login(
            self.sp_session, username, password, bool(remember_me), blob)
        if err != Error.OK:
            raise Error(err)

    def relogin(self):
        err = lib.sp_session_relogin(self.sp_session)
        if err != Error.OK:
            raise Error(err)

    @property
    def remembered_user(self):
        return get_with_growing_buffer(
            lib.sp_session_remembered_user, self.sp_session)

    @property
    def user_name(self):
        return to_unicode(lib.sp_session_user_name(self.sp_session))

    def forget_me(self):
        err = lib.sp_session_forget_me(self.sp_session)
        if err != Error.OK:
            raise Error(err)

    @property
    def user(self):
        sp_user = lib.sp_session_user(self.sp_session)
        if sp_user == ffi.NULL:
            return None
        return User(sp_user)

    def logout(self):
        err = lib.sp_session_logout(self.sp_session)
        if err != Error.OK:
            raise Error(err)

    def process_events(self):
        next_timeout = ffi.new('int *')

        err = lib.sp_session_process_events(self.sp_session, next_timeout)
        if err != Error.OK:
            raise Error(err)

        return next_timeout[0] / 1000.0

    # TODO Add all sp_session_* methods
