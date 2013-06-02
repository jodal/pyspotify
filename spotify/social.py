from __future__ import unicode_literals

from spotify.utils import enum


__all__ = [
    'ScrobblingState',
    'SocialProvider',
]


@enum('SP_SCROBBLING_STATE_')
class ScrobblingState(object):
    pass


@enum('SP_SOCIAL_PROVIDER_')
class SocialProvider(object):
    pass
