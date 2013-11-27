from __future__ import unicode_literals

from spotify import utils


__all__ = [
    'ToplistType',
]


@utils.make_enum('SP_TOPLIST_TYPE_')
class ToplistType(utils.IntEnum):
    pass
