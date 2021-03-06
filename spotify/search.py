from __future__ import unicode_literals

import logging
import threading

import spotify
from spotify import ffi, lib, serialized, utils

__all__ = ["Search", "SearchPlaylist", "SearchType"]

logger = logging.getLogger(__name__)


class Search(object):

    """A Spotify search result.

    Call the :meth:`~Session.search` method on your :class:`Session` instance
    to do a search and get a :class:`Search` back.
    """

    def __init__(
        self,
        session,
        query="",
        callback=None,
        track_offset=0,
        track_count=20,
        album_offset=0,
        album_count=20,
        artist_offset=0,
        artist_count=20,
        playlist_offset=0,
        playlist_count=20,
        search_type=None,
        sp_search=None,
        add_ref=True,
    ):

        assert query or sp_search, "query or sp_search is required"

        self._session = session
        self.callback = callback
        self.track_offset = track_offset
        self.track_count = track_count
        self.album_offset = album_offset
        self.album_count = album_count
        self.artist_offset = artist_offset
        self.artist_count = artist_count
        self.playlist_offset = playlist_offset
        self.playlist_count = playlist_count
        if search_type is None:
            search_type = SearchType.STANDARD
        self.search_type = search_type

        self.loaded_event = threading.Event()

        if sp_search is None:
            handle = ffi.new_handle((self._session, self, callback))
            self._session._callback_handles.add(handle)

            sp_search = lib.sp_search_create(
                self._session._sp_session,
                utils.to_char(query),
                track_offset,
                track_count,
                album_offset,
                album_count,
                artist_offset,
                artist_count,
                playlist_offset,
                playlist_count,
                int(search_type),
                _search_complete_callback,
                handle,
            )
            add_ref = False

        if add_ref:
            lib.sp_search_add_ref(sp_search)
        self._sp_search = ffi.gc(sp_search, lib.sp_search_release)

    def __repr__(self):
        return "Search(%r)" % self.link.uri

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._sp_search == other._sp_search
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self._sp_search)

    loaded_event = None
    """:class:`threading.Event` that is set when the search is loaded."""

    @property
    def is_loaded(self):
        """Whether the search's data is loaded."""
        return bool(lib.sp_search_is_loaded(self._sp_search))

    @property
    def error(self):
        """An :class:`ErrorType` associated with the search.

        Check to see if there was problems loading the search.
        """
        return spotify.ErrorType(lib.sp_search_error(self._sp_search))

    def load(self, timeout=None):
        """Block until the search's data is loaded.

        After ``timeout`` seconds with no results :exc:`~spotify.Timeout` is
        raised. If ``timeout`` is :class:`None` the default timeout is used.

        The method returns ``self`` to allow for chaining of calls.
        """
        return utils.load(self._session, self, timeout=timeout)

    @property
    @serialized
    def query(self):
        """The search query.

        Will always return :class:`None` if the search isn't loaded.
        """
        spotify.Error.maybe_raise(self.error)
        query = utils.to_unicode(lib.sp_search_query(self._sp_search))
        return query if query else None

    @property
    @serialized
    def did_you_mean(self):
        """The search's "did you mean" query or :class:`None` if no such
        suggestion exists.

        Will always return :class:`None` if the search isn't loaded.
        """
        spotify.Error.maybe_raise(self.error)
        did_you_mean = utils.to_unicode(lib.sp_search_did_you_mean(self._sp_search))
        return did_you_mean if did_you_mean else None

    @property
    @serialized
    def tracks(self):
        """The tracks matching the search query.

        Will always return an empty list if the search isn't loaded.
        """
        spotify.Error.maybe_raise(self.error, ignores=[spotify.ErrorType.IS_LOADING])
        if not self.is_loaded:
            return []

        @serialized
        def get_track(sp_search, key):
            return spotify.Track(
                self._session,
                sp_track=lib.sp_search_track(sp_search, key),
                add_ref=True,
            )

        return utils.Sequence(
            sp_obj=self._sp_search,
            add_ref_func=lib.sp_search_add_ref,
            release_func=lib.sp_search_release,
            len_func=lib.sp_search_num_tracks,
            getitem_func=get_track,
        )

    @property
    def track_total(self):
        """The total number of tracks matching the search query.

        If the number is larger than the interval specified at search object
        creation, more search results are available. To fetch these, create a
        new search object with a new interval.
        """
        spotify.Error.maybe_raise(self.error)
        return lib.sp_search_total_tracks(self._sp_search)

    @property
    @serialized
    def albums(self):
        """The albums matching the search query.

        Will always return an empty list if the search isn't loaded.
        """
        spotify.Error.maybe_raise(self.error, ignores=[spotify.ErrorType.IS_LOADING])
        if not self.is_loaded:
            return []

        @serialized
        def get_album(sp_search, key):
            return spotify.Album(
                self._session,
                sp_album=lib.sp_search_album(sp_search, key),
                add_ref=True,
            )

        return utils.Sequence(
            sp_obj=self._sp_search,
            add_ref_func=lib.sp_search_add_ref,
            release_func=lib.sp_search_release,
            len_func=lib.sp_search_num_albums,
            getitem_func=get_album,
        )

    @property
    def album_total(self):
        """The total number of albums matching the search query.

        If the number is larger than the interval specified at search object
        creation, more search results are available. To fetch these, create a
        new search object with a new interval.
        """
        spotify.Error.maybe_raise(self.error)
        return lib.sp_search_total_albums(self._sp_search)

    @property
    @serialized
    def artists(self):
        """The artists matching the search query.

        Will always return an empty list if the search isn't loaded.
        """
        spotify.Error.maybe_raise(self.error, ignores=[spotify.ErrorType.IS_LOADING])
        if not self.is_loaded:
            return []

        @serialized
        def get_artist(sp_search, key):
            return spotify.Artist(
                self._session,
                sp_artist=lib.sp_search_artist(sp_search, key),
                add_ref=True,
            )

        return utils.Sequence(
            sp_obj=self._sp_search,
            add_ref_func=lib.sp_search_add_ref,
            release_func=lib.sp_search_release,
            len_func=lib.sp_search_num_artists,
            getitem_func=get_artist,
        )

    @property
    def artist_total(self):
        """The total number of artists matching the search query.

        If the number is larger than the interval specified at search object
        creation, more search results are available. To fetch these, create a
        new search object with a new interval.
        """
        spotify.Error.maybe_raise(self.error)
        return lib.sp_search_total_artists(self._sp_search)

    @property
    @serialized
    def playlists(self):
        """The playlists matching the search query as
        :class:`SearchPlaylist` objects containing the name, URI and
        image URI for matching playlists.

        Will always return an empty list if the search isn't loaded.
        """
        spotify.Error.maybe_raise(self.error, ignores=[spotify.ErrorType.IS_LOADING])
        if not self.is_loaded:
            return []

        @serialized
        def getitem(sp_search, key):
            return spotify.SearchPlaylist(
                self._session,
                name=utils.to_unicode(
                    lib.sp_search_playlist_name(self._sp_search, key)
                ),
                uri=utils.to_unicode(lib.sp_search_playlist_uri(self._sp_search, key)),
                image_uri=utils.to_unicode(
                    lib.sp_search_playlist_image_uri(self._sp_search, key)
                ),
            )

        return utils.Sequence(
            sp_obj=self._sp_search,
            add_ref_func=lib.sp_search_add_ref,
            release_func=lib.sp_search_release,
            len_func=lib.sp_search_num_playlists,
            getitem_func=getitem,
        )

    @property
    def playlist_total(self):
        """The total number of playlists matching the search query.

        If the number is larger than the interval specified at search object
        creation, more search results are available. To fetch these, create a
        new search object with a new interval.
        """
        spotify.Error.maybe_raise(self.error)
        return lib.sp_search_total_playlists(self._sp_search)

    def more(
        self,
        callback=None,
        track_count=None,
        album_count=None,
        artist_count=None,
        playlist_count=None,
    ):
        """Get the next page of search results for the same query.

        If called without arguments, the ``callback`` and ``*_count`` arguments
        from the original search is reused. If anything other than
        :class:`None` is specified, the value is used instead.
        """
        callback = callback or self.callback
        track_offset = self.track_offset + self.track_count
        track_count = track_count or self.track_count
        album_offset = self.album_offset + self.album_count
        album_count = album_count or self.album_count
        artist_offset = self.artist_offset + self.artist_count
        artist_count = artist_count or self.artist_count
        playlist_offset = self.playlist_offset + self.playlist_count
        playlist_count = playlist_count or self.playlist_count

        return Search(
            self._session,
            query=self.query,
            callback=callback,
            track_offset=track_offset,
            track_count=track_count,
            album_offset=album_offset,
            album_count=album_count,
            artist_offset=artist_offset,
            artist_count=artist_count,
            playlist_offset=playlist_offset,
            playlist_count=playlist_count,
            search_type=self.search_type,
        )

    @property
    def link(self):
        """A :class:`Link` to the search."""
        return spotify.Link(
            self._session,
            sp_link=lib.sp_link_create_from_search(self._sp_search),
            add_ref=False,
        )


@ffi.callback("void(sp_search *, void *)")
@serialized
def _search_complete_callback(sp_search, handle):
    logger.debug("search_complete_callback called")
    if handle == ffi.NULL:
        logger.warning("pyspotify search_complete_callback called without userdata")
        return
    (session, search_result, callback) = ffi.from_handle(handle)
    session._callback_handles.remove(handle)
    search_result.loaded_event.set()
    if callback is not None:
        callback(search_result)


class SearchPlaylist(object):

    """A playlist matching a search query."""

    name = None
    """The name of the playlist."""

    uri = None
    """The URI of the playlist."""

    image_uri = None
    """The URI of the playlist's image."""

    def __init__(self, session, name, uri, image_uri):
        self._session = session
        self.name = name
        self.uri = uri
        self.image_uri = image_uri

    def __repr__(self):
        return "SearchPlaylist(name=%r, uri=%r)" % (self.name, self.uri)

    @property
    def playlist(self):
        """The :class:`~spotify.Playlist` object for this
        :class:`SearchPlaylist`."""
        return self._session.get_playlist(self.uri)

    @property
    def image(self):
        """The :class:`~spotify.Image` object for this
        :class:`SearchPlaylist`."""
        return self._session.get_image(self.image_uri)


@utils.make_enum("SP_SEARCH_")
class SearchType(utils.IntEnum):
    pass
