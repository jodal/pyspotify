from __future__ import unicode_literals

from spotify.utils import IntEnum, make_enum


__all__ = [
    'ConnectionRule',
    'ConnectionState',
    'ConnectionType',
]


@make_enum('SP_CONNECTION_RULE_')
class ConnectionRule(IntEnum):
    pass


@make_enum('SP_CONNECTION_STATE_')
class ConnectionState(IntEnum):
    pass


@make_enum('SP_CONNECTION_TYPE_')
class ConnectionType(IntEnum):
    pass
