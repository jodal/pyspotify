# -*- coding: utf-8 -*-
#
# Settings for session creation

class Settings:
    """
    This class stores settings used when creating a Spotify session.
    """

    application_key = None
    """
    Your application key (binary string).
    """

    cache_location = 'tmp'
    """
    The location where Spotify will write cache files. This cache include
    tracks, cached browse results and coverarts. Set to ``''`` to disable
    cache.
    """

    proxy = None
    """
    Url to the proxy server that should be used. The format is
    ``protocol://<host>:port`` (where protocol is http/https/socks4/socks5).
    """

    proxy_password = None
    """
    Password to authenticate with the proxy server.
    """

    proxy_username = None
    """
    Username to authenticate with proxy server.
    """

    settings_location = 'tmp'
    """
    The location where Spotify will write setting files and per-user cache
    items. This includes playlists, track metadata, etc. 'settings_location'
    may be the same path as 'cache_location'. 'settings_location' folder will
    not be created (unlike 'cache_location'), if you don't want to create the
    folder yourself, you can set 'settings_location' to 'cache_location'. 
    """

    user_agent = 'pyspotify-example'
    """
    "User-Agent" for your application - max 255 characters long. The User-Agent
    should be a relevant, customer facing identification of your application.
    """
