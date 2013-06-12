from __future__ import unicode_literals

from spotify import utils


__all__ = [
    'ConnectionRule',
    'ConnectionState',
    'ConnectionType',
]


@utils.make_enum('SP_CONNECTION_RULE_')
class ConnectionRule(utils.IntEnum):
    pass


@utils.make_enum('SP_CONNECTION_STATE_')
class ConnectionState(utils.IntEnum):
    pass


@utils.make_enum('SP_CONNECTION_TYPE_')
class ConnectionType(utils.IntEnum):
    pass
