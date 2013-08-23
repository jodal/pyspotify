from __future__ import unicode_literals

import collections
import threading

import spotify
from spotify import ffi, lib, utils


__all__ = [
    'SearchResult',
    'SearchResultPlaylist',
    'SearchType',
]


class SearchResult(object):
    """A Spotify search result.

    Call the :meth:`~Session.search` method on your :class:`Session` instance
    to do a search and get a :class:`SearchResult` back.
    """

    def __init__(self, sp_search, add_ref=True):
        if add_ref:
            lib.sp_search_add_ref(sp_search)
        self._sp_search = ffi.gc(sp_search, lib.sp_search_release)
        self.complete_event = threading.Event()

    complete_event = None
    """:class:`threading.Event` that is set when the search is completed."""

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

        :param timeout: seconds before giving up and raising an exception
        :type timeout: float
        :returns: self
        """
        # TODO Replace with self.complete_event.wait(timeout) when we have a
        # thread that takes care of all ``process_events()`` calls for us.
        return utils.load(self, timeout=timeout)

    @property
    def query(self):
        """The search query.

        Will always return :class:`None` if the search isn't loaded.
        """
        spotify.Error.maybe_raise(self.error)
        query = utils.to_unicode(lib.sp_search_query(self._sp_search))
        return query if query else None

    @property
    def did_you_mean(self):
        """The search's "did you mean" query or :class:`None` if no such
        suggestion exists.

        Will always return :class:`None` if the search isn't loaded.
        """
        spotify.Error.maybe_raise(self.error)
        did_you_mean = utils.to_unicode(
            lib.sp_search_did_you_mean(self._sp_search))
        return did_you_mean if did_you_mean else None

    @property
    def tracks(self):
        """The tracks matching the search query.

        Will always return an empty list if the search isn't loaded.
        """
        # TODO Replace with collections.Sequence subclass
        spotify.Error.maybe_raise(self.error)
        if not self.is_loaded:
            return []
        num_tracks = lib.sp_search_num_tracks(self._sp_search)
        tracks = []
        for i in range(num_tracks):
            tracks.append(spotify.Track(
                sp_track=lib.sp_search_track(self._sp_search, i)))
        return tracks

    @property
    def total_tracks(self):
        """The total number of tracks matching the search query.

        If the number is larger than the interval specified at search object
        creation, more search results are available. To fetch these, create a
        new search object with a new interval.
        """
        spotify.Error.maybe_raise(self.error)
        return lib.sp_search_total_tracks(self._sp_search)

    @property
    def albums(self):
        """The albums matching the search query.

        Will always return an empty list if the search isn't loaded.
        """
        # TODO Replace with collections.Sequence subclass
        spotify.Error.maybe_raise(self.error)
        if not self.is_loaded:
            return []
        num_albums = lib.sp_search_num_albums(self._sp_search)
        albums = []
        for i in range(num_albums):
            albums.append(spotify.Album(
                sp_album=lib.sp_search_album(self._sp_search, i)))
        return albums

    @property
    def total_albums(self):
        """The total number of albums matching the search query.

        If the number is larger than the interval specified at search object
        creation, more search results are available. To fetch these, create a
        new search object with a new interval.
        """
        spotify.Error.maybe_raise(self.error)
        return lib.sp_search_total_albums(self._sp_search)

    @property
    def artists(self):
        """The artists matching the search query.

        Will always return an empty list if the search isn't loaded.
        """
        # TODO Replace with collections.Sequence subclass
        spotify.Error.maybe_raise(self.error)
        if not self.is_loaded:
            return []
        num_artists = lib.sp_search_num_artists(self._sp_search)
        artists = []
        for i in range(num_artists):
            artists.append(spotify.Artist(
                sp_artist=lib.sp_search_artist(self._sp_search, i)))
        return artists

    @property
    def total_artists(self):
        """The total number of artists matching the search query.

        If the number is larger than the interval specified at search object
        creation, more search results are available. To fetch these, create a
        new search object with a new interval.
        """
        spotify.Error.maybe_raise(self.error)
        return lib.sp_search_total_artists(self._sp_search)

    @property
    def playlists(self):
        """The playlists matching the search query as
        :class:`SearchResultPlaylist` objects containing the name, URI and
        image URI for matching playlists.

        Will always return an empty list if the search isn't loaded.
        """
        # TODO Replace with collections.Sequence subclass
        spotify.Error.maybe_raise(self.error)
        if not self.is_loaded:
            return []
        num_playlists = lib.sp_search_num_playlists(self._sp_search)
        playlists = []
        for i in range(num_playlists):
            playlists.append(spotify.SearchResultPlaylist(
                name=utils.to_unicode(
                    lib.sp_search_playlist_name(self._sp_search, i)),
                uri=utils.to_unicode(
                    lib.sp_search_playlist_uri(self._sp_search, i)),
                image_uri=utils.to_unicode(
                    lib.sp_search_playlist_image_uri(self._sp_search, i)),
            ))
        return playlists

    @property
    def total_playlists(self):
        """The total number of playlists matching the search query.

        If the number is larger than the interval specified at search object
        creation, more search results are available. To fetch these, create a
        new search object with a new interval.
        """
        spotify.Error.maybe_raise(self.error)
        return lib.sp_search_total_playlists(self._sp_search)

    @property
    def link(self):
        """A :class:`Link` to the search."""
        return spotify.Link(self)

    # TODO Add more(count=None) method to search for the next "page" of search
    # results without having to manually manage the *_limit and *_count kwargs
    # and check the *_total counts.


class SearchResultPlaylist(collections.namedtuple(
        'SearchResultPlaylist', ['name', 'uri', 'image_uri'])):
    """A playlist matching a search query."""
    pass


@utils.make_enum('SP_SEARCH_')
class SearchType(utils.IntEnum):
    pass
