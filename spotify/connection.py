from __future__ import unicode_literals

from spotify.utils import enum


__all__ = [
    'ConnectionRule',
    'ConnectionState',
    'ConnectionType',
]


@enum('SP_CONNECTION_RULE_')
class ConnectionRule(object):
    pass


@enum('SP_CONNECTION_STATE_')
class ConnectionState(object):
    pass


@enum('SP_CONNECTION_TYPE_')
class ConnectionType(object):
    pass
