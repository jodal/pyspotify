from __future__ import unicode_literals

import functools
import operator

import spotify
from spotify import lib, utils


__all__ = [
    'ConnectionRule',
    'ConnectionState',
    'ConnectionType',
]


class Connection(object):
    """Connection controller.

    You'll never need to create an instance of this class yourself. You'll find
    it ready to use as the :attr:`~Session.connection` attribute on the
    :class:`Session` instance.
    """

    def __init__(self, session):
        self._session = session

    @property
    def state(self):
        """The current :class:`ConnectionState`."""
        return spotify.ConnectionState(
            lib.sp_session_connectionstate(self._session._sp_session))

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


@utils.make_enum('SP_CONNECTION_RULE_')
class ConnectionRule(utils.IntEnum):
    pass


@utils.make_enum('SP_CONNECTION_STATE_')
class ConnectionState(utils.IntEnum):
    pass


@utils.make_enum('SP_CONNECTION_TYPE_')
class ConnectionType(utils.IntEnum):
    pass
