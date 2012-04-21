import logging
import Queue

import spotify

logger = logging.getLogger('pyspotify.manager.session')

class SpotifySessionManager(object):
    """
    Client for Spotify. Inherit from this class to have your callbacks
    called on the appropriate events.

    Exceptions raised in your callback handlers will be displayed on the
    standard error output (stderr).

    When logging in a user, the application can pass one of:
        - `username` + `password`: standard login using a plaintext password
        - nothing: logs in the last user which credentials have been stored
          using `remember_me`.
        - `username` + `login_blob`: the blob is encrypted data from
          *libspotify*, for when a multi-user application wants to use
          the re-login feature. The blob is obtained from the
          :meth:`credentials_blob_updated` callback after a successful
          login to the Spotify AP.
    """

    api_version = spotify.api_version
    cache_location = 'tmp'
    settings_location = 'tmp'
    application_key = None
    appkey_file = 'spotify_appkey.key'
    user_agent = 'pyspotify-example'

    def __init__(self, username=None, password=None, remember_me=False,
                 login_blob=''):
        self._cmdqueue = Queue.Queue()
        self.username = username
        self.password = password
        self.remember_me = remember_me
        self.login_blob = login_blob
        if self.application_key is None:
            self.application_key = open(self.appkey_file).read()

    def connect(self):
        """
        Connect to the Spotify API using the given username and password.

        This method calls the :func:`spotify.connect` function.

        This method does not return before we disconnect from the Spotify
        service.
        """
        session = spotify.connect(self)
        self.loop(session) # returns on disconnect

    def loop(self, session):
        """
        The main loop.

        Processes events from ``libspotify`` and turns some of them into
        callback calls.
        """
        running = True
        timeout = 0
        while running:
            try:
                message = self._cmdqueue.get(timeout=timeout)
                if message.get('command') == 'music_delivery':
                    num_frames = self.music_delivery_safe(
                        session, *message['args'])
                    message['reply_to'].put(num_frames)
                elif message.get('command') == 'process_events':
                    logger.debug('Got message; processing events')
                    timeout = session.process_events() / 1000.0
                    logger.debug('Will wait %.3fs for next message', timeout)
                elif message.get('command') == 'disconnect':
                    logger.debug('Got message; disconnecting')
                    session.logout()
                    running = False
                else:
                    raise ValueError('Unknown message type')
            except Queue.Empty:
                logger.debug(
                    'No message received before timeout. Processing events')
                timeout = session.process_events() / 1000.0
                logger.debug('Will wait %.3fs for next message', timeout)

    def disconnect(self):
        """
        Terminate the current Spotify session.
        """
        self._cmdqueue.put({'command': 'disconnect'})

    def logged_in(self, session, error):
        """
        Callback.

        Called when the login completes. You almost
        certainly want to do something with
        :meth:`session.playlist_container() <spotify.Session.playlist_container>`
        if the login succeded.

        :param session: the current session.
        :type session: :class:`spotify.Session`
        :param error: an error message, :class:`None` if all went well.
        :type error: string or :class:`None`
        """
        pass

    def logged_out(self, session):
        """
        Callback.

        The user has or has been logged out from Spotify.

        :param session: the current session.
        :type session: :class:`spotify.Session`
        """
        pass

    def metadata_updated(self, session):
        """
        Callback.

        The current user's metadata has been updated.

        :param session: the current session.
        :type session: :class:`spotify.Session`
        """
        pass

    def connection_error(self, session, error):
        """
        Callback.

        A connection error occured in ``libspotify``.

        :param session: the current session.
        :type session: :class:`spotify.Session`
        :param error: an error message. If :class:`None`, the connection is
          back.
        :type error: string or :class:`None`
        """
        pass

    def message_to_user(self, session, message):
        """
        Callback.

        An informative message from ``libspotify``, destinated to the user.

        :param session: the current session.
        :type session: :class:`spotify.Session`
        :param message: a message.
        :type message: string
        """
        pass

    def notify_main_thread(self, session=None):
        """
        Callback.

        When this method is called by ``libspotify``, one should call
        :meth:`session.process_events() <spotify.Session.process_events>`.

        If you use the :class:`SessionManager`'s default loop, the default
        implementation of this method does the job. Though, if you implement
        your own loop for handling Spotify events, you'll need to override this
        method.

        .. warning::
            This method is called from an internal thread in libspotify. You
            should make sure *not* to use the Spotify API from within it, as
            libspotify isn't thread safe.

        :param session: the current session.
        :type session: :class:`spotify.Session`
        """
        self._cmdqueue.put({'command': 'process_events'})

    def music_delivery(self, session, frames, frame_size, num_frames,
            sample_type, sample_rate, channels):
        """
        Callback.

        Called whenever new music data arrives from Spotify.

        You should override this method *or* :meth:`music_delivery_safe`, not both.

        .. warning::
            This method is called from an internal thread in libspotify. You
            should make sure *not* to use the Spotify API from within it, as
            libspotify isn't thread safe.

        :param session: the current session
        :type session: :class:`spotify.Session`
        :param frames: the audio data
        :type frames: :class:`buffer`
        :param frame_size: bytes per frame
        :type frame_size: :class:`int`
        :param num_frames: number of frames in this delivery
        :type num_frames: :class:`int`
        :param sample_type: currently this is always 0 which means 16-bit
            signed native endian integer samples
        :type sample_type: :class:`int`
        :param sample_rate: audio sample rate, in samples per second
        :type sample_rate: :class:`int`
        :param channels: number of audio channels. Currently 1 or 2
        :type channels: :class:`int`
        :return: number of frames consumed
        :rtype: :class:`int`
        """
        try:
            future = Queue.Queue()
            self._cmdqueue.put({
                'command': 'music_delivery',
                'args': (frames, frame_size, num_frames, sample_type, sample_rate,
                    channels),
                'reply_to': future,
            }, block=False)
            return future.get()
        except Queue.Full:
            return 0

    def music_delivery_safe(self, session, frames, frame_size, num_frames,
            sample_type, sample_rate, channels):
        """
        This method does the same as :meth:`music_delivery`, except that it's
        called from the :class:`SpotifySessionManager` loop. You can safely use
        Spotify APIs from within this method.

        You should override this method *or* :meth:`music_delivery`, not both.
        """
        return 0

    def play_token_lost(self, session):
        """
        Callback.

        The playback stopped because a track was played from another
        application, with the same account.

        :param session: the current session.
        :type session: :class:`spotify.Session`
        """
        pass

    def log_message(self, session, message):
        """
        Callback.

        A log message from ``libspotify``.

        :param session: the current session.
        :type session: :class:`spotify.Session`
        :param message: the message.
        :type message: string
        """
        pass

    def end_of_track(self, session):
        """
        Callback.

        Playback has reached the end of the current track.

        :param session: the current session.
        :type session: :class:`spotify.Session`
        """
        pass

    def credentials_blob_updated(self, session, blob):
        """
        Callback.

        Called when storable credentials have been updated, usually called when
        we have connected to the AP.

        .. warning::
            This method is called from an internal thread in libspotify. You
            should make sure *not* to use the Spotify API from within it, as
            libspotify isn't thread safe.

        :param session: the current session.
        :type session: :class:`spotify.Session`
        :param blob: a string which contains an encrypted token that can be
            stored safely on disk instead of storing plaintext passwords.
        """
        pass
