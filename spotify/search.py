from __future__ import unicode_literals

import spotify
from spotify import ffi, lib, utils


__all__ = [
    'Search',
]


class Search(object):
    """A Spotify search."""

    def __init__(self, sp_search):
        lib.sp_search_add_ref(sp_search)
        self._sp_search = ffi.gc(sp_search, lib.sp_search_release)

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

    @property
    def query(self):
        """The search query.

        Will always return :class:`None` if the search isn't loaded.
        """
        spotify.Error.maybe_raise(self.error)
        query = utils.to_unicode(lib.sp_search_query(self._sp_search))
        return query if query else None

    @property
    def link(self):
        """A :class:`Link` to the search."""
        from spotify.link import Link
        return Link(self)

    # TODO Add sp_search_* methods
