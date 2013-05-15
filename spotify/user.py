from __future__ import unicode_literals

from spotify import ffi, lib
from spotify.utils import to_unicode


__all__ = [
    'User',
]


class User(object):
    def __init__(self, sp_user):
        lib.sp_user_add_ref(sp_user)
        self.sp_user = ffi.gc(sp_user, lib.sp_user_release)

    @property
    def canonical_name(self):
        return to_unicode(lib.sp_user_canonical_name(self.sp_user))

    @property
    def display_name(self):
        return to_unicode(lib.sp_user_display_name(self.sp_user))

    @property
    def is_loaded(self):
        return bool(lib.sp_user_is_loaded(self.sp_user))

    @property
    def link(self):
        from spotify.link import Link
        return Link(self)
