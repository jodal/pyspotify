from __future__ import unicode_literals

import spotify
from spotify import ffi, lib
from spotify.utils import enum, get_with_growing_buffer, to_bytes


__all__ = [
    'Link',
]


@enum('SP_LINK')
class Link(object):
    def __init__(self, value):
        if spotify.session_instance is None:
            raise RuntimeError('Session must be initialized to create links')

        sp_link = lib.sp_link_create_from_string(
            ffi.new('char[]', to_bytes(value)))

        if sp_link == ffi.NULL:
            raise ValueError('Failed to get link from Spotify URI: %s' % value)

        self.sp_link = ffi.gc(sp_link, lib.sp_link_release)

    def __str__(self):
        return get_with_growing_buffer(lib.sp_link_as_string, self.sp_link)

    @property
    def type(self):
        return lib.sp_link_type(self.sp_link)
