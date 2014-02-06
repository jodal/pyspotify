from __future__ import unicode_literals

import spotify
from spotify import lib, ffi, utils
from spotify.session import _SessionCallbacks

__all__ = [
    'Config',
]


class Config(object):
    """The session config.

    Create an instance and assign to its attributes to configure. Then use the
    config object to create a session::

        >>> config = spotify.Config()
        >>> config.user_agent = 'My awesome Spotify client'
        >>> # Etc ...
        >>> session = spotify.Session(config=config)
    """

    def __init__(self):
        self._sp_session_callbacks = _SessionCallbacks.get_struct()
        self._sp_session_config = ffi.new('sp_session_config *', {
            'callbacks': self._sp_session_callbacks,
        })

        # Defaults
        self.api_version = lib.SPOTIFY_API_VERSION
        self.cache_location = b'tmp'
        self.settings_location = b'tmp'
        self.user_agent = 'pyspotify %s' % spotify.__version__
        self.compress_playlists = False
        self.dont_save_metadata_for_playlists = False
        self.initially_unload_playlists = False

    @property
    def api_version(self):
        """The API version of the libspotify we're using.

        You should not need to change this. It defaults to the value provided
        by libspotify through :attr:`spotify.lib.SPOTIFY_API_VERSION`.
        """
        return self._sp_session_config.api_version

    @api_version.setter
    def api_version(self, value):
        self._sp_session_config.api_version = value

    @property
    def cache_location(self):
        """A location for libspotify to cache files.

        Defaults to ``tmp`` in the current working directory.

        Must be a bytestring. Cannot be shared with other Spotify apps. Can
        only be used by one session at the time. Optimally, you should use a
        lock file or similar to ensure this.
        """
        return utils.to_bytes_or_none(self._sp_session_config.cache_location)

    @cache_location.setter
    def cache_location(self, value):
        self._cache_location = utils.to_char_or_null(value)
        self._sp_session_config.cache_location = self._cache_location

    @property
    def settings_location(self):
        """A location for libspotify to save settings.

        Defaults to ``tmp`` in the current working directory.

        Must be a bytestring. Cannot be shared with other Spotify apps. Can
        only be used by one session at the time. Optimally, you should use a
        lock file or similar to ensure this.
        """
        return utils.to_bytes_or_none(
            self._sp_session_config.settings_location)

    @settings_location.setter
    def settings_location(self, value):
        self._settings_location = utils.to_char_or_null(value)
        self._sp_session_config.settings_location = self._settings_location

    @property
    def application_key(self):
        """Your libspotify application key.

        Must be a bytestring. Alternatively, you can set
        :attr:`application_key_filename`, and pyspotify will read the file and
        use it instead of :attr:`application_key`.
        """
        return utils.to_bytes_or_none(
            ffi.cast('char *', self._sp_session_config.application_key))

    @application_key.setter
    def application_key(self, value):
        if value is None:
            size = 0
        else:
            size = len(value)
        assert size in (0, 321), (
            'Invalid application key; expected 321 bytes, got %d bytes' % size)

        self._application_key = utils.to_char_or_null(value)
        self._sp_session_config.application_key = ffi.cast(
            'void *', self._application_key)
        self._sp_session_config.application_key_size = size

    def load_application_key_file(self, filename=b'spotify_appkey.key'):
        """Load your libspotify application key file.

        If called without arguments, it tries to read ``spotify_appkey.key``
        from the current working directory.

        This is an alternative to setting :attr:`application_key` yourself. The
        file must be a binary key file, not the C code key file that can be
        compiled into an application.
        """
        with open(filename, 'rb') as fh:
            self.application_key = fh.read()

    @property
    def user_agent(self):
        """A string with the name of your client.

        Defaults to ``pyspotify 2.x.y``.
        """
        return utils.to_unicode_or_none(self._sp_session_config.user_agent)

    @user_agent.setter
    def user_agent(self, value):
        self._user_agent = utils.to_char_or_null(value)
        self._sp_session_config.user_agent = self._user_agent

    @property
    def compress_playlists(self):
        """Compress local copy of playlists, reduces disk space usage.

        Defaults to :class:`False`.
        """
        return bool(self._sp_session_config.compress_playlists)

    @compress_playlists.setter
    def compress_playlists(self, value):
        self._sp_session_config.compress_playlists = bool(value)

    @property
    def dont_save_metadata_for_playlists(self):
        """Don't save metadata for local copies of playlists.

        Defaults to :class:`False`.

        Reduces disk space usage at the expense of needing to request metadata
        from Spotify backend when loading list.
        """
        return bool(self._sp_session_config.dont_save_metadata_for_playlists)

    @dont_save_metadata_for_playlists.setter
    def dont_save_metadata_for_playlists(self, value):
        self._sp_session_config.dont_save_metadata_for_playlists = bool(value)

    @property
    def initially_unload_playlists(self):
        """Avoid loading playlists into RAM on startup.

        Defaults to :class:`False`.

        See :meth:`Playlist.in_ram` for more details.
        """
        return bool(self._sp_session_config.initially_unload_playlists)

    @initially_unload_playlists.setter
    def initially_unload_playlists(self, value):
        self._sp_session_config.initially_unload_playlists = bool(value)

    @property
    def device_id(self):
        """Device ID for offline synchronization and logging purposes.

        Defaults to :class:`None`.

        The Device ID must be unique to the particular device instance, i.e. no
        two units must supply the same Device ID. The Device ID must not change
        between sessions or power cycles. Good examples is the device's MAC
        address or unique serial number.
        """
        return utils.to_unicode_or_none(self._sp_session_config.device_id)

    @device_id.setter
    def device_id(self, value):
        self._device_id = utils.to_char_or_null(value)
        self._sp_session_config.device_id = self._device_id

    @property
    def proxy(self):
        """URL to the proxy server that should be used.

        Defaults to :class:`None`.

        The format is protocol://host:port where protocol is
        http/https/socks4/socks5.
        """
        return utils.to_unicode_or_none(self._sp_session_config.proxy)

    @proxy.setter
    def proxy(self, value):
        self._proxy = utils.to_char_or_null(value)
        self._sp_session_config.proxy = self._proxy

    @property
    def proxy_username(self):
        """Username to authenticate with proxy server.

        Defaults to :class:`None`.
        """
        return utils.to_unicode_or_none(self._sp_session_config.proxy_username)

    @proxy_username.setter
    def proxy_username(self, value):
        self._proxy_username = utils.to_char_or_null(value)
        self._sp_session_config.proxy_username = self._proxy_username

    @property
    def proxy_password(self):
        """Password to authenticate with proxy server.

        Defaults to :class:`None`.
        """
        return utils.to_unicode_or_none(self._sp_session_config.proxy_password)

    @proxy_password.setter
    def proxy_password(self, value):
        self._proxy_password = utils.to_char_or_null(value)
        self._sp_session_config.proxy_password = self._proxy_password

    @property
    def ca_certs_filename(self):
        """Path to a file containing the root CA certificates that the peer
        should be verified with.

        Defaults to :class:`None`. Must be a bytestring otherwise.

        The file must be a concatenation of all certificates in PEM format.
        Provided with libspotify is a sample PEM file in the ``examples/``
        dir. It is recommended that the application export a similar file
        from the local certificate store.

        .. warning::
            libspotify 12.1.51 for OS X does not have this field. Thus,
            this field is currently a no-op in pyspotify so that the same
            code can run on both Linux and OS X.
        """
        # XXX Waiting for ca_certs_filename on OS X
        #return utils.to_bytes_or_none(
        #    self._sp_session_config.ca_certs_filename)
        pass

    @ca_certs_filename.setter
    def ca_certs_filename(self, value):
        # XXX Waiting for ca_certs_filename on OS X
        #self._ca_certs_filename = utils.to_char_or_null(value)
        #self._sp_session_config.ca_certs_filename = self._ca_certs_filename
        pass

    @property
    def tracefile(self):
        """Path to API trace file.

        Defaults to :class:`None`. Must be a bytestring otherwise.
        """
        return utils.to_bytes_or_none(self._sp_session_config.tracefile)

    @tracefile.setter
    def tracefile(self, value):
        self._tracefile = utils.to_char_or_null(value)
        self._sp_session_config.tracefile = self._tracefile
