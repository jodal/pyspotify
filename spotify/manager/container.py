class SpotifyContainerManager:
    """
    Handles Spotify playlist container callbacks. To implement you own
    callbacks, inherit from this class.

    Exceptions raised in your callback handlers will be displayed on the
    standard error output (stderr).
    """

    def __init__(self):
        pass

    def watch(self, container, userdata=None):
        """
        Listen to modifications events on a container.
        """
        container.add_loaded_callback(self.container_loaded, userdata)
        container.add_playlist_added_callback(self.playlist_added, userdata)
        container.add_playlist_moved_callback(self.playlist_moved, userdata)
        container.add_playlist_removed_callback(self.playlist_removed,
                                                userdata)

    def unwatch(self, container, userdata=None):
        """
        Stop listenning to events on the container.
        """
        try:
            container.remove_callback(self.container_loaded, userdata)
            container.remove_callback(self.playlist_added, userdata)
            container.remove_callback(self.playlist_moved, userdata)
            container.remove_callback(self.playlist_removed, userdata)
        except:
            pass

### Callbacks

    def container_loaded(self, container, userdata):
        """
        Callback

        This callback is called when the container has finished loading. This
        event happens after a successful login, or after a modification on the
        container (after the 3 callbacks described below).

        :param container:   a playlist container
        :type container:    :class:`spotify.PlaylistContainer`
        """
        pass

    def playlist_added(self, container, playlist, position, userdata):
        """
        Callback

        Called when a new playlist is added to the container.

        :param container:   a playlist container
        :type container:    :class:`spotify.PlaylistContainer`
        :param playlist:    playlist added to the container
        :type playlist:     :class:`spotify.Playlist`
        :param position:    new position of the playlist
        :type position:     :class:`int`
        """
        pass

    def playlist_moved(self, container, playlist, position, new_position,
            userdata):
        """
        Callback

        Called when a playlist is moved in the container.

        :param container:   a playlist container
        :type container:    :class:`spotify.PlaylistContainer`
        :param playlist:    playlist moved
        :type playlist:     :class:`spotify.Playlist`
        :param position:    old position
        :type position:     :class:`int`
        :param new_position:
        :type new_position: :class:`int`
        """
        pass

    def playlist_removed(self, container, playlist, position, userdata):
        """
        Callback

        Called when a playlist is removed from the container.

        :param container:   a playlist container
        :type container:    :class:`spotify.PlaylistContainer`
        :param playlist:    playlist removed
        :type playlist:     :class:`spotify.Playlist`
        :param position:    old position
        :type position:     :class:`int`
        """
        pass
