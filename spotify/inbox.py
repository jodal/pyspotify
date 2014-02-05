from __future__ import unicode_literals

import logging
import threading

import spotify
from spotify import ffi, lib, utils


__all__ = [
    'InboxPostResult',
]

logger = logging.getLogger(__name__)


class InboxPostResult(object):
    """The result object returned by :meth:`Session.inbox_post_tracks`."""

    def __init__(
            self, canonical_username=None, tracks=None, message='',
            callback=None, sp_inbox=None, add_ref=True):

        assert canonical_username and tracks or sp_inbox, \
            'canonical_username and tracks, or sp_inbox, is required'

        self.complete_event = threading.Event()
        self._callback_handles = set()

        if sp_inbox is None:
            canonical_username = ffi.new(
                'char[]', utils.to_bytes(canonical_username))

            if isinstance(tracks, spotify.Track):
                tracks = [tracks]

            message = ffi.new('char[]', utils.to_bytes(message))

            handle = ffi.new_handle((callback, self))
            # TODO Think through the life cycle of the handle object. Can it
            # happen that we GC the search and handle object, and then later
            # the callback is called?
            self._callback_handles.add(handle)

            sp_inbox = lib.sp_inbox_post_tracks(
                spotify.session_instance._sp_session, canonical_username,
                [t._sp_track for t in tracks], len(tracks),
                message, _inboxpost_complete_callback, handle)

            if sp_inbox == ffi.NULL:
                raise spotify.Error('Inbox post request failed to initialize')

        if add_ref:
            lib.sp_inbox_add_ref(sp_inbox)
        self._sp_inbox = ffi.gc(sp_inbox, lib.sp_inbox_release)

    complete_event = None
    """:class:`threading.Event` that is set when the inbox post is
    completed.
    """

    def __repr__(self):
        if not self.complete_event.is_set():
            return '<InboxPostResult: pending>'
        else:
            return '<InboxPostResult: %s>' % self.error._name

    @property
    def error(self):
        """An :class:`ErrorType` associated with the inbox post result.

        Check to see if there was problems posting to the inbox.
        """
        return spotify.ErrorType(lib.sp_inbox_error(self._sp_inbox))


@ffi.callback('void(sp_inbox *, void *)')
def _inboxpost_complete_callback(sp_inbox, handle):
    logger.debug('inboxpost_complete_callback called')
    if handle == ffi.NULL:
        logger.warning('inboxpost_complete_callback called without userdata')
        return
    (callback, inbox_post_result) = ffi.from_handle(handle)
    inbox_post_result._callback_handles.remove(handle)
    inbox_post_result.complete_event.set()
    if callback is not None:
        callback(inbox_post_result)
