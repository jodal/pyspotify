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
    toplist to create.

    ``region`` is either a :class:`ToplistRegion` instance, or a 2-letter ISO
    3166-1 country code as a unicode string, that specifies the geographical
    region to create a toplist for.

    If ``region`` is :attr:`ToplistRegion.USER` and ``canonical_username``
    isn't specified, the region of the current user will be used. If
    ``canonical_username`` is specified, the region of the specified user will
    be used instead.

    If ``callback`` isn't :class:`None`, it is expected to be a callable that
    accepts a single argument, a :class:`Toplist` instance, when the toplist
    request completes.

    Example::

        >>> toplist = spotify.Toplist(
        ...     type=spotify.ToplistType.TRACKS, region='US')
        >>> toplist.load()
        >>> len(toplist.tracks)
        100
        >>> len(toplist.artists)
        0
        >>> toplist.tracks[0]
        Track(u'spotify:track:2dLLR6qlu5UJ5gk0dKz0h3')
    """

    def __init__(
            self, type=None, region=None, canonical_username=None,
            callback=None, sp_toplistbrowse=None, add_ref=True):

        assert (type is not None and region is not None) or sp_toplistbrowse, \
            'type and region, or sp_toplistbrowse, is required'

        self.type = type
        self.region = region
        self.canonical_username = canonical_username

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
    """:class:`threading.Event` that is set when the toplist request is
    completed.
    """

    def __repr__(self):
        return 'Toplist(type=%r, region=%r, canonical_username=%r)' % (
            self.type, self.region, self.canonical_username)

    @property
    def is_loaded(self):
        """Whether the toplist's data is loaded yet."""
        return bool(lib.sp_toplistbrowse_is_loaded(self._sp_toplistbrowse))

    def load(self, timeout=None):
        """Block until the user's data is loaded.

        After ``timeout`` seconds with no results :exc:`~spotify.Timeout` is
        raised. If ``timeout`` is :class:`None` the default timeout is used.

        The method returns ``self`` to allow for chaining of calls.
        """
        return utils.load(self, timeout=timeout)

    @property
    def error(self):
        """An :class:`ErrorType` associated with the toplist.

        Check to see if there was problems creating the toplist.
        """
        return spotify.ErrorType(
            lib.sp_toplistbrowse_error(self._sp_toplistbrowse))

    @property
    def backend_request_duration(self):
        """The time in ms that was spent waiting for the Spotify backend to
        create the toplist.

        Returns ``-1`` if the request was served from local cache. Returns
        :class:`None` if the toplist isn't loaded yet.
        """
        if not self.is_loaded:
            return None
        return lib.sp_toplistbrowse_backend_request_duration(
            self._sp_toplistbrowse)

    @property
    def tracks(self):
        """The tracks in the toplist.

        Will always return an empty list if the toplist isn't loaded.
        """
        spotify.Error.maybe_raise(self.error)
        if not self.is_loaded:
            return []

        def get_track(sp_toplistbrowse, key):
            return spotify.Track(
                sp_track=lib.sp_toplistbrowse_track(sp_toplistbrowse, key))

        return utils.Sequence(
            sp_obj=self._sp_toplistbrowse,
            add_ref_func=lib.sp_toplistbrowse_add_ref,
            release_func=lib.sp_toplistbrowse_release,
            len_func=lib.sp_toplistbrowse_num_tracks,
            getitem_func=get_track)

    @property
    def albums(self):
        """The albums in the toplist.

        Will always return an empty list if the toplist isn't loaded.
        """
        spotify.Error.maybe_raise(self.error)
        if not self.is_loaded:
            return []

        def get_album(sp_toplistbrowse, key):
            return spotify.Album(
                sp_album=lib.sp_toplistbrowse_album(sp_toplistbrowse, key))

        return utils.Sequence(
            sp_obj=self._sp_toplistbrowse,
            add_ref_func=lib.sp_toplistbrowse_add_ref,
            release_func=lib.sp_toplistbrowse_release,
            len_func=lib.sp_toplistbrowse_num_albums,
            getitem_func=get_album)

    @property
    def artists(self):
        """The artists in the toplist.

        Will always return an empty list if the toplist isn't loaded.
        """
        spotify.Error.maybe_raise(self.error)
        if not self.is_loaded:
            return []

        def get_artist(sp_toplistbrowse, key):
            return spotify.Artist(
                sp_artist=lib.sp_toplistbrowse_artist(sp_toplistbrowse, key))

        return utils.Sequence(
            sp_obj=self._sp_toplistbrowse,
            add_ref_func=lib.sp_toplistbrowse_add_ref,
            release_func=lib.sp_toplistbrowse_release,
            len_func=lib.sp_toplistbrowse_num_artists,
            getitem_func=get_artist)


@ffi.callback('void(sp_toplistbrowse *, void *)')
def _toplistbrowse_complete_callback(sp_toplistbrowse, handle):
    logger.debug('toplistbrowse_complete_callback called')
    if handle == ffi.NULL:
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
