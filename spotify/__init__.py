__version__ = '1.7'

class SpotifyError(Exception):
    pass

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
