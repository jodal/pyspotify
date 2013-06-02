from __future__ import unicode_literals

import logging

import spotify
from spotify import (
    Error, ErrorType, ffi, lib, Playlist, PlaylistContainer, User)
from spotify.utils import enum, get_with_growing_buffer, to_bytes, to_unicode


__all__ = [
    'ConnectionState',
    'SessionCallbacks',
    'SessionConfig',
    'Session',
]

logger = logging.getLogger(__name__)


@enum('SP_CONNECTION_STATE_')
class ConnectionState(object):
    pass


class SessionCallbacks(object):
    """Session callbacks.

    If needed, callback functions and :class:`None` can be assigned to
    :class:`SessionCallbacks` instance's attributes while a session exists and
    is in use.

    All callbacks will cause debug log statements to be emitted, even if the
    callback attributes are set to :class:`None`. Thus, there is no need to
    define callback functions just to log that they're called.
    """

    logged_in = None
    """Called when login has completed.

    :param session: the current session
    :type session: :class:`Session`
    :param error: the login error
    :type error: :class:`Error`
    """

    logged_out = None
    """Called when logout has completed or there is a permanent connection
    error.

    :param session: the current session
    :type session: :class:`Session`
    """

    metadata_updated = None
    """Called when some metadata has been updated.

    There is no way to know what metadata was updated, so you'll have to
    refresh all you metadata caches.

    :param session: the current session
    :type session: :class:`Session`
    """

    connection_error = None
    """Called when there is a connection error and libspotify has problems
    reconnecting to the Spotify service.

    May be called repeatedly as long as the problem persists. Will be called
    with an :attr:`Error.OK` error when the problem is resolved.

    :param session: the current session
    :type session: :class:`Session`
    :param error: the connection error
    :type error: :class:`Error`
    """

    message_to_user = None
    """Called when libspotify wants to show a message to the end user.

    :param session: the current session
    :type session: :class:`Session`
    :param data: the message
    :type data: text
    """

    notify_main_thread = None
    """Called when processing on the main thread is needed.

    When this is called, you should call :meth:`~Session.process_events` from
    your main thread. Failure to do so may cause request timeouts, or a lost
    connection.

    .. warning::

        This function is called from an internal libspotify thread. You need
        proper synchronization.

    :param session: the current session
    :type session: :class:`Session`
    """

    music_delivery = None
    """Called when there is decompressed audio data available.

    If the function returns a lower number of frames consumed than
    ``num_frames``, libspotify will retry delivery of the unconsumed frames in
    about 100ms. This can be used for rate limiting if libspotify is giving you
    audio data too fast.

    .. warning::

        This function is called from an internal libspotify thread. You need
        proper synchronization.

    :param session: the current session
    :type session: :class:`Session`
    :param audio_format: the audio format
    :type audio_format: :class:`AudioFormat`
    :param frames: the audio frames
    :type frames: bytestring
    :param num_frames: the number of frames
    :type num_frames: int
    :returns: the number of frames consumed
    """

    play_token_lost = None
    """Music has been paused because an account only allows music to be played
    from one location simultaneously.

    When this callback is called, you should pause playback.

    :param session: the current session
    :type session: :class:`Session`
    """

    log_message = None
    """Called when libspotify have something to log.

    Note that pyspotify logs this for you, so you'll probably never need to
    define this callback.

    :param session: the current session
    :type session: :class:`Session`
    :param data: the message
    :type data: text
    """

    end_of_track = None
    """Called when all audio data for the current track has been delivered.

    :param session: the current session
    :type session: :class:`Session`
    """

    streaming_error = None
    """Called when audio streaming cannot start or continue.

    :param session: the current session
    :type session: :class:`Session`
    :param error: the streaming error
    :type error: :class:`Error`
    """

    user_info_updated = None
    """Called when anything related to :class:`User` objects is updated.

    :param session: the current session
    :type session: :class:`Session`
    """

    start_playback = None
    """Called when audio playback should start.

    You need to implement :attr:`get_audio_buffer_stats` for this callback to
    be useful.

    .. warning::

        This function is called from an internal libspotify thread. You need
        proper synchronization.

    :param session: the current session
    :type session: :class:`Session`
    """

    stop_playback = None
    """Called when audio playback should stop.

    You need to implement :attr:`get_audio_buffer_stats` for this callback to
    be useful.

    .. warning::

        This function is called from an internal libspotify thread. You need
        proper synchronization.

    :param session: the current session
    :type session: :class:`Session`
    """

    get_audio_buffer_stats = None
    """Called to query the application about its audio buffer.

    .. warning::

        This function is called from an internal libspotify thread. You need
        proper synchronization.

    :param session: the current session
    :type session: :class:`Session`
    :returns: an :class:`AudioBufferStats` instance
    """

    offline_status_updated = None
    """Called when offline sync status is updated.

    :param session: the current session
    :type session: :class:`Session`
    """

    credentials_blob_updated = None
    """Called when storable credentials have been updated, typically right
    after login.

    The ``blob`` argument can be stored and later passed to
    :meth:`~Session.login` to login without storing the user's password.

    :param session: the current session
    :type session: :class:`Session`
    :param blob: the authentication blob
    :type blob: bytestring
    """

    connection_state_updated = None
    """Called when the connection state is updated.

    The connection state includes login, logout, offline mode, etc.

    :param session: the current session
    :type session: :class:`Session`
    """

    scrobble_error = None
    """Called when there is a scrobble error event.

    :param session: the current session
    :type session: :class:`Session`
    :param error: the scrobble error
    :type error: :class:`Error`
    """

    private_session_mode_changed = None
    """Called when there is a change in the private session mode.

    :param session: the current session
    :type session: :class:`Session`
    :param is_private: whether the session is private
    :type is_private: bool
    """

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
        self._play_token_lost = ffi.callback(
            'void(sp_session *)', self._play_token_lost)
        self._log_message = ffi.callback(
            'void(sp_session *, const char *)', self._log_message)
        self._end_of_track = ffi.callback(
            'void(sp_session *)', self._end_of_track)
        self._streaming_error = ffi.callback(
            'void(sp_session *, sp_error)', self._streaming_error)
        self._user_info_updated = ffi.callback(
            'void(sp_session *)', self._user_info_updated)
        self._start_playback = ffi.callback(
            'void(sp_session *)', self._start_playback)
        self._stop_playback = ffi.callback(
            'void(sp_session *)', self._stop_playback)
        self._get_audio_buffer_stats = ffi.callback(
            'void(sp_session *, sp_audio_buffer_stats *)',
            self._get_audio_buffer_stats)
        self._offline_status_updated = ffi.callback(
            'void(sp_session *)', self._offline_status_updated)
        self._credentials_blob_updated = ffi.callback(
            'void(sp_session *, const char *)', self._credentials_blob_updated)
        self._connection_state_updated = ffi.callback(
            'void(sp_session *)', self._connection_state_updated)
        self._scrobble_error = ffi.callback(
            'void(sp_session *, sp_error)', self._scrobble_error)
        self._private_session_mode_changed = ffi.callback(
            'void(sp_session *, bool)', self._private_session_mode_changed)

    def _logged_in(self, sp_session, sp_error):
        if not spotify.session_instance:
            return
        if sp_error == ErrorType.OK:
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
            frames_bytes = buffer_[:]
            return self.music_delivery(
                spotify.session_instance, audio_format,
                frames_bytes, num_frames)
        else:
            return 0

    def _play_token_lost(self, sp_session):
        if not spotify.session_instance:
            return
        logger.debug('Play token lost')
        if self.play_token_lost is not None:
            self.play_token_lost(spotify.session_instance)

    def _log_message(self, sp_session, data):
        if not spotify.session_instance:
            return
        data = to_unicode(data).strip()
        logger.debug('Log message from Spotify: %s', data)
        if self.log_message is not None:
            self.log_message(spotify.session_instance, data)

    def _end_of_track(self, sp_session):
        if not spotify.session_instance:
            return
        logger.debug('End of track')
        if self.end_of_track is not None:
            self.end_of_track(spotify.session_instance)

    def _streaming_error(self, sp_session, sp_error):
        if not spotify.session_instance:
            return
        error = Error(sp_error)
        logger.error('Streaming error: %s', error)
        if self.streaming_error is not None:
            self.streaming_error(spotify.session_instance, error)

    def _user_info_updated(self, sp_session):
        if not spotify.session_instance:
            return
        logger.debug('User info updated')
        if self.user_info_updated is not None:
            self.user_info_updated(spotify.session_instance)

    def _start_playback(self, sp_session):
        if not spotify.session_instance:
            return
        logger.debug('Start playback called')
        if self.start_playback is not None:
            self.start_playback(spotify.session_instance)

    def _stop_playback(self, sp_session):
        if not spotify.session_instance:
            return
        logger.debug('Stop playback called')
        if self.stop_playback is not None:
            self.stop_playback(spotify.session_instance)

    def _get_audio_buffer_stats(self, sp_session, sp_audio_buffer_stats):
        if not spotify.session_instance:
            return
        logger.debug('Audio buffer stats requested')
        if self.get_audio_buffer_stats is not None:
            stats = self.get_audio_buffer_stats(spotify.session_instance)
            sp_audio_buffer_stats.samples = stats.samples
            sp_audio_buffer_stats.stutter = stats.stutter

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

    def _connection_state_updated(self, sp_session):
        if not spotify.session_instance:
            return
        logger.debug('Connection state updated')
        if self.connection_state_updated is not None:
            self.connection_state_updated(spotify.session_instance)

    def _scrobble_error(self, sp_session, sp_error):
        if not spotify.session_instance:
            return
        error = Error(sp_error)
        logger.error('Scrobble error: %s', error)
        if self.scrobble_error is not None:
            self.scrobble_error(spotify.session_instance, error)

    def _private_session_mode_changed(self, sp_session, is_private):
        if not spotify.session_instance:
            return
        is_private = bool(is_private)
        status = 'private' if is_private else 'public'
        logger.error('Private session mode changed: %s', status)
        if self.private_session_mode_changed is not None:
            self.private_session_mode_changed(
                spotify.session_instance, is_private)

    def make_sp_session_callbacks(self):
        """Internal method."""

        return ffi.new('sp_session_callbacks *', {
            'logged_in': self._logged_in,
            'logged_out': self._logged_out,
            'metadata_updated': self._metadata_updated,
            'connection_error': self._connection_error,
            'message_to_user': self._message_to_user,
            'notify_main_thread': self._notify_main_thread,
            'music_delivery': self._music_delivery,
            'play_token_lost': self._play_token_lost,
            'log_message': self._log_message,
            'end_of_track': self._end_of_track,
            'streaming_error': self._streaming_error,
            'userinfo_updated': self._user_info_updated,
            'start_playback': self._start_playback,
            'stop_playback': self._stop_playback,
            'get_audio_buffer_stats': self._get_audio_buffer_stats,
            'offline_status_updated': self._offline_status_updated,
            'credentials_blob_updated': self._credentials_blob_updated,
            'connectionstate_updated': self._connection_state_updated,
            'scrobble_error': self._scrobble_error,
            'private_session_mode_changed': self._private_session_mode_changed,
        })


class SessionConfig(object):
    """The session config.

    Create an instance and assign to its attributes to configure. Then use the
    config object to create a session::

        >>> import spotify
        >>> config = spotify.SessionConfig()
        >>> config.user_agent = 'My Spotify client'
        >>> # Etc ...
        >>> session = spotify.Session(config)
    """

    api_version = lib.SPOTIFY_API_VERSION
    """The API version of the libspotify we're using.

    You should not need to change this. It is read from
    :attr:`spotify.lib.SPOTIFY_API_VERSION`.
    """

    cache_location = b'tmp'
    """A location for libspotify to cache files.

    Must be a bytestring. Cannot be shared with other Spotify apps. Can only be
    used by one session at the time. Optimally, you should use a lock file or
    similar to ensure this.
    """

    settings_location = b'tmp'
    """A location for libspotify to save settings.

    Must be a bytestring. Cannot be shared with other Spotify apps. Can only be
    used by one session at the time. Optimally, you should use a lock file or
    similar to ensure this.
    """

    application_key = None
    """Your libspotify application key.

    Must be a bytestring. Alternatively, you can set
    :attr:`application_key_filename`, and pyspotify will read the file and use
    it instead of :attr:`application_key`.
    """

    application_key_filename = b'spotify_appkey.key'
    """Path to your libspotify application key file.

    This is an alternative to :attr:`application_key`. The file must be a
    binary key file, not the C code key file that can be compiled into an
    application.
    """

    user_agent = 'pyspotify'
    """A string with the name of your client."""

    callbacks = None
    """A :class:`SessionCallbacks` instance.

    If not set, a :class:`SessionCallbacks` instance will be created for you.
    """

    compress_playlists = False
    """Compress local copy of playlists, reduces disk space usage."""

    dont_save_metadata_for_playlists = False
    """Don't save metadata for local copies of playlists.

    Reduces disk space usage at the expense of needing to request metadata from
    Spotify backend when loading list."""

    initially_unload_playlists = False
    """Avoid loading playlists into RAM on startup.

    See :meth:`Playlist.is_in_ram` for more details.
    """

    device_id = None
    """Device ID for offline synchronization and logging purposes.

    The Device ID must be unique to the particular device instance, i.e. no two
    units must supply the same Device ID. The Device ID must not change between
    sessions or power cycles. Good examples is the device's MAC address or
    unique serial number.
    """

    proxy = None
    """URL to the proxy server that should be used.

    The format is protocol://host:port where protocol is
    http/https/socks4/socks5.
    """

    proxy_username = None
    """Username to authenticate with proxy server."""

    proxy_password = None
    """Password to authenticate with proxy server."""

    ca_certs_filename = None
    """Path to a file containing the root CA certificates that the peer should
    be verified with.

    The file must be a concatenation of all certificates in PEM format.
    Provided with libspotify is a sample PEM file in the ``examples/`` dir. It
    is recommended that the application export a similar file from the local
    certificate store.

    Must be a bytestring.
    """

    tracefile = None
    """Path to API trace file.

    Must be a bytestring.
    """

    def get_application_key(self):
        """Internal method."""
        if self.application_key is None:
            return open(self.application_key_filename, 'rb').read()
        else:
            return self.application_key

    def get_callbacks(self):
        """Internal method."""
        if self.callbacks is None:
            return SessionCallbacks()
        else:
            return self.callbacks

    def make_sp_session_config(self):
        """Internal method."""

        convert = lambda value: ffi.NULL if value is None else ffi.new(
            'char[]', to_bytes(value))

        cache_location = ffi.new('char[]', to_bytes(self.cache_location))
        settings_location = ffi.new('char[]', to_bytes(self.settings_location))
        application_key_bytes = self.get_application_key()
        application_key = ffi.new('char[]', application_key_bytes)
        user_agent = ffi.new('char[]', to_bytes(self.user_agent))
        callbacks = self.get_callbacks()
        device_id = convert(self.device_id)
        proxy = convert(self.proxy)
        proxy_username = convert(self.proxy_username)
        proxy_password = convert(self.proxy_password)
        ca_certs_filename = convert(self.ca_certs_filename)
        tracefile = convert(self.tracefile)

        sp_session_config = ffi.new('sp_session_config *', {
            'api_version': self.api_version,
            'cache_location': cache_location,
            'settings_location': settings_location,
            'application_key': ffi.cast('void *', application_key),
            'application_key_size': len(application_key_bytes),
            'user_agent': user_agent,
            'callbacks': callbacks.make_sp_session_callbacks(),
            'compress_playlists': bool(self.compress_playlists),
            'dont_save_metadata_for_playlists': bool(
                self.dont_save_metadata_for_playlists),
            'initially_unload_playlists': bool(
                self.initially_unload_playlists),
            'device_id': device_id,
            'proxy': proxy,
            'proxy_username': proxy_username,
            'proxy_password': proxy_password,
            'ca_certs_filename': ca_certs_filename,
            'tracefile': tracefile,
        })

        spotify.weak_key_dict[sp_session_config] = [
            cache_location,
            settings_location,
            application_key,
            user_agent,
            callbacks,
            device_id,
            proxy,
            proxy_username,
            proxy_password,
            ca_certs_filename,
            tracefile,
        ]

        return sp_session_config


class Session(object):
    """The Spotify session.

    You can only have one session instance per process.

    If no ``config`` is provided, the default config is used. If no
    ``callbacks`` is provided, no callbacks are hooked up initially.

    :param config: the session config
    :type config: :class:`SessionConfig` or :class:`None`
    :param callbacks: the session callbacks
    :type callbacks: :class:`SessionCallbacks` or :class:`None`
    """

    def __init__(self, config=None, callbacks=None):
        if spotify.session_instance is not None:
            raise RuntimeError('Session has already been initialized')

        if config is None:
            config = SessionConfig()

        if callbacks is not None:
            config.callbacks = callbacks

        sp_session_config = config.make_sp_session_config()
        sp_session_ptr = ffi.new('sp_session **')

        Error.maybe_raise(lib.sp_session_create(
            sp_session_config, sp_session_ptr))

        self.sp_session = ffi.gc(sp_session_ptr[0], lib.sp_session_release)

        spotify.weak_key_dict[self.sp_session] = [sp_session_config]

        spotify.session_instance = self

    def login(self, username, password=None, remember_me=False, blob=None):
        """Authenticate to Spotify's servers.

        You can login with one of two combinations:

        - ``username`` and ``password``
        - ``username`` and ``blob``

        To get the ``blob`` string, you must once log in with ``username`` and
        ``password``. You'll then get the ``blob`` string passed to the
        :attr:`~SessionCallbacks.credentials_blob_updated` callback.

        If you set ``remember_me`` to :class:`True`, you can later login to the
        same account without providing any ``username`` or credentials by
        calling :meth:`relogin`.
        """

        username = ffi.new('char[]', to_bytes(username))

        if password is not None:
            password = ffi.new('char[]', to_bytes(password)) or ffi.NULL
            blob = ffi.NULL
        elif blob is not None:
            password = ffi.NULL
            blob = ffi.new('char[]', to_bytes(blob))
        else:
            raise AttributeError('password or blob is required to login')

        Error.maybe_raise(lib.sp_session_login(
            self.sp_session, username, password, bool(remember_me), blob))

    def relogin(self):
        """Relogin as the remembered user.

        To be able do this, you must previously have logged in with
        :meth:`login` with the ``remember_me`` argument set to :class:`True`.

        To check what user you'll be logged in as if you call this method, see
        :attr:`remembered_user_name`.
        """
        Error.maybe_raise(lib.sp_session_relogin(self.sp_session))

    @property
    def remembered_user_name(self):
        """The username of the remembered user from a previous :meth:`login`
        call."""
        return get_with_growing_buffer(
            lib.sp_session_remembered_user, self.sp_session)

    @property
    def user_name(self):
        """The username of the logged in user."""
        return to_unicode(lib.sp_session_user_name(self.sp_session))

    def forget_me(self):
        """Forget the remembered user from a previous :meth:`login` call."""
        Error.maybe_raise(lib.sp_session_forget_me(self.sp_session))

    @property
    def user(self):
        """The logged in :class:`User`."""
        sp_user = lib.sp_session_user(self.sp_session)
        if sp_user == ffi.NULL:
            return None
        return User(sp_user)

    def logout(self):
        """Log out the current user.

        If you logged in with the ``remember_me`` argument set to
        :class:`True`, you will also need to call :meth:`forget_me` to
        completely remove all credentials of the user that was logged in.
        """
        Error.maybe_raise(lib.sp_session_logout(self.sp_session))

    def flush_caches(self):
        """Write all cached data to disk.

        libspotify does this regularly and on logout, so you should never need
        to call this method yourself.
        """
        Error.maybe_raise(lib.sp_session_flush_caches(self.sp_session))

    @property
    def connection_state(self):
        """The current :class:`ConnectionState`."""
        return lib.sp_session_connectionstate(self.sp_session)

    def set_cache_size(self, size):
        """Set maximum size in MB for libspotify's cache.

        If set to 0 (the default), up to 10% of the free disk space will be
        used."""
        Error.maybe_raise(lib.sp_session_set_cache_size(
            self.sp_session, size))

    def process_events(self):
        """Process pending events in libspotify.

        This method must be called for most callbacks to be called. Without
        calling this method, you'll only get the callbacks that are called from
        internal libspotify threads. When the
        :attr:`~SessionCallbacks.notify_main_thread` callback is called (from
        an internal libspotify thread), it's your job to make sure this method
        is called (from the thread you use for accessing Spotify), so that
        further callbacks can be triggered (from the same thread).
        """
        next_timeout = ffi.new('int *')

        Error.maybe_raise(lib.sp_session_process_events(
            self.sp_session, next_timeout))

        return next_timeout[0]

    def player_load(self, track):
        """Load :class:`Track` for playback."""
        Error.maybe_raise(lib.sp_session_player_load(
            self.sp_session, track.sp_track))

    def player_seek(self, offset):
        """Seek to the offset in ms in the currently loaded track."""
        Error.maybe_raise(lib.sp_session_player_seek(self.sp_session, offset))

    def player_play(self, play=True):
        """Play the currently loaded track.

        This will cause audio data to be passed to the
        :attr:`~SessionCallbacks.music_delivery` callback.
        """
        Error.maybe_raise(lib.sp_session_player_play(
            self.sp_session, play))

    def player_unload(self):
        """Stops the currently playing track."""
        Error.maybe_raise(lib.sp_session_player_unload(self.sp_session))

    def player_prefetch(self, track):
        """Prefetch a :class:`Track` for playback.

        This can be used to make libspotify download and cache a track before
        playing it.
        """
        Error.maybe_raise(lib.sp_session_player_prefetch(
            self.sp_session, track.sp_track))

    @property
    def playlist_container(self):
        """The :class:`PlaylistContainer` for the currently logged in user."""
        sp_playlistcontainer = lib.sp_session_playlistcontainer(
            self.sp_session)
        if sp_playlistcontainer == ffi.NULL:
            return None
        return PlaylistContainer(sp_playlistcontainer)

    @property
    def inbox(self):
        """The inbox :class:`Playlist` for the currently logged in user."""
        sp_playlist = lib.sp_session_inbox_create(self.sp_session)
        if sp_playlist == ffi.NULL:
            return None
        return Playlist(sp_playlist, add_ref=False)

    @property
    def starred(self):
        """The starred :class:`Playlist` for the currently logged in user."""
        sp_playlist = lib.sp_session_starred_create(self.sp_session)
        if sp_playlist == ffi.NULL:
            return None
        return Playlist(sp_playlist, add_ref=False)

    def starred_for_user(self, canonical_username):
        """The starred :class:`Playlist` for the user with
        ``canonical_username``."""
        sp_playlist = lib.sp_session_starred_for_user_create(
            self.sp_session, to_bytes(canonical_username))
        if sp_playlist == ffi.NULL:
            return None
        return Playlist(sp_playlist, add_ref=False)

    def published_container_for_user(self, canonical_username=None):
        """The :class:`PlaylistContainer` of published playlists for the user
        with ``canonical_username``.

        If ``canonical_username`` isn't specified, the published container for
        the currently logged in user is returned."""
        if canonical_username is None:
            canonical_username = ffi.NULL
        else:
            canonical_username = to_bytes(canonical_username)
        sp_playlistcontainer = (
            lib.sp_session_publishedcontainer_for_user_create(
                self.sp_session, canonical_username))
        if sp_playlistcontainer == ffi.NULL:
            return None
        return PlaylistContainer(sp_playlistcontainer, add_ref=False)

    # TODO Add all sp_session_* methods
