from __future__ import unicode_literals

import logging

from spotify import Error, ffi, global_weakrefs, lib
from spotify.utils import to_bytes, to_unicode


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
    notify_main_thread = None
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
        self._notify_main_thread = ffi.callback(
            'void(sp_session *)', self._notify_main_thread)
        self._log_message = ffi.callback(
            'void(sp_session *, const char *)', self._log_message)
        self._offline_status_updated = ffi.callback(
            'void(sp_session *)', self._offline_status_updated)
        self._credentials_blob_updated = ffi.callback(
            'void(sp_session *, const char *)', self._credentials_blob_updated)

    def _logged_in(self, sp_session, sp_error):
        if sp_error == Error.OK:
            logger.info('Logged in')
        else:
            logger.error('Login error: %s', Error(sp_error))
        if self.logged_in is not None:
            self.logged_in(Session(sp_session), Error(sp_error))

    def _logged_out(self, sp_session):
        logger.info('Logged out')
        if self.logged_out is not None:
            self.logged_out(Session(sp_session))

    def _metadata_updated(self, sp_session):
        logger.debug('Metadata updated')
        if self.metadata_updated is not None:
            self.metadata_updated(Session(sp_session))

    def _connection_error(self, sp_session, sp_error):
        error = Error(sp_error)
        logger.error('Connection error: %s', error)
        if self.connection_error is not None:
            self.connection_error(Session(sp_session), error)

    def _notify_main_thread(self, sp_session):
        logger.debug('Notify main thread')
        if self.notify_main_thread is not None:
            self.notify_main_thread(Session(sp_session))

    def _log_message(self, sp_session, data):
        data = to_unicode(data).strip()
        logger.debug('Log message from Spotify: %s', data)
        if self.log_message is not None:
            self.log_message(Session(sp_session), data)

    def _offline_status_updated(self, sp_session):
        logger.debug('Offline status updated')
        if self.offline_status_updated is not None:
            self.offline_status_updated(Session(sp_session))

    def _credentials_blob_updated(self, sp_session, data):
        data = ffi.string(data)
        logger.debug('Credentials blob updated: %r', data)
        if self.credentials_blob_updated is not None:
            self.credentials_blob_updated(Session(sp_session), data)

    def make_sp_session_callbacks(self):
        # TODO Add remaining callbacks

        return ffi.new('sp_session_callbacks *', {
            'logged_in': self._logged_in,
            'logged_out': self._logged_out,
            'metadata_updated': self._metadata_updated,
            'connection_error': self._connection_error,
            'notify_main_thread': self._notify_main_thread,
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

        global_weakrefs[sp_session_config] = [
            cache_location,
            settings_location,
            application_key,
            user_agent,
            callbacks,
        ]

        return sp_session_config


class Session(object):
    def __init__(self, sp_session=None, config=None):
        if sp_session is not None:
            self.sp_session = sp_session
            return

        if config is None:
            config = SessionConfig()

        sp_session_config = config.make_sp_session_config()
        sp_session_ptr = ffi.new('sp_session **')

        err = lib.sp_session_create(sp_session_config, sp_session_ptr)
        if err != Error.OK:
            raise Error(err)

        self.sp_session = ffi.gc(sp_session_ptr[0], lib.sp_session_release)

        global_weakrefs[self.sp_session] = [sp_session_config]

    def __eq__(self, other):
        return self.sp_session == other.sp_session

    def __ne__(self, other):
        return not self.__eq__(other)

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

    def process_events(self):
        next_timeout = ffi.new('int *')

        err = lib.sp_session_process_events(self.sp_session, next_timeout)
        if err != Error.OK:
            raise Error(err)

        return next_timeout[0]
