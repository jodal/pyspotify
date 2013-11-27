from __future__ import unicode_literals

from spotify import utils


__all__ = [
    'ToplistRegion',
    'ToplistType',
]


@utils.make_enum('SP_TOPLIST_REGION_')
class ToplistRegion(utils.IntEnum):
    pass


@utils.make_enum('SP_TOPLIST_TYPE_')
class ToplistType(utils.IntEnum):
    pass
