from __future__ import unicode_literals

import logging
import threading

import spotify
from spotify import ffi, lib, utils


__all__ = [
    'Album',
    'AlbumBrowser',
    'AlbumType',
]

logger = logging.getLogger(__name__)


class Album(object):
    """A Spotify album.

    You can get an album from a track or an artist, or you can create an
    :class:`Album` yourself from a Spotify URI::

        >>> album = spotify.Album('spotify:album:6wXDbHLesy6zWqQawAa91d')
        >>> album.load().name
        u'Forward / Return'
    """

    def __init__(self, uri=None, sp_album=None):
        assert uri or sp_album, 'uri or sp_album is required'
        if uri is not None:
            album = spotify.Link(uri).as_album()
            if album is None:
                raise ValueError(
                    'Failed to get album from Spotify URI: %r' % uri)
            sp_album = album._sp_album
        lib.sp_album_add_ref(sp_album)
        self._sp_album = ffi.gc(sp_album, lib.sp_album_release)

    def __repr__(self):
        return 'Album(%r)' % self.link.uri

    @property
    def is_loaded(self):
        """Whether the album's data is loaded."""
        return bool(lib.sp_album_is_loaded(self._sp_album))

    def load(self, timeout=None):
        """Block until the album's data is loaded.

        :param timeout: seconds before giving up and raising an exception
        :type timeout: float
        :returns: self
        """
        # TODO Need to send a browse request for the object to be populated
        # with data
        return utils.load(self, timeout=timeout)

    @property
    def is_available(self):
        """Whether the album is available in the current region.

        Will always return :class:`None` if the album isn't loaded.
        """
        if not self.is_loaded:
            return None
        return bool(lib.sp_album_is_available(self._sp_album))

    @property
    def artist(self):
        """The artist of the album.

        Will always return :class:`None` if the album isn't loaded.
        """
        sp_artist = lib.sp_album_artist(self._sp_album)
        return spotify.Artist(sp_artist=sp_artist) if sp_artist else None

    def cover(self, image_size=None):
        """The album's cover :class:`Image`.

        ``image_size`` is an :class:`ImageSize` value, by default
        :attr:`ImageSize.NORMAL`.

        Will always return :class:`None` if the album isn't loaded or the
        album has no cover.
        """
        if image_size is None:
            image_size = spotify.ImageSize.NORMAL
        cover_id = lib.sp_album_cover(self._sp_album, image_size)
        if cover_id == ffi.NULL:
            return None
        sp_image = lib.sp_image_create(
            spotify.session_instance._sp_session, cover_id)
        return spotify.Image(sp_image=sp_image, add_ref=False)

    def cover_link(self, image_size=None):
        """A :class:`Link` to the album's cover.

        ``image_size`` is an :class:`ImageSize` value, by default
        :attr:`ImageSize.NORMAL`.

        This is equivalent with ``album.cover.link``, except that this method
        does not need to create the album cover image object to create a link
        to it.
        """
        if image_size is not None:
            image_size = spotify.ImageSize.NORMAL
        return spotify.Link(sp_link=lib.sp_link_create_from_album_cover(
            self._sp_album, image_size))

    @property
    def name(self):
        """The album's name.

        Will always return :class:`None` if the album isn't loaded.
        """
        name = utils.to_unicode(lib.sp_album_name(self._sp_album))
        return name if name else None

    @property
    def year(self):
        """The album's release year.

        Will always return :class:`None` if the album isn't loaded.
        """
        if not self.is_loaded:
            return None
        return lib.sp_album_year(self._sp_album)

    @property
    def type(self):
        """The album's :class:`AlbumType`.

        Will always return :class:`None` if the album isn't loaded.
        """
        if not self.is_loaded:
            return None
        return AlbumType(lib.sp_album_type(self._sp_album))

    @property
    def link(self):
        """A :class:`Link` to the album."""
        return spotify.Link(
            sp_link=lib.sp_link_create_from_album(self._sp_album))

    def browse(self, callback=None):
        """Get an :class:`AlbumBrowser` for the album.

        If ``callback`` isn't :class:`None`, it is expected to be a callable
        that accepts a single argument, an :class:`AlbumBrowser` instance, when
        the browser is done loading.

        Can be created without the album being loaded.
        """
        return spotify.AlbumBrowser(album=self, callback=callback)


class AlbumBrowser(object):
    """An album browser for a Spotify album.

    You can get an album browser from any :class:`Album` instance by calling
    :meth:`Album.browse`::

        >>> album = spotify.Album('spotify:album:6wXDbHLesy6zWqQawAa91d')
        >>> browser = album.browse()
        >>> browser.load()
        >>> len(browser.tracks)
        7
    """

    def __init__(
            self, album=None, callback=None,
            sp_albumbrowse=None, add_ref=True):

        assert album or sp_albumbrowse, 'album or sp_albumbrowse is required'

        self.complete_event = threading.Event()
        self._callback_handles = set()

        if sp_albumbrowse is None:
            handle = ffi.new_handle((callback, self))
            # TODO Think through the life cycle of the handle object. Can it
            # happen that we GC the browser and handle object, and then later
            # the callback is called?
            self._callback_handles.add(handle)

            sp_albumbrowse = lib.sp_albumbrowse_create(
                spotify.session_instance._sp_session, album._sp_album,
                _albumbrowse_complete_callback, handle)
            add_ref = False

        if add_ref:
            lib.sp_albumbrowse_add_ref(sp_albumbrowse)
        self._sp_albumbrowse = ffi.gc(
            sp_albumbrowse, lib.sp_albumbrowse_release)

    complete_event = None
    """:class:`threading.Event` that is set when the album browser is loaded.
    """

    # TODO __repr__()
    # TODO is_loaded
    # TODO load()
    # TODO error
    # TODO backend_request_duration

    # TODO album
    # TODO artist
    # TODO copyrights collection
    # TODO tracks collection
    # TODO review


@ffi.callback('void(sp_albumbrowse *, void *)')
def _albumbrowse_complete_callback(sp_albumbrowse, handle):
    logger.debug('albumbrowse_complete_callback called')
    if handle is ffi.NULL:
        logger.warning(
            'albumbrowse_complete_callback called without userdata')
        return
    (callback, album_browser) = ffi.from_handle(handle)
    album_browser._callback_handles.remove(handle)
    album_browser.complete_event.set()
    if callback is not None:
        callback(album_browser)


@utils.make_enum('SP_ALBUMTYPE_')
class AlbumType(utils.IntEnum):
    pass
