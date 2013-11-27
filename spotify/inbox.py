from __future__ import unicode_literals

import spotify
from spotify import ffi, lib, utils


__all__ = [
    'InboxPostResult',
]


class InboxPostResult(object):
    """The result object returned by :meth:`Session.inbox_post_tracks`."""

    def __init__(
            self, canonical_username=None, tracks=None, message='',
            callback=None, sp_inbox=None, add_ref=True):

        # TODO inboxpost_complete_cb callback

        assert canonical_username and tracks or sp_inbox, \
            'canonical_username and tracks, or sp_inbox, is required'

        if sp_inbox is None:
            if isinstance(tracks, spotify.Track):
                tracks = [tracks]

            sp_inbox = lib.sp_inbox_post_tracks(
                spotify.session_instance._sp_session,
                utils.to_bytes(canonical_username),
                [t._sp_track for t in tracks], len(tracks),
                utils.to_bytes(message), ffi.NULL, ffi.NULL)

            if sp_inbox == ffi.NULL:
                raise spotify.Error('Inbox post request failed to initialize')

        if add_ref:
            lib.sp_inbox_add_ref(sp_inbox)
        self._sp_inbox = ffi.gc(sp_inbox, lib.sp_inbox_release)

    @property
    def error(self):
        """An :class:`ErrorType` associated with the inbox post result.

        Check to see if there was problems posting to the inbox.
        """
        return spotify.ErrorType(lib.sp_inbox_error(self._sp_inbox))
