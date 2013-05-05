from __future__ import unicode_literals

import logging

from spotify import Error, ffi, global_weakrefs, lib
from spotify.utils import to_unicode


__all__ = [
    'SessionCallbacks',
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


class Session(object):
    def __init__(self, sp_session):
        self.sp_session = sp_session

    def __eq__(self, other):
        return self.sp_session == other.sp_session

    def __ne__(self, other):
        return not self.__eq__(other)
