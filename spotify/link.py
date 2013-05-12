from __future__ import unicode_literals

import spotify
from spotify import ffi, lib
from spotify.utils import to_bytes, to_unicode


__all__ = [
    'Link',
]


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
        actual_length = 10
        buffer_length = actual_length
        while actual_length >= buffer_length:
            buffer_length = actual_length + 1
            link = ffi.new('char[%d]' % buffer_length)
            actual_length = lib.sp_link_as_string(
                self.sp_link, link, buffer_length)
        if actual_length == -1:
            return None
        return to_unicode(link)
