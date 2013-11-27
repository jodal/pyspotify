from __future__ import unicode_literals

import logging
import threading

import spotify
from spotify import ffi, lib, utils


__all__ = [
    'Toplist',
    'ToplistRegion',
    'ToplistType',
]

logger = logging.getLogger(__name__)


class Toplist(object):
    """A Spotify toplist of artists, albums, or tracks that are the currently
    most popular worldwide or in a specific region.

    ``type`` is a :class:`ToplistType` instance that specifies the type of
    toplist to get.

    ``region`` is either a :class:`ToplistRegion` instance, or a 2-letter ISO
    3166-1 country code as a unicode string, that specified for what
    geographical region the toplist is for.

    If ``region`` is :attr:`ToplistRegion.USER` and ``canonical_username``
    isn't specified, the region of the current user will be used.

    If ``region`` is :attr:`ToplistRegion.USER` and ``canonical_username``
    is specified, the region of the specified user will be used.

    If ``callback`` isn't :class:`None`, it is expected to be a callable that
    accepts a single argument, a :class:`Toplist` instance, when the toplist
    request completes.
    """

    def __init__(
            self, type=None, region=None, canonical_username=None,
            callback=None, sp_toplistbrowse=None, add_ref=True):

        assert (type and region) or sp_toplistbrowse, \
            'type and region, or sp_toplistbrowse, is required'

        self.complete_event = threading.Event()
        self._callback_handles = set()

        if sp_toplistbrowse is None:
            if isinstance(region, ToplistRegion):
                region = int(region)
            else:
                region = utils.to_country_code(region)

            if canonical_username is not None:
                canonical_username = ffi.new(
                    'char[]', utils.to_bytes(canonical_username))
            else:
                canonical_username = ffi.NULL

            handle = ffi.new_handle((callback, self))
            # TODO Think through the life cycle of the handle object. Can it
            # happen that we GC the search and handle object, and then later
            # the callback is called?
            self._callback_handles.add(handle)

            sp_toplistbrowse = lib.sp_toplistbrowse_create(
                spotify.session_instance._sp_session,
                int(type), region, canonical_username,
                _toplistbrowse_complete_callback, handle)
            add_ref = False

        if add_ref:
            lib.sp_toplistbrowse_add_ref(sp_toplistbrowse)
        self._sp_toplistbrowse = ffi.gc(
            sp_toplistbrowse, lib.sp_toplistbrowse_release)

    complete_event = None
    """:class:`threading.Event` that is set when the inbox post is
    completed.
    """

    @property
    def is_loaded(self):
        """Whether the toplist's data is loaded yet."""
        return bool(lib.sp_toplistbrowse_is_loaded(self._sp_toplistbrowse))

    def load(self, timeout=None):
        """Block until the user's data is loaded.

        :param timeout: seconds before giving up and raising an exception
        :type timeout: float
        :returns: self
        """
        return utils.load(self, timeout=timeout)

    # TODO error
    # TODO artists collection
    # TODO albums collection
    # TODO tracks collection
    # TODO backend_request_duration


@ffi.callback('void(sp_toplistbrowse *, void *)')
def _toplistbrowse_complete_callback(sp_toplistbrowse, handle):
    logger.debug('toplistbrowse_complete_callback called')
    if handle is ffi.NULL:
        logger.warning(
            'toplistbrowse_complete_callback called without userdata')
        return
    (callback, toplist) = ffi.from_handle(handle)
    toplist._callback_handles.remove(handle)
    toplist.complete_event.set()
    if callback is not None:
        callback(toplist)


@utils.make_enum('SP_TOPLIST_REGION_')
class ToplistRegion(utils.IntEnum):
    pass


@utils.make_enum('SP_TOPLIST_TYPE_')
class ToplistType(utils.IntEnum):
    pass
