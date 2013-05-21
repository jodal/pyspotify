from __future__ import unicode_literals

from spotify import ffi, lib, Loadable
from spotify.utils import to_unicode


__all__ = [
    'User',
]


class User(Loadable):
    """A Spotify user."""

    def __init__(self, sp_user):
        lib.sp_user_add_ref(sp_user)
        self.sp_user = ffi.gc(sp_user, lib.sp_user_release)

    @property
    def canonical_name(self):
        """The user's canonical username."""
        return to_unicode(lib.sp_user_canonical_name(self.sp_user))

    @property
    def display_name(self):
        """The user's displayable username."""
        return to_unicode(lib.sp_user_display_name(self.sp_user))

    @property
    def is_loaded(self):
        """Whether the user's data is loaded yet."""
        return bool(lib.sp_user_is_loaded(self.sp_user))

    def as_link(self):
        """Make a :class:`Link` to the user."""
        from spotify.link import Link
        return Link(self)
