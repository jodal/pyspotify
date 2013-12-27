from __future__ import unicode_literals

import functools
import logging
import operator

import spotify
from spotify import ffi, lib, utils


__all__ = [
    'SessionCallbacks',
    'SessionConfig',
    'Session',
]

logger = logging.getLogger(__name__)


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

        self._sp_session_callbacks = ffi.new('sp_session_callbacks *', {
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

    def _logged_in(self, sp_session, sp_error):
        if not spotify.session_instance:
            return
        if sp_error == spotify.ErrorType.OK:
            logger.info('Logged in')
        else:
            logger.error('Login error: %s', spotify.LibError(sp_error))
        if self.logged_in is not None:
            self.logged_in(
                spotify.session_instance, spotify.LibError(sp_error))

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
        error = spotify.LibError(sp_error)
        logger.error('Connection error: %s', error)
        if self.connection_error is not None:
            self.connection_error(spotify.session_instance, error)

    def _message_to_user(self, sp_session, data):
        if not spotify.session_instance:
            return
        data = utils.to_unicode(data).strip()
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
            buffer_ = ffi.buffer(
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
        data = utils.to_unicode(data).strip()
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
        error = spotify.LibError(sp_error)
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
        error = spotify.LibError(sp_error)
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


class SessionConfig(object):
    """The session config.

    Create an instance and assign to its attributes to configure. Then use the
    config object to create a session::

        >>> import spotify
        >>> config = spotify.SessionConfig()
        >>> config.user_agent = 'My awesome Spotify client'
        >>> # Etc ...
        >>> session = spotify.Session(config=config)
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

    See :meth:`Playlist.in_ram` for more details.
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

    # XXX libspotify 12.1.51 for Darwin does not have this field, so we remove
    # it for now to be able to run the same code on Linux and OS X.
    #ca_certs_filename = None
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
            with open(self.application_key_filename, 'rb') as fh:
                self.application_key = fh.read()
        assert len(self.application_key) == 321, 'Invalid application key'
        return self.application_key

    def get_callbacks(self):
        """Internal method."""
        if self.callbacks is None:
            self.callbacks = SessionCallbacks()
        return self.callbacks

    def make_sp_session_config(self):
        """Internal method."""

        cache_location = ffi.new('char[]', utils.to_bytes(self.cache_location))
        settings_location = ffi.new(
            'char[]', utils.to_bytes(self.settings_location))
        application_key_bytes = self.get_application_key()
        application_key = ffi.new('char[]', application_key_bytes)
        user_agent = ffi.new('char[]', utils.to_bytes(self.user_agent))
        callbacks = self.get_callbacks()
        device_id = utils.to_char_or_null(self.device_id)
        proxy = utils.to_char_or_null(self.proxy)
        proxy_username = utils.to_char_or_null(self.proxy_username)
        proxy_password = utils.to_char_or_null(self.proxy_password)
        # XXX See explanation above
        #ca_certs_filename = utils.to_char_or_null(self.ca_certs_filename)
        tracefile = utils.to_char_or_null(self.tracefile)

        sp_session_config = ffi.new('sp_session_config *', {
            'api_version': self.api_version,
            'cache_location': cache_location,
            'settings_location': settings_location,
            'application_key': ffi.cast('void *', application_key),
            'application_key_size': len(application_key_bytes),
            'user_agent': user_agent,
            'callbacks': callbacks._sp_session_callbacks,
            'compress_playlists': bool(self.compress_playlists),
            'dont_save_metadata_for_playlists': bool(
                self.dont_save_metadata_for_playlists),
            'initially_unload_playlists': bool(
                self.initially_unload_playlists),
            'device_id': device_id,
            'proxy': proxy,
            'proxy_username': proxy_username,
            'proxy_password': proxy_password,
            # XXX See explanation above
            #'ca_certs_filename': ca_certs_filename,
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
            # XXX See explanation above
            #ca_certs_filename,
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

        spotify.Error.maybe_raise(lib.sp_session_create(
            sp_session_config, sp_session_ptr))

        self._sp_session = ffi.gc(sp_session_ptr[0], lib.sp_session_release)

        spotify.weak_key_dict[self._sp_session] = [sp_session_config]

        self._callbacks = config.callbacks
        self.offline = Offline(self)
        self.player = Player(self)
        self.social = Social(self)
        spotify.session_instance = self

    offline = None
    """An :class:`~spotify.session.Offline` instance for controlling offline
    sync."""

    player = None
    """A :class:`~spotify.session.Player` instance for controlling playback."""

    social = None
    """A :class:`~spotify.session.Social` instance for controlling social
    sharing."""

    @property
    def callbacks(self):
        """The session's :class:`SessionCallbacks` instance.

        You can assign functions to the instance's attributes to change
        callbacks on the fly.
        """
        return self._callbacks

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

        username = ffi.new('char[]', utils.to_bytes(username))

        if password is not None:
            password = ffi.new('char[]', utils.to_bytes(password)) or ffi.NULL
            blob = ffi.NULL
        elif blob is not None:
            password = ffi.NULL
            blob = ffi.new('char[]', utils.to_bytes(blob))
        else:
            raise AttributeError('password or blob is required to login')

        spotify.Error.maybe_raise(lib.sp_session_login(
            self._sp_session, username, password, bool(remember_me), blob))

    def relogin(self):
        """Relogin as the remembered user.

        To be able do this, you must previously have logged in with
        :meth:`login` with the ``remember_me`` argument set to :class:`True`.

        To check what user you'll be logged in as if you call this method, see
        :attr:`remembered_user_name`.
        """
        spotify.Error.maybe_raise(lib.sp_session_relogin(self._sp_session))

    @property
    def remembered_user_name(self):
        """The username of the remembered user from a previous :meth:`login`
        call."""
        return utils.get_with_growing_buffer(
            lib.sp_session_remembered_user, self._sp_session)

    @property
    def user_name(self):
        """The username of the logged in user."""
        return utils.to_unicode(lib.sp_session_user_name(self._sp_session))

    def forget_me(self):
        """Forget the remembered user from a previous :meth:`login` call."""
        spotify.Error.maybe_raise(lib.sp_session_forget_me(self._sp_session))

    @property
    def user(self):
        """The logged in :class:`User`."""
        sp_user = lib.sp_session_user(self._sp_session)
        if sp_user == ffi.NULL:
            return None
        return spotify.User(sp_user=sp_user)

    def logout(self):
        """Log out the current user.

        If you logged in with the ``remember_me`` argument set to
        :class:`True`, you will also need to call :meth:`forget_me` to
        completely remove all credentials of the user that was logged in.
        """
        spotify.Error.maybe_raise(lib.sp_session_logout(self._sp_session))

    def flush_caches(self):
        """Write all cached data to disk.

        libspotify does this regularly and on logout, so you should never need
        to call this method yourself.
        """
        spotify.Error.maybe_raise(
            lib.sp_session_flush_caches(self._sp_session))

    @property
    def connection_state(self):
        """The current :class:`ConnectionState`."""
        return spotify.ConnectionState(
            lib.sp_session_connectionstate(self._sp_session))

    def set_cache_size(self, size):
        """Set maximum size in MB for libspotify's cache.

        If set to 0 (the default), up to 10% of the free disk space will be
        used."""
        spotify.Error.maybe_raise(lib.sp_session_set_cache_size(
            self._sp_session, size))

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

        spotify.Error.maybe_raise(lib.sp_session_process_events(
            self._sp_session, next_timeout))

        return next_timeout[0]

    @property
    def playlist_container(self):
        """The :class:`PlaylistContainer` for the currently logged in user."""
        sp_playlistcontainer = lib.sp_session_playlistcontainer(
            self._sp_session)
        if sp_playlistcontainer == ffi.NULL:
            return None
        return spotify.PlaylistContainer(sp_playlistcontainer)

    @property
    def inbox(self):
        """The inbox :class:`Playlist` for the currently logged in user."""
        sp_playlist = lib.sp_session_inbox_create(self._sp_session)
        if sp_playlist == ffi.NULL:
            return None
        return spotify.Playlist(sp_playlist=sp_playlist, add_ref=False)

    def inbox_post_tracks(
            self, canonical_username, tracks, message, callback=None):
        """Post a ``message`` and one or more ``tracks`` to the inbox of the
        user with the given ``canonical_username``.

        ``tracks`` can be a single :class:`~spotify.Track` or a list of
        :class:`~spotify.Track` objects.

        Returns an :class:`InboxPostResult` that can be used to check if the
        request completed successfully.

        If callback isn't :class:`None`, it is called with an
        :class:`InboxPostResult` instance when the request has completed.
        """
        return spotify.InboxPostResult(
            canonical_username, tracks, message, callback)

    @property
    def starred(self):
        """The starred :class:`Playlist` for the currently logged in user."""
        sp_playlist = lib.sp_session_starred_create(self._sp_session)
        if sp_playlist == ffi.NULL:
            return None
        return spotify.Playlist(sp_playlist=sp_playlist, add_ref=False)

    def starred_for_user(self, canonical_username):
        """The starred :class:`Playlist` for the user with
        ``canonical_username``."""
        sp_playlist = lib.sp_session_starred_for_user_create(
            self._sp_session, utils.to_bytes(canonical_username))
        if sp_playlist == ffi.NULL:
            return None
        return spotify.Playlist(sp_playlist=sp_playlist, add_ref=False)

    def published_playlists_for_user(self, canonical_username=None):
        """The :class:`PlaylistContainer` of published playlists for the user
        with ``canonical_username``.

        If ``canonical_username`` isn't specified, the published container for
        the currently logged in user is returned."""
        if canonical_username is None:
            canonical_username = ffi.NULL
        else:
            canonical_username = utils.to_bytes(canonical_username)
        sp_playlistcontainer = (
            lib.sp_session_publishedcontainer_for_user_create(
                self._sp_session, canonical_username))
        if sp_playlistcontainer == ffi.NULL:
            return None
        return spotify.PlaylistContainer(sp_playlistcontainer, add_ref=False)

    def preferred_bitrate(self, bitrate):
        """Set preferred :class:`Bitrate` for music streaming."""
        spotify.Error.maybe_raise(lib.sp_session_preferred_bitrate(
            self._sp_session, bitrate))

    def preferred_offline_bitrate(self, bitrate, allow_resync=False):
        """Set preferred :class:`Bitrate` for offline sync.

        If ``allow_resync`` is :class:`True` libspotify may resynchronize
        already synced tracks."""
        spotify.Error.maybe_raise(lib.sp_session_preferred_offline_bitrate(
            self._sp_session, bitrate, allow_resync))

    def get_volume_normalization(self):
        return bool(lib.sp_session_get_volume_normalization(self._sp_session))

    def set_volume_normalization(self, value):
        spotify.Error.maybe_raise(lib.sp_session_set_volume_normalization(
            self._sp_session, value))

    volume_normalization = property(
        get_volume_normalization, set_volume_normalization)
    """Whether volume normalization is active or not.

    Set to :class:`True` or :class:`False` to change.
    """

    @property
    def user_country(self):
        """The country of the currently logged in user.

        The :attr:`~SessionCallbacks.offline_status_updated` callback is called
        when this changes.
        """
        return utils.to_country(lib.sp_session_user_country(self._sp_session))

    def search(
            self, query, callback=None,
            track_offset=0, track_count=20,
            album_offset=0, album_count=20,
            artist_offset=0, artist_count=20,
            playlist_offset=0, playlist_count=20,
            search_type=None):
        """
        Search Spotify for tracks, albums, artists, and playlists matching
        ``query``.

        The ``query`` string can be free format, or use some prefixes like
        ``title:`` and ``artist:`` to limit what to match on. There is no
        official docs on the search query format, but there's a `Spotify blog
        post
        <https://www.spotify.com/blog/archives/2008/01/22/searching-spotify/>`_
        from 2008 with some examples.

        If ``callback`` isn't :class:`None`, it is expected to be a callable
        that accepts a single argument, a :class:`Search` instance, when
        the search completes.

        The ``*_offset`` and ``*_count`` arguments can be used to retrieve more
        search results. libspotify will currently not respect ``*_count``
        values higher than 200, though this may change at any time as the limit
        isn't documented in any official docs. If you want to retrieve more
        than 200 results, you'll have to search multiple times with different
        ``*_offset`` values. See the ``*_total`` attributes on the
        :class:`Search` to see how many results exists, and to figure out
        how many searches you'll need to make to retrieve everything.

        ``search_type`` is a :class:`SearchType` value. It defaults to
        :attr:`SearchType.STANDARD`.
        """
        return spotify.Search(
            query=query, callback=callback,
            track_offset=track_offset, track_count=track_count,
            album_offset=album_offset, album_count=album_count,
            artist_offset=artist_offset, artist_count=artist_count,
            playlist_offset=playlist_offset, playlist_count=playlist_count,
            search_type=search_type)


class Offline(object):
    """Offline sync controller.

    You'll never need to create an instance of this class yourself. You'll find
    it ready to use as the :attr:`~Session.offline` attribute on the
    :class:`Session` instance.
    """

    def __init__(self, session):
        self._session = session

    def set_connection_type(self, connection_type):
        """Set the :class:`ConnectionType`.

        This is used together with :meth:`set_connection_rules` to control
        offline syncing and network usage.
        """
        spotify.Error.maybe_raise(lib.sp_session_set_connection_type(
            self._session._sp_session, connection_type))

    def set_connection_rules(self, *connection_rules):
        """Set one or more :class:`connection rules <ConnectionRule>`.

        This is used together with :meth:`set_connection_type` to control
        offline syncing and network usage.

        To remove all rules, simply call this method without any arguments.
        """
        connection_rules = functools.reduce(operator.or_, connection_rules, 0)
        spotify.Error.maybe_raise(lib.sp_session_set_connection_rules(
            self._session._sp_session, connection_rules))

    @property
    def tracks_to_sync(self):
        """Total number of tracks that needs download before everything from
        all playlists that is marked for offline is fully synchronized.
        """
        return lib.sp_offline_tracks_to_sync(self._session._sp_session)

    @property
    def num_playlists(self):
        """Number of playlists that is marked for offline synchronization."""
        return lib.sp_offline_num_playlists(self._session._sp_session)

    @property
    def sync_status(self):
        """The :class:`OfflineSyncStatus` or :class:`None` if not syncing.

        The :attr:`~SessionCallbacks.offline_status_updated` callback is called
        when this is updated.
        """
        sp_offline_sync_status = ffi.new('sp_offline_sync_status *')
        syncing = lib.sp_offline_sync_get_status(
            self._session._sp_session, sp_offline_sync_status)
        if syncing:
            return spotify.OfflineSyncStatus(sp_offline_sync_status)

    @property
    def time_left(self):
        """The number of seconds until the user has to get online and
        relogin."""
        return lib.sp_offline_time_left(self._session._sp_session)


class Player(object):
    """Playback controller.

    You'll never need to create an instance of this class yourself. You'll find
    it ready to use as the :attr:`~Session.player` attribute on the
    :class:`Session` instance.
    """

    def __init__(self, session):
        self._session = session

    def load(self, track):
        """Load :class:`Track` for playback."""
        spotify.Error.maybe_raise(lib.sp_session_player_load(
            self._session._sp_session, track._sp_track))

    def seek(self, offset):
        """Seek to the offset in ms in the currently loaded track."""
        spotify.Error.maybe_raise(
            lib.sp_session_player_seek(self._session._sp_session, offset))

    def play(self, play=True):
        """Play the currently loaded track.

        This will cause audio data to be passed to the
        :attr:`~SessionCallbacks.music_delivery` callback.

        If ``play`` is set to :class:`False`, playback will be paused.
        """
        spotify.Error.maybe_raise(lib.sp_session_player_play(
            self._session._sp_session, play))

    def unload(self):
        """Stops the currently playing track."""
        spotify.Error.maybe_raise(
            lib.sp_session_player_unload(self._session._sp_session))

    def prefetch(self, track):
        """Prefetch a :class:`Track` for playback.

        This can be used to make libspotify download and cache a track before
        playing it.
        """
        spotify.Error.maybe_raise(lib.sp_session_player_prefetch(
            self._session._sp_session, track._sp_track))


class Social(object):
    """Social sharing controller.

    You'll never need to create an instance of this class yourself. You'll find
    it ready to use as the :attr:`~Session.social` attribute on the
    :class:`Session` instance.
    """

    def __init__(self, session):
        self._session = session

    def is_private_session(self):
        return bool(
            lib.sp_session_is_private_session(self._session._sp_session))

    def set_private_session(self, value):
        # TODO Segfaults unless we're logged in and have called
        # process_events() at least once afterwards. Need to identify the
        # relevant session callback, set a threading.Event from it, and check
        # here if that event is set before calling the sp_ function.
        spotify.Error.maybe_raise(lib.sp_session_set_private_session(
            self._session._sp_session, value))

    private_session = property(
        is_private_session, set_private_session)
    """Whether the session is private.

    Set to :class:`True` or :class:`False` to change.
    """

    def is_scrobbling(self, social_provider):
        """Get the :class:`ScrobblingState` for the given
        ``social_provider``."""
        scrobbling_state = ffi.new('sp_scrobbling_state *')
        spotify.Error.maybe_raise(lib.sp_session_is_scrobbling(
            self._session._sp_session, social_provider, scrobbling_state))
        return spotify.ScrobblingState(scrobbling_state[0])

    def is_scrobbling_possible(self, social_provider):
        """Check if the scrobbling settings should be shown to the user."""
        out = ffi.new('bool *')
        spotify.Error.maybe_raise(lib.sp_session_is_scrobbling_possible(
            self._session._sp_session, social_provider, out))
        return bool(out[0])

    def set_scrobbling(self, social_provider, scrobbling_state):
        """Set the ``scrobbling_state`` for the given ``social_provider``."""
        spotify.Error.maybe_raise(lib.sp_session_set_scrobbling(
            self._session._sp_session, social_provider, scrobbling_state))

    def set_social_credentials(self, social_provider, username, password):
        """Set the user's credentials with a social provider.

        Currently this is only relevant for Last.fm. Call
        :meth:`set_scrobbling` to force an authentication attempt with the
        provider. If authentication fails a
        :attr:`~SessionCallbacks.scrobble_error` callback will be sent.
        """
        username = ffi.new('char[]', utils.to_bytes(username))
        password = ffi.new('char[]', utils.to_bytes(password))
        spotify.Error.maybe_raise(lib.sp_session_set_social_credentials(
            self._session._sp_session, social_provider, username, password))
