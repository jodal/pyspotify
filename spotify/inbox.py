from __future__ import unicode_literals

import spotify
from spotify import ffi, lib


__all__ = [
    'InboxPostResult',
]


class InboxPostResult(object):
    """The result object returned by :meth:`Session.inbox_post_tracks`."""

    def __init__(self, sp_inbox):
        lib.sp_inbox_add_ref(sp_inbox)
        self._sp_inbox = ffi.gc(sp_inbox, lib.sp_inbox_release)

    @property
    def error(self):
        """An :class:`ErrorType` associated with the inbox post result.

        Check to see if there was problems posting to the inbox.
        """
        return spotify.ErrorType(lib.sp_inbox_error(self._sp_inbox))
