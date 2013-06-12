from __future__ import unicode_literals

from spotify import utils


__all__ = [
    'ScrobblingState',
    'SocialProvider',
]


@utils.make_enum('SP_SCROBBLING_STATE_')
class ScrobblingState(utils.IntEnum):
    pass


@utils.make_enum('SP_SOCIAL_PROVIDER_')
class SocialProvider(utils.IntEnum):
    pass
