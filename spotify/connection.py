from __future__ import unicode_literals

import functools
import operator

import spotify
from spotify import lib, utils

__all__ = ["ConnectionRule", "ConnectionState", "ConnectionType"]


class Connection(object):

    """Connection controller.

    You'll never need to create an instance of this class yourself. You'll find
    it ready to use as the :attr:`~Session.connection` attribute on the
    :class:`Session` instance.
    """

    def __init__(self, session):
        self._session = session

        # The following defaults are based on the libspotify documentation
        self._connection_type = spotify.ConnectionType.UNKNOWN
        self._allow_network = True
        self._allow_network_if_roaming = False
        self._allow_sync_over_wifi = True
        self._allow_sync_over_mobile = False

    @property
    def state(self):
        """The session's current :class:`ConnectionState`.

        The connection state involves two components, authentication and
        offline mode. The mapping is as follows

        - :attr:`~ConnectionState.LOGGED_OUT`: not authenticated, offline
        - :attr:`~ConnectionState.OFFLINE`: authenticated, offline
        - :attr:`~ConnectionState.LOGGED_IN`: authenticated, online
        - :attr:`~ConnectionState.DISCONNECTED`: authenticated, offline, was
          previously online

        Register listeners for the
        :attr:`spotify.SessionEvent.CONNECTION_STATE_UPDATED` event to be
        notified when the connection state changes.
        """
        return spotify.ConnectionState(
            lib.sp_session_connectionstate(self._session._sp_session)
        )

    @property
    def type(self):
        """The session's :class:`ConnectionType`.

        Defaults to :attr:`ConnectionType.UNKNOWN`. Set to a
        :class:`ConnectionType` value to tell libspotify what type of
        connection you're using.

        This is used together with :attr:`~Connection.allow_network`,
        :attr:`~Connection.allow_network_if_roaming`,
        :attr:`~Connection.allow_sync_over_wifi`, and
        :attr:`~Connection.allow_sync_over_mobile` to control offline syncing
        and network usage.
        """
        return self._connection_type

    @type.setter
    def type(self, value):
        spotify.Error.maybe_raise(
            lib.sp_session_set_connection_type(self._session._sp_session, value)
        )
        self._connection_type = value

    @property
    def allow_network(self):
        """Whether or not network access is allowed at all.

        Defaults to :class:`True`. Setting this to :class:`False` turns on
        offline mode.
        """
        return self._allow_network

    @allow_network.setter
    def allow_network(self, value):
        self._allow_network = value
        self._update_connection_rules()

    @property
    def allow_network_if_roaming(self):
        """Whether or not network access is allowed if :attr:`~Connection.type`
        is set to :attr:`ConnectionType.MOBILE_ROAMING`.

        Defaults to :class:`False`.
        """
        return self._allow_network_if_roaming

    @allow_network_if_roaming.setter
    def allow_network_if_roaming(self, value):
        self._allow_network_if_roaming = value
        self._update_connection_rules()

    @property
    def allow_sync_over_wifi(self):
        """Whether or not offline syncing is allowed when
        :attr:`~Connection.type` is set to :attr:`ConnectionType.WIFI`.

        Defaults to :class:`True`.
        """
        return self._allow_sync_over_wifi

    @allow_sync_over_wifi.setter
    def allow_sync_over_wifi(self, value):
        self._allow_sync_over_wifi = value
        self._update_connection_rules()

    @property
    def allow_sync_over_mobile(self):
        """Whether or not offline syncing is allowed when
        :attr:`~Connection.type` is set to :attr:`ConnectionType.MOBILE`, or
        :attr:`allow_network_if_roaming` is :class:`True` and
        :attr:`~Connection.type` is set to
        :attr:`ConnectionType.MOBILE_ROAMING`.

        Defaults to :class:`True`.
        """
        return self._allow_sync_over_mobile

    @allow_sync_over_mobile.setter
    def allow_sync_over_mobile(self, value):
        self._allow_sync_over_mobile = value
        self._update_connection_rules()

    def _update_connection_rules(self):
        rules = []
        if self._allow_network:
            rules.append(spotify.ConnectionRule.NETWORK)
        if self._allow_network_if_roaming:
            rules.append(spotify.ConnectionRule.NETWORK_IF_ROAMING)
        if self._allow_sync_over_wifi:
            rules.append(spotify.ConnectionRule.ALLOW_SYNC_OVER_WIFI)
        if self._allow_sync_over_mobile:
            rules.append(spotify.ConnectionRule.ALLOW_SYNC_OVER_MOBILE)
        rules = functools.reduce(operator.or_, rules, 0)
        spotify.Error.maybe_raise(
            lib.sp_session_set_connection_rules(self._session._sp_session, rules)
        )


@utils.make_enum("SP_CONNECTION_RULE_")
class ConnectionRule(utils.IntEnum):
    pass


@utils.make_enum("SP_CONNECTION_STATE_")
class ConnectionState(utils.IntEnum):
    pass


@utils.make_enum("SP_CONNECTION_TYPE_")
class ConnectionType(utils.IntEnum):
    pass
