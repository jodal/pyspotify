from __future__ import unicode_literals

import logging
import threading

import spotify
from spotify import ffi, lib, serialized, utils

__all__ = ["InboxPostResult"]

logger = logging.getLogger(__name__)


class InboxPostResult(object):

    """The result object returned by :meth:`Session.inbox_post_tracks`."""

    @serialized
    def __init__(
        self,
        session,
        canonical_username=None,
        tracks=None,
        message="",
        callback=None,
        sp_inbox=None,
        add_ref=True,
    ):

        assert (
            canonical_username and tracks or sp_inbox
        ), "canonical_username and tracks, or sp_inbox, is required"

        self._session = session
        self.loaded_event = threading.Event()

        if sp_inbox is None:
            canonical_username = utils.to_char(canonical_username)

            if isinstance(tracks, spotify.Track):
                tracks = [tracks]

            message = utils.to_char(message)

            handle = ffi.new_handle((self._session, self, callback))
            self._session._callback_handles.add(handle)

            sp_inbox = lib.sp_inbox_post_tracks(
                self._session._sp_session,
                canonical_username,
                [t._sp_track for t in tracks],
                len(tracks),
                message,
                _inboxpost_complete_callback,
                handle,
            )
            add_ref = True

            if sp_inbox == ffi.NULL:
                raise spotify.Error("Inbox post request failed to initialize")

        if add_ref:
            lib.sp_inbox_add_ref(sp_inbox)
        self._sp_inbox = ffi.gc(sp_inbox, lib.sp_inbox_release)

    loaded_event = None
    """:class:`threading.Event` that is set when the inbox post result is
    loaded.
    """

    def __repr__(self):
        if not self.loaded_event.is_set():
            return "InboxPostResult(<pending>)"
        else:
            return "InboxPostResult(%s)" % self.error._name

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._sp_inbox == other._sp_inbox
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self._sp_inbox)

    @property
    def error(self):
        """An :class:`ErrorType` associated with the inbox post result.

        Check to see if there was problems posting to the inbox.
        """
        return spotify.ErrorType(lib.sp_inbox_error(self._sp_inbox))


@ffi.callback("void(sp_inbox *, void *)")
@serialized
def _inboxpost_complete_callback(sp_inbox, handle):
    logger.debug("inboxpost_complete_callback called")
    if handle == ffi.NULL:
        logger.warning("pyspotify inboxpost_complete_callback called without userdata")
        return
    (session, inbox_post_result, callback) = ffi.from_handle(handle)
    session._callback_handles.remove(handle)
    inbox_post_result.loaded_event.set()
    if callback is not None:
        callback(inbox_post_result)
