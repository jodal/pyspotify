__version__ = '1.4'

class SpotifyError(Exception):
    pass

from _spotify import Session
from _spotify import Track
from _spotify import Artist
from _spotify import Album
from _spotify import Link
from _spotify import Results
from _spotify import Playlist
from _spotify import PlaylistContainer
from _spotify import AlbumBrowser
from _spotify import ArtistBrowser
from _spotify import Image
from _spotify import User
from _spotify import ToplistBrowser

from _spotify import api_version
from _spotify import connect
