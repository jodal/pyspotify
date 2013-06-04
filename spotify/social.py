from __future__ import unicode_literals

from spotify.utils import IntEnum, make_enum


__all__ = [
    'ScrobblingState',
    'SocialProvider',
]


@make_enum('SP_SCROBBLING_STATE_')
class ScrobblingState(IntEnum):
    pass


@make_enum('SP_SOCIAL_PROVIDER_')
class SocialProvider(IntEnum):
    pass
