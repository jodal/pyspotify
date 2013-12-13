from __future__ import unicode_literals

import spotify
from spotify import ffi, lib, utils


__all__ = [
    'Artist',
    'ArtistBrowserType',
]


class Artist(object):
    """A Spotify artist.

    You can get artists from tracks and albums, or you can create an
    :class:`Artist` yourself from a Spotify URI::

        >>> artist = spotify.Artist('spotify:artist:22xRIphSN7IkPVbErICu7s')
        >>> artist.load().name
        u'Rob Dougan'
    """

    def __init__(self, uri=None, sp_artist=None):
        assert uri or sp_artist, 'uri or sp_artist is required'
        if uri is not None:
            artist = spotify.Link(uri).as_artist()
            if artist is None:
                raise ValueError(
                    'Failed to get artist from Spotify URI: %r' % uri)
            sp_artist = artist._sp_artist
        lib.sp_artist_add_ref(sp_artist)
        self._sp_artist = ffi.gc(sp_artist, lib.sp_artist_release)

    def __repr__(self):
        return 'Artist(%r)' % self.link.uri

    @property
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

        :param timeout: seconds before giving up and raising an exception
        :type timeout: float
        :returns: self
        """
        # TODO Need to send a browse request for the object to be populated
        # with data
        return utils.load(self, timeout=timeout)

    def portrait(self, image_size=None):
        """The artist's portrait :class:`Image`.

        ``image_size`` is an :class:`ImageSize` value, by default
        :attr:`ImageSize.NORMAL`.

        Will always return :class:`None` if the artist isn't loaded or the
        artist has no portrait.
        """
        if image_size is None:
            image_size = spotify.ImageSize.NORMAL
        portrait_id = lib.sp_artist_portrait(self._sp_artist, image_size)
        if portrait_id == ffi.NULL:
            return None
        sp_image = lib.sp_image_create(
            spotify.session_instance._sp_session, portrait_id)
        return spotify.Image(sp_image=sp_image, add_ref=False)

    def portrait_link(self, image_size=None):
        """A :class:`Link` to the artist's portrait.

        ``image_size`` is an :class:`ImageSize` value, by default
        :attr:`ImageSize.NORMAL`.

        This is equivalent with ``artist.portrait.link``, except that this
        method does not need to create the artist portrait image object to
        create a link to it.
        """
        if image_size is None:
            image_size = spotify.ImageSize.NORMAL
        return spotify.Link(sp_link=lib.sp_link_create_from_artist_portrait(
            self._sp_artist, image_size))

    @property
    def link(self):
        """A :class:`Link` to the artist."""
        return spotify.Link(
            sp_link=lib.sp_link_create_from_artist(self._sp_artist))


@utils.make_enum('SP_ARTISTBROWSE_')
class ArtistBrowserType(utils.IntEnum):
    pass
