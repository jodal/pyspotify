from __future__ import unicode_literals

import logging
import threading

import spotify
from spotify import ffi, lib, serialized, utils

__all__ = ["Artist", "ArtistBrowser", "ArtistBrowserType"]

logger = logging.getLogger(__name__)


class Artist(object):

    """A Spotify artist.

    You can get artists from tracks and albums, or you can create an
    :class:`Artist` yourself from a Spotify URI::

        >>> session = spotify.Session()
        # ...
        >>> artist = session.get_artist(
        ...     'spotify:artist:22xRIphSN7IkPVbErICu7s')
        >>> artist.load().name
        u'Rob Dougan'
    """

    def __init__(self, session, uri=None, sp_artist=None, add_ref=True):
        assert uri or sp_artist, "uri or sp_artist is required"

        self._session = session

        if uri is not None:
            artist = spotify.Link(self._session, uri=uri).as_artist()
            if artist is None:
                raise ValueError("Failed to get artist from Spotify URI: %r" % uri)
            sp_artist = artist._sp_artist

        if add_ref:
            lib.sp_artist_add_ref(sp_artist)
        self._sp_artist = ffi.gc(sp_artist, lib.sp_artist_release)

    def __repr__(self):
        return "Artist(%r)" % self.link.uri

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._sp_artist == other._sp_artist
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self._sp_artist)

    @property
    @serialized
    def name(self):
        """The artist's name.

        Will always return :class:`None` if the artist isn't loaded.
        """
        name = utils.to_unicode(lib.sp_artist_name(self._sp_artist))
        return name if name else None

    @property
    def is_loaded(self):
        """Whether the artist's data is loaded."""
        return bool(lib.sp_artist_is_loaded(self._sp_artist))

    def load(self, timeout=None):
        """Block until the artist's data is loaded.

        After ``timeout`` seconds with no results :exc:`~spotify.Timeout` is
        raised. If ``timeout`` is :class:`None` the default timeout is used.

        The method returns ``self`` to allow for chaining of calls.
        """
        return utils.load(self._session, self, timeout=timeout)

    @serialized
    def portrait(self, image_size=None, callback=None):
        """The artist's portrait :class:`Image`.

        ``image_size`` is an :class:`ImageSize` value, by default
        :attr:`ImageSize.NORMAL`.

        If ``callback`` isn't :class:`None`, it is expected to be a callable
        that accepts a single argument, an :class:`Image` instance, when
        the image is done loading.

        Will always return :class:`None` if the artist isn't loaded or the
        artist has no portrait.
        """
        if image_size is None:
            image_size = spotify.ImageSize.NORMAL
        portrait_id = lib.sp_artist_portrait(self._sp_artist, int(image_size))
        if portrait_id == ffi.NULL:
            return None
        sp_image = lib.sp_image_create(self._session._sp_session, portrait_id)
        return spotify.Image(
            self._session, sp_image=sp_image, add_ref=False, callback=callback
        )

    def portrait_link(self, image_size=None):
        """A :class:`Link` to the artist's portrait.

        ``image_size`` is an :class:`ImageSize` value, by default
        :attr:`ImageSize.NORMAL`.

        This is equivalent with ``artist.portrait(image_size).link``, except
        that this method does not need to create the artist portrait image
        object to create a link to it.
        """
        if image_size is None:
            image_size = spotify.ImageSize.NORMAL
        sp_link = lib.sp_link_create_from_artist_portrait(
            self._sp_artist, int(image_size)
        )
        return spotify.Link(self._session, sp_link=sp_link, add_ref=False)

    @property
    def link(self):
        """A :class:`Link` to the artist."""
        sp_link = lib.sp_link_create_from_artist(self._sp_artist)
        return spotify.Link(self._session, sp_link=sp_link, add_ref=False)

    def browse(self, type=None, callback=None):
        """Get an :class:`ArtistBrowser` for the artist.

        If ``type`` is :class:`None`, it defaults to
        :attr:`ArtistBrowserType.FULL`.

        If ``callback`` isn't :class:`None`, it is expected to be a callable
        that accepts a single argument, an :class:`ArtistBrowser` instance,
        when the browser is done loading.

        Can be created without the artist being loaded.
        """
        return spotify.ArtistBrowser(
            self._session, artist=self, type=type, callback=callback
        )


class ArtistBrowser(object):

    """An artist browser for a Spotify artist.

    You can get an artist browser from any :class:`Artist` instance by calling
    :meth:`Artist.browse`::

        >>> session = spotify.Session()
        # ...
        >>> artist = session.get_artist(
        ...     'spotify:artist:421vyBBkhgRAOz4cYPvrZJ')
        >>> browser = artist.browse()
        >>> browser.load()
        >>> len(browser.albums)
        7
    """

    def __init__(
        self,
        session,
        artist=None,
        type=None,
        callback=None,
        sp_artistbrowse=None,
        add_ref=True,
    ):

        assert artist or sp_artistbrowse, "artist or sp_artistbrowse is required"

        self._session = session
        self.loaded_event = threading.Event()

        if sp_artistbrowse is None:
            if type is None:
                type = ArtistBrowserType.FULL

            handle = ffi.new_handle((self._session, self, callback))
            self._session._callback_handles.add(handle)

            sp_artistbrowse = lib.sp_artistbrowse_create(
                self._session._sp_session,
                artist._sp_artist,
                int(type),
                _artistbrowse_complete_callback,
                handle,
            )
            add_ref = False

        if add_ref:
            lib.sp_artistbrowse_add_ref(sp_artistbrowse)
        self._sp_artistbrowse = ffi.gc(sp_artistbrowse, lib.sp_artistbrowse_release)

    loaded_event = None
    """:class:`threading.Event` that is set when the artist browser is loaded.
    """

    def __repr__(self):
        if self.is_loaded:
            return "ArtistBrowser(%r)" % self.artist.link.uri
        else:
            return "ArtistBrowser(<not loaded>)"

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._sp_artistbrowse == other._sp_artistbrowse
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self._sp_artistbrowse)

    @property
    def is_loaded(self):
        """Whether the artist browser's data is loaded."""
        return bool(lib.sp_artistbrowse_is_loaded(self._sp_artistbrowse))

    def load(self, timeout=None):
        """Block until the artist browser's data is loaded.

        After ``timeout`` seconds with no results :exc:`~spotify.Timeout` is
        raised. If ``timeout`` is :class:`None` the default timeout is used.

        The method returns ``self`` to allow for chaining of calls.
        """
        return utils.load(self._session, self, timeout=timeout)

    @property
    def error(self):
        """An :class:`ErrorType` associated with the artist browser.

        Check to see if there was problems creating the artist browser.
        """
        return spotify.ErrorType(lib.sp_artistbrowse_error(self._sp_artistbrowse))

    @property
    def backend_request_duration(self):
        """The time in ms that was spent waiting for the Spotify backend to
        create the artist browser.

        Returns ``-1`` if the request was served from local cache. Returns
        :class:`None` if the artist browser isn't loaded yet.
        """
        if not self.is_loaded:
            return None
        return lib.sp_artistbrowse_backend_request_duration(self._sp_artistbrowse)

    @property
    @serialized
    def artist(self):
        """Get the :class:`Artist` the browser is for.

        Will always return :class:`None` if the artist browser isn't loaded.
        """
        sp_artist = lib.sp_artistbrowse_artist(self._sp_artistbrowse)
        if sp_artist == ffi.NULL:
            return None
        return Artist(self._session, sp_artist=sp_artist, add_ref=True)

    @serialized
    def portraits(self, callback=None):
        """The artist's portraits.

        Due to limitations in libspotify's API you can't specify the
        :class:`ImageSize` of these images.

        If ``callback`` isn't :class:`None`, it is expected to be a callable
        that accepts a single argument, an :class:`Image` instance, when
        the image is done loading. The callable will be called once for each
        portrait.

        Will always return an empty list if the artist browser isn't loaded.
        """
        if not self.is_loaded:
            return []

        @serialized
        def get_image(sp_artistbrowse, key):
            image_id = lib.sp_artistbrowse_portrait(sp_artistbrowse, key)
            sp_image = lib.sp_image_create(image_id)
            return spotify.Image(
                self._session,
                sp_image=sp_image,
                add_ref=False,
                callback=callback,
            )

        return utils.Sequence(
            sp_obj=self._sp_artistbrowse,
            add_ref_func=lib.sp_artistbrowse_add_ref,
            release_func=lib.sp_artistbrowse_release,
            len_func=lib.sp_artistbrowse_num_portraits,
            getitem_func=get_image,
        )

    @property
    @serialized
    def tracks(self):
        """The artist's tracks.

        Will be an empty list if the browser was created with a ``type`` of
        :attr:`ArtistBrowserType.NO_TRACKS` or
        :attr:`ArtistBrowserType.NO_ALBUMS`.

        Will always return an empty list if the artist browser isn't loaded.
        """
        if not self.is_loaded:
            return []

        @serialized
        def get_track(sp_artistbrowse, key):
            return spotify.Track(
                self._session,
                sp_track=lib.sp_artistbrowse_track(sp_artistbrowse, key),
                add_ref=True,
            )

        return utils.Sequence(
            sp_obj=self._sp_artistbrowse,
            add_ref_func=lib.sp_artistbrowse_add_ref,
            release_func=lib.sp_artistbrowse_release,
            len_func=lib.sp_artistbrowse_num_tracks,
            getitem_func=get_track,
        )

    @property
    @serialized
    def tophit_tracks(self):
        """The artist's top hit tracks.

        Will always return an empty list if the artist browser isn't loaded.
        """
        if not self.is_loaded:
            return []

        @serialized
        def get_track(sp_artistbrowse, key):
            return spotify.Track(
                self._session,
                sp_track=lib.sp_artistbrowse_tophit_track(sp_artistbrowse, key),
                add_ref=True,
            )

        return utils.Sequence(
            sp_obj=self._sp_artistbrowse,
            add_ref_func=lib.sp_artistbrowse_add_ref,
            release_func=lib.sp_artistbrowse_release,
            len_func=lib.sp_artistbrowse_num_tophit_tracks,
            getitem_func=get_track,
        )

    @property
    @serialized
    def albums(self):
        """The artist's albums.

        Will be an empty list if the browser was created with a ``type`` of
        :attr:`ArtistBrowserType.NO_ALBUMS`.

        Will always return an empty list if the artist browser isn't loaded.
        """
        if not self.is_loaded:
            return []

        @serialized
        def get_album(sp_artistbrowse, key):
            return spotify.Album(
                self._session,
                sp_album=lib.sp_artistbrowse_album(sp_artistbrowse, key),
                add_ref=True,
            )

        return utils.Sequence(
            sp_obj=self._sp_artistbrowse,
            add_ref_func=lib.sp_artistbrowse_add_ref,
            release_func=lib.sp_artistbrowse_release,
            len_func=lib.sp_artistbrowse_num_albums,
            getitem_func=get_album,
        )

    @property
    @serialized
    def similar_artists(self):
        """The artist's similar artists.

        Will always return an empty list if the artist browser isn't loaded.
        """
        if not self.is_loaded:
            return []

        @serialized
        def get_artist(sp_artistbrowse, key):
            return spotify.Artist(
                self._session,
                sp_artist=lib.sp_artistbrowse_similar_artist(sp_artistbrowse, key),
                add_ref=True,
            )

        return utils.Sequence(
            sp_obj=self._sp_artistbrowse,
            add_ref_func=lib.sp_artistbrowse_add_ref,
            release_func=lib.sp_artistbrowse_release,
            len_func=lib.sp_artistbrowse_num_similar_artists,
            getitem_func=get_artist,
        )

    @property
    @serialized
    def biography(self):
        """A biography of the artist.

        Will always return an empty string if the artist browser isn't loaded.
        """
        return utils.to_unicode(lib.sp_artistbrowse_biography(self._sp_artistbrowse))


@ffi.callback("void(sp_artistbrowse *, void *)")
@serialized
def _artistbrowse_complete_callback(sp_artistbrowse, handle):
    logger.debug("artistbrowse_complete_callback called")
    if handle == ffi.NULL:
        logger.warning(
            "pyspotify artistbrowse_complete_callback called without userdata"
        )
        return
    (session, artist_browser, callback) = ffi.from_handle(handle)
    session._callback_handles.remove(handle)
    artist_browser.loaded_event.set()
    if callback is not None:
        callback(artist_browser)


@utils.make_enum("SP_ARTISTBROWSE_")
class ArtistBrowserType(utils.IntEnum):
    pass
