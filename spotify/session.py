from __future__ import unicode_literals

import functools
import logging
import operator
import weakref

import spotify
from spotify import ffi, lib, utils


__all__ = [
    'Session',
    'SessionEvent',
]

logger = logging.getLogger(__name__)


class Session(utils.EventEmitter):
    """The Spotify session.

    If no ``config`` is provided, the default config is used.

    The session object will emit a number of events. See :class:`SessionEvent`
    for a list of all available events and how to connect your own listener
    functions up to get called when the events happens.

    .. warning::

        You can only have one :class:`Session` instance per process. This is a
        libspotify limitation. If you create a second :class:`Session` instance
        in the same process pyspotify will raise a :exc:`RuntimeError` with the
        message "Session has already been initialized".

    :param config: the session config
    :type config: :class:`Config` or :class:`None`
    """

    def __init__(self, config=None):
        super(Session, self).__init__()

        if spotify.session_instance is not None:
            raise RuntimeError('Session has already been initialized')

        if config is not None:
            self.config = config
        else:
            self.config = spotify.Config()

        if self.config.application_key is None:
            self.config.load_application_key_file()

        sp_session_ptr = ffi.new('sp_session **')

        spotify.Error.maybe_raise(lib.sp_session_create(
            self.config._sp_session_config, sp_session_ptr))

        self._sp_session = ffi.gc(sp_session_ptr[0], lib.sp_session_release)

        self._cache = weakref.WeakValueDictionary()
        self._emitters = []

        self.offline = Offline(self)
        self.player = Player(self)
        self.social = Social(self)
        spotify.session_instance = self

    _cache = None
    """A mapping from sp_* objects to their corresponding Python instances.

    The ``_cached`` helper contructors on wrapper objects use this cache for
    finding and returning existing alive wrapper objects for the sp_* object is
    about to create a wrapper for.

    The cache *does not* keep objects alive. It's only a means for looking up
    the objects if they are kept alive somewhere else in the application.

    Internal attribute.
    """

    _emitters = None
    """A list of event emitters with attached listeners.

    When an event emitter has attached event listeners, we must keep the
    emitter alive for as long as the listeners are attached. This is achieved
    by adding them to this list.

    When creating wrapper objects around sp_* objects we must also return the
    existing wrapper objects instead of creating new ones so that the set of
    event listeners on the wrapper object can be modified. This is achieved
    with a combination of this list and the :attr:`_cache` mapping.

    Internal attribute.
    """

    config = None
    """A :class:`Config` instance with the current configuration.

    Once the session has been created, changing the attributes of this object
    will generally have no effect.
    """

    offline = None
    """An :class:`~spotify.session.Offline` instance for controlling offline
    sync."""

    player = None
    """A :class:`~spotify.session.Player` instance for controlling playback."""

    social = None
    """A :class:`~spotify.session.Social` instance for controlling social
    sharing."""

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
        :attr:`~SessionEvent.NOTIFY_MAIN_THREAD` event is emitted (from an
        internal libspotify thread), it's your job to make sure this method is
        called (from the thread you use for accessing Spotify), so that further
        callbacks can be triggered (from the same thread).
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
        return spotify.PlaylistContainer._cached(
            sp_playlistcontainer, add_ref=True)

    @property
    def inbox(self):
        """The inbox :class:`Playlist` for the currently logged in user."""
        sp_playlist = lib.sp_session_inbox_create(self._sp_session)
        if sp_playlist == ffi.NULL:
            return None
        return spotify.Playlist._cached(sp_playlist=sp_playlist, add_ref=False)

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
        return spotify.Playlist._cached(sp_playlist=sp_playlist, add_ref=False)

    def starred_for_user(self, canonical_username):
        """The starred :class:`Playlist` for the user with
        ``canonical_username``."""
        sp_playlist = lib.sp_session_starred_for_user_create(
            self._sp_session, utils.to_bytes(canonical_username))
        if sp_playlist == ffi.NULL:
            return None
        return spotify.Playlist._cached(sp_playlist=sp_playlist, add_ref=False)

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
        return spotify.PlaylistContainer._cached(
            sp_playlistcontainer, add_ref=False)

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

    @property
    def volume_normalization(self):
        """Whether volume normalization is active or not.

        Set to :class:`True` or :class:`False` to change.
        """
        return bool(lib.sp_session_get_volume_normalization(self._sp_session))

    @volume_normalization.setter
    def volume_normalization(self, value):
        spotify.Error.maybe_raise(lib.sp_session_set_volume_normalization(
            self._sp_session, value))

    @property
    def user_country(self):
        """The country of the currently logged in user.

        The :attr:`~SessionEvent.OFFLINE_STATUS_UPDATED` event is emitted on
        the session object when this changes.
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

        This is used together with :meth:`~Offline.set_connection_rules` to
        control offline syncing and network usage.
        """
        spotify.Error.maybe_raise(lib.sp_session_set_connection_type(
            self._session._sp_session, connection_type))

    def set_connection_rules(self, *connection_rules):
        """Set one or more :class:`connection rules <ConnectionRule>`.

        This is used together with :meth:`~Offline.set_connection_type` to
        control offline syncing and network usage.

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

        The :attr:`~SessionEvent.OFFLINE_STATUS_UPDATED` event is emitted on
        the session object when this is updated.
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

    @property
    def private_session(self):
        """Whether the session is private.

        Set to :class:`True` or :class:`False` to change.
        """
        return bool(
            lib.sp_session_is_private_session(self._session._sp_session))

    @private_session.setter
    def private_session(self, value):
        # TODO Segfaults unless we're logged in and have called
        # process_events() at least once afterwards. Need to identify the
        # relevant session callback, set a threading.Event from it, and check
        # here if that event is set before calling the sp_ function.
        spotify.Error.maybe_raise(lib.sp_session_set_private_session(
            self._session._sp_session, value))

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
        :attr:`~SessionEvent.SCROBBLE_ERROR` event will be emitted on the
        :class:`Session` object.
        """
        username = ffi.new('char[]', utils.to_bytes(username))
        password = ffi.new('char[]', utils.to_bytes(password))
        spotify.Error.maybe_raise(lib.sp_session_set_social_credentials(
            self._session._sp_session, social_provider, username, password))


class SessionEvent(object):
    """Session events.

    Using the :class:`Session` object, you can register listener functions to
    be called when various session related events occurs. This class enumerates
    the available events and the arguments your listener functions will be
    called with.

    Example usage::

        import spotify

        def logged_in(session, error_type):
            if error_type is spotify.ErrorType.OK:
                print('Logged in as %s' % session.user)
            else:
                print('Login failed: %s' % error_type)

        session = spotify.Session()
        session.on(spotify.SessionEvent.LOGGED_IN, logged_in)
        session.login('alice', 's3cret')

    All events will cause debug log statements to be emitted, even if no
    listeners are registered. Thus, there is no need to register listener
    functions just to log that they're called.
    """

    LOGGED_IN = 'logged_in'
    """Called when login has completed.

    :param session: the current session
    :type session: :class:`Session`
    :param error_type: the login error type
    :type error_type: :class:`ErrorType`
    """

    LOGGED_OUT = 'logged_out'
    """Called when logout has completed or there is a permanent connection
    error.

    :param session: the current session
    :type session: :class:`Session`
    """

    METADATA_UPDATED = 'metadata_updated'
    """Called when some metadata has been updated.

    There is no way to know what metadata was updated, so you'll have to
    refresh all you metadata caches.

    :param session: the current session
    :type session: :class:`Session`
    """

    CONNECTION_ERROR = 'connection_error'
    """Called when there is a connection error and libspotify has problems
    reconnecting to the Spotify service.

    May be called repeatedly as long as the problem persists. Will be called
    with an :attr:`ErrorType.OK` error when the problem is resolved.

    :param session: the current session
    :type session: :class:`Session`
    :param error_type: the connection error type
    :type error_type: :class:`ErrorType`
    """

    MESSAGE_TO_USER = 'message_to_user'
    """Called when libspotify wants to show a message to the end user.

    :param session: the current session
    :type session: :class:`Session`
    :param data: the message
    :type data: text
    """

    NOTIFY_MAIN_THREAD = 'notify_main_thread'
    """Called when processing on the main thread is needed.

    When this is called, you should call :meth:`~Session.process_events` from
    your main thread. Failure to do so may cause request timeouts, or a lost
    connection.

    .. warning::

        This event is emitted from an internal libspotify thread. Thus, your
        event listener must not block, and must use proper synchronization
        around anything it does.

    :param session: the current session
    :type session: :class:`Session`
    """

    MUSIC_DELIVERY = 'music_delivery'
    """Called when there is decompressed audio data available.

    If the function returns a lower number of frames consumed than
    ``num_frames``, libspotify will retry delivery of the unconsumed frames in
    about 100ms. This can be used for rate limiting if libspotify is giving you
    audio data too fast.

    .. note::

        You can register at most one event listener for this event.

    .. warning::

        This event is emitted from an internal libspotify thread. Thus, your
        event listener must not block, and must use proper synchronization
        around anything it does.

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

    PLAY_TOKEN_LOST = 'play_token_lost'
    """Music has been paused because an account only allows music to be played
    from one location simultaneously.

    When this event is emitted, you should pause playback.

    :param session: the current session
    :type session: :class:`Session`
    """

    LOG_MESSAGE = 'log_message'
    """Called when libspotify have something to log.

    Note that pyspotify logs this for you, so you'll probably never need to
    register a listener for this event.

    :param session: the current session
    :type session: :class:`Session`
    :param data: the message
    :type data: text
    """

    END_OF_TRACK = 'end_of_track'
    """Called when all audio data for the current track has been delivered.

    :param session: the current session
    :type session: :class:`Session`
    """

    STREAMING_ERROR = 'streaming_error'
    """Called when audio streaming cannot start or continue.

    :param session: the current session
    :type session: :class:`Session`
    :param error_type: the streaming error type
    :type error_type: :class:`ErrorType`
    """

    USER_INFO_UPDATED = 'user_info_updated'
    """Called when anything related to :class:`User` objects is updated.

    :param session: the current session
    :type session: :class:`Session`
    """

    START_PLAYBACK = 'start_playback'
    """Called when audio playback should start.

    You need to implement a listener for the :attr:`GET_AUDIO_BUFFER_STATS`
    event for the :attr:`START_PLAYBACK` event to be useful.

    .. warning::

        This event is emitted from an internal libspotify thread. Thus, your
        event listener must not block, and must use proper synchronization
        around anything it does.

    :param session: the current session
    :type session: :class:`Session`
    """

    STOP_PLAYBACK = 'stop_playback'
    """Called when audio playback should stop.

    You need to implement a listener for the :attr:`GET_AUDIO_BUFFER_STATS`
    event for the :attr:`STOP_PLAYBACK` event to be useful.

    .. warning::

        This event is emitted from an internal libspotify thread. Thus, your
        event listener must not block, and must use proper synchronization
        around anything it does.

    :param session: the current session
    :type session: :class:`Session`
    """

    GET_AUDIO_BUFFER_STATS = 'get_audio_buffer_stats'
    """Called to query the application about its audio buffer.

    .. note::

        You can register at most one event listener for this event.

    .. warning::

        This event is emitted from an internal libspotify thread. Thus, your
        event listener must not block, and must use proper synchronization
        around anything it does.

    :param session: the current session
    :type session: :class:`Session`
    :returns: an :class:`AudioBufferStats` instance
    """

    OFFLINE_STATUS_UPDATED = 'offline_status_updated'
    """Called when offline sync status is updated.

    :param session: the current session
    :type session: :class:`Session`
    """

    CREDENTIALS_BLOB_UPDATED = 'credentials_blob_updated'
    """Called when storable credentials have been updated, typically right
    after login.

    The ``blob`` argument can be stored and later passed to
    :meth:`~Session.login` to login without storing the user's password.

    :param session: the current session
    :type session: :class:`Session`
    :param blob: the authentication blob
    :type blob: bytestring
    """

    CONNECTION_STATE_UPDATED = 'connection_state_updated'
    """Called when the connection state is updated.

    The connection state includes login, logout, offline mode, etc.

    :param session: the current session
    :type session: :class:`Session`
    """

    SCROBBLE_ERROR = 'scrobble_error'
    """Called when there is a scrobble error event.

    :param session: the current session
    :type session: :class:`Session`
    :param error_type: the scrobble error type
    :type error_type: :class:`ErrorType`
    """

    PRIVATE_SESSION_MODE_CHANGED = 'private_session_mode_changed'
    """Called when there is a change in the private session mode.

    :param session: the current session
    :type session: :class:`Session`
    :param is_private: whether the session is private
    :type is_private: bool
    """


class _SessionCallbacks(object):
    """Internal class."""

    @classmethod
    def get_struct(cls):
        return ffi.new('sp_session_callbacks *', {
            'logged_in': cls.logged_in,
            'logged_out': cls.logged_out,
            'metadata_updated': cls.metadata_updated,
            'connection_error': cls.connection_error,
            'message_to_user': cls.message_to_user,
            'notify_main_thread': cls.notify_main_thread,
            'music_delivery': cls.music_delivery,
            'play_token_lost': cls.play_token_lost,
            'log_message': cls.log_message,
            'end_of_track': cls.end_of_track,
            'streaming_error': cls.streaming_error,
            'userinfo_updated': cls.user_info_updated,
            'start_playback': cls.start_playback,
            'stop_playback': cls.stop_playback,
            'get_audio_buffer_stats': cls.get_audio_buffer_stats,
            'offline_status_updated': cls.offline_status_updated,
            'credentials_blob_updated': cls.credentials_blob_updated,
            'connectionstate_updated': cls.connection_state_updated,
            'scrobble_error': cls.scrobble_error,
            'private_session_mode_changed': cls.private_session_mode_changed,
        })

    @staticmethod
    @ffi.callback('void(sp_session *, sp_error)')
    def logged_in(sp_session, sp_error):
        if not spotify.session_instance:
            return
        if sp_error == spotify.ErrorType.OK:
            logger.info('Logged in')
        else:
            logger.error('Login error: %s', spotify.ErrorType(sp_error))
        spotify.session_instance.emit(
            SessionEvent.LOGGED_IN,
            spotify.session_instance, spotify.ErrorType(sp_error))

    @staticmethod
    @ffi.callback('void(sp_session *)')
    def logged_out(sp_session):
        if not spotify.session_instance:
            return
        logger.info('Logged out')
        spotify.session_instance.emit(
            SessionEvent.LOGGED_OUT, spotify.session_instance)

    @staticmethod
    @ffi.callback('void(sp_session *)')
    def metadata_updated(sp_session):
        if not spotify.session_instance:
            return
        logger.debug('Metadata updated')
        spotify.session_instance.emit(
            SessionEvent.METADATA_UPDATED, spotify.session_instance)

    @staticmethod
    @ffi.callback('void(sp_session *, sp_error)')
    def connection_error(sp_session, sp_error):
        if not spotify.session_instance:
            return
        error_type = spotify.ErrorType(sp_error)
        logger.error('Connection error: %s', error_type)
        spotify.session_instance.emit(
            SessionEvent.CONNECTION_ERROR,
            spotify.session_instance, error_type)

    @staticmethod
    @ffi.callback('void(sp_session *, const char *)')
    def message_to_user(sp_session, data):
        if not spotify.session_instance:
            return
        data = utils.to_unicode(data).strip()
        logger.debug('Message to user: %s', data)
        spotify.session_instance.emit(
            SessionEvent.MESSAGE_TO_USER, spotify.session_instance, data)

    @staticmethod
    @ffi.callback('void(sp_session *)')
    def notify_main_thread(sp_session):
        if not spotify.session_instance:
            return
        logger.debug('Notify main thread')
        spotify.session_instance.emit(
            SessionEvent.NOTIFY_MAIN_THREAD, spotify.session_instance)

    @staticmethod
    @ffi.callback(
        'int(sp_session *, const sp_audioformat *, const void *, int)')
    def music_delivery(sp_session, sp_audioformat, frames, num_frames):
        if not spotify.session_instance:
            return 0
        if spotify.session_instance.num_listeners(
                SessionEvent.MUSIC_DELIVERY) == 0:
            logger.debug('Got music delivery, but no event listener')
            return 0
        logger.debug('Got music delivery of %d frames', num_frames)
        audio_format = spotify.AudioFormat(sp_audioformat)
        buffer_ = ffi.buffer(
            frames, audio_format.frame_size() * num_frames)
        frames_bytes = buffer_[:]
        return spotify.session_instance.call(
            SessionEvent.MUSIC_DELIVERY,
            spotify.session_instance, audio_format, frames_bytes, num_frames)

    @staticmethod
    @ffi.callback('void(sp_session *)')
    def play_token_lost(sp_session):
        if not spotify.session_instance:
            return
        logger.debug('Play token lost')
        spotify.session_instance.emit(
            SessionEvent.PLAY_TOKEN_LOST, spotify.session_instance)

    @staticmethod
    @ffi.callback('void(sp_session *, const char *)')
    def log_message(sp_session, data):
        if not spotify.session_instance:
            return
        data = utils.to_unicode(data).strip()
        logger.debug('Log message from Spotify: %s', data)
        spotify.session_instance.emit(
            SessionEvent.LOG_MESSAGE, spotify.session_instance, data)

    @staticmethod
    @ffi.callback('void(sp_session *)')
    def end_of_track(sp_session):
        if not spotify.session_instance:
            return
        logger.debug('End of track')
        spotify.session_instance.emit(
            SessionEvent.END_OF_TRACK, spotify.session_instance)

    @staticmethod
    @ffi.callback('void(sp_session *, sp_error)')
    def streaming_error(sp_session, sp_error):
        if not spotify.session_instance:
            return
        error_type = spotify.ErrorType(sp_error)
        logger.error('Streaming error: %s', error_type)
        spotify.session_instance.emit(
            SessionEvent.STREAMING_ERROR,
            spotify.session_instance, error_type)

    @staticmethod
    @ffi.callback('void(sp_session *)')
    def user_info_updated(sp_session):
        if not spotify.session_instance:
            return
        logger.debug('User info updated')
        spotify.session_instance.emit(
            SessionEvent.USER_INFO_UPDATED, spotify.session_instance)

    @staticmethod
    @ffi.callback('void(sp_session *)')
    def start_playback(sp_session):
        if not spotify.session_instance:
            return
        logger.debug('Start playback called')
        spotify.session_instance.emit(
            SessionEvent.START_PLAYBACK, spotify.session_instance)

    @staticmethod
    @ffi.callback('void(sp_session *)')
    def stop_playback(sp_session):
        if not spotify.session_instance:
            return
        logger.debug('Stop playback called')
        spotify.session_instance.emit(
            SessionEvent.STOP_PLAYBACK, spotify.session_instance)

    @staticmethod
    @ffi.callback('void(sp_session *, sp_audio_buffer_stats *)')
    def get_audio_buffer_stats(sp_session, sp_audio_buffer_stats):
        if not spotify.session_instance:
            return
        if spotify.session_instance.num_listeners(
                SessionEvent.GET_AUDIO_BUFFER_STATS) == 0:
            logger.debug('Audio buffer stats requested, but no listener')
            return
        logger.debug('Audio buffer stats requested')
        stats = spotify.session_instance.call(
            SessionEvent.GET_AUDIO_BUFFER_STATS, spotify.session_instance)
        sp_audio_buffer_stats.samples = stats.samples
        sp_audio_buffer_stats.stutter = stats.stutter

    @staticmethod
    @ffi.callback('void(sp_session *)')
    def offline_status_updated(sp_session):
        if not spotify.session_instance:
            return
        logger.debug('Offline status updated')
        spotify.session_instance.emit(
            SessionEvent.OFFLINE_STATUS_UPDATED, spotify.session_instance)

    @staticmethod
    @ffi.callback('void(sp_session *, const char *)')
    def credentials_blob_updated(sp_session, data):
        if not spotify.session_instance:
            return
        data = ffi.string(data)
        logger.debug('Credentials blob updated: %r', data)
        spotify.session_instance.emit(
            SessionEvent.CREDENTIALS_BLOB_UPDATED,
            spotify.session_instance, data)

    @staticmethod
    @ffi.callback('void(sp_session *)')
    def connection_state_updated(sp_session):
        if not spotify.session_instance:
            return
        logger.debug('Connection state updated')
        spotify.session_instance.emit(
            SessionEvent.CONNECTION_STATE_UPDATED,
            spotify.session_instance)

    @staticmethod
    @ffi.callback('void(sp_session *, sp_error)')
    def scrobble_error(sp_session, sp_error):
        if not spotify.session_instance:
            return
        error_type = spotify.ErrorType(sp_error)
        logger.error('Scrobble error: %s', error_type)
        spotify.session_instance.emit(
            SessionEvent.SCROBBLE_ERROR,
            spotify.session_instance, error_type)

    @staticmethod
    @ffi.callback('void(sp_session *, bool)')
    def private_session_mode_changed(sp_session, is_private):
        if not spotify.session_instance:
            return
        is_private = bool(is_private)
        status = 'private' if is_private else 'public'
        logger.error('Private session mode changed: %s', status)
        spotify.session_instance.emit(
            SessionEvent.PRIVATE_SESSION_MODE_CHANGED,
            spotify.session_instance, is_private)
