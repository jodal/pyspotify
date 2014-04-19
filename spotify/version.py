from __future__ import unicode_literals

from spotify import lib, utils


def get_libspotify_api_version():
    """Get the API compatibility level of the wrapped libspotify library.

    >>> import spotify
    >>> spotify.get_libspotify_api_version()
    12
    """
    return lib.SPOTIFY_API_VERSION


def get_libspotify_build_id():
    """Get the build ID of the wrapped libspotify library.

    >>> import spotify
    >>> spotify.get_libspotify_build_id()
    u'12.1.51.g86c92b43 Release Linux-x86_64 '
    """
    return utils.to_unicode(lib.sp_build_id())
