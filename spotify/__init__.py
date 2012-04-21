__version__ = '1.7'

class SpotifyError(Exception):
    pass

# pylint: disable = W0404
def _add_null_handler_for_logging():
    import logging
    try:
        NullHandler = logging.NullHandler  # Python 2.7 and upwards
    except AttributeError:
        class NullHandler(logging.Handler):
            def emit(self, record):
                pass
    logging.getLogger('spotify').addHandler(NullHandler())

_add_null_handler_for_logging()
# pylint: enable = W0404

from spotify._spotify import Session
from spotify._spotify import Track
from spotify._spotify import Artist
from spotify._spotify import Album
from spotify._spotify import Link
from spotify._spotify import Results
from spotify._spotify import Playlist
from spotify._spotify import PlaylistContainer
from spotify._spotify import AlbumBrowser
from spotify._spotify import ArtistBrowser
from spotify._spotify import Image
from spotify._spotify import User
from spotify._spotify import ToplistBrowser

from spotify._spotify import api_version
from spotify._spotify import connect


