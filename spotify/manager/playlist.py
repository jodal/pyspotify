class SpotifyPlaylistManager:
    """
    Handles Spotify playlists callbacks. To implement you own callbacks,
    inherit from this class.

    Exceptions raised in your callback handlers will be displayed on the
    standard error output (stderr).
    """

    def __init__(self):
        pass

    def watch(self, playlist, userdata=None):
        """
        Listen to modifications events on a playlist.
        """
        playlist.add_tracks_added_callback(self.tracks_added, userdata)
        playlist.add_tracks_moved_callback(self.tracks_moved, userdata)
        playlist.add_tracks_removed_callback(self.tracks_removed, userdata)

    def unwatch(self, playlist, userdata=None):
        """
        Stop listening to events on the playlist.
        """
        try:
            playlist.remove_callback(self.tracks_added, userdata)
            playlist.remove_callback(self.tracks_moved, userdata)
            playlist.remove_callback(self.tracks_removed, userdata)
        except:
            pass

### Callbacks

    def tracks_added(self, playlist, tracks, position, userdata):
        """
        Callback

        Called when tracks are inserted in the playlist.

        :param playlist:    playlist on which the event occured
        :type playlist:     :class:`spotify.Playlist`
        :param tracks:      list of added tracks
        :type tracks:       list of :class:`spotify.Track`
        :param position:    position in which the tracks where inserted
        :type position:     :class:`int`
        """
        pass

    def tracks_moved(self, playlist, tracks, new_position, userdata):
        """
        Callback

        Called when tracks are moved in the playlist.

        :param playlist:    playlist on which the event occured
        :type playlist:     :class:`spotify.Playlist`
        :param tracks:      list of moved tracks
        :type tracks:       list of :class:`spotify.Track`
        :param new_position: new position of the tracks
        :type new_position: :class:`int`
        """
        pass

    def tracks_removed(self, playlist, tracks, userdata):
        """
        Callback

        Called when tracks are removed from the playlist.

        :param playlist:    playlist on which the event occured
        :type playlist:     :class:`spotify.Playlist`
        :param tracks:      list of removed tracks
        :type tracks:       list of :class:`spotify.Track`
        """
        pass

    def playlist_renamed(self, playlist, userdata):
        """
        Callback

        Called when a playlist has been renamed.
        :meth:`spotify.Playlist.name()` can be used to find out the new name.

        :param playlist:    playlist on which the event occured
        :type playlist:     :class:`spotify.Playlist`
        """
        pass

    def playlist_state_changed(self, playlist, userdata):
        """
        Callback

        Called when state changed for a playlist.

        There are three states that trigger this callback:

        - Collaboration for this playlist has been turned on or off.
        - The playlist started having pending changes, or all pending changes
          have now been committed.
        - The playlist started loading, or finished loading.

        :param playlist:    playlist on which the event occured
        :type playlist:     :class:`spotify.Playlist`
        """
        pass

    def playlist_update_in_progress(self, playlist, done, userdata):
        """
        Callback

        Called when a playlist is updating or is done updating.

        This is called before and after a series of changes are applied to the
        playlist. It allows e.g. the user interface to defer updating until the
        entire operation is complete.

        :param playlist:    playlist on which the event occured
        :type playlist:     :class:`spotify.Playlist`
        :param done:        whether the update is finished
        :type done:         :class:`bool`
        """
        pass

    def playlist_metadata_updated(self, playlist, userdata):
        """
        Callback

        Called when metadata for one or more tracks in a playlist has been
        updated.

        :param playlist:    playlist on which the event occured
        :type playlist:     :class:`spotify.Playlist`
        """
        pass

    def track_created_changed(self, playlist, position, user, when, userdata):
        """
        Callback

        Called when create time and/or creator for a playlist entry changes.

        :param playlist:    playlist on which the event occured
        :type playlist:     :class:`spotify.Playlist`
        :param position:    track's position in the playlist
        :type position:     :class:`int`
        :param user:        creator of the playlist
        :type user:         :class:`spotify.User`
        :param when:        time in seconds since the UNIX Epoch
        :type when:         :class:`int`
        """
        pass

    def track_message_changed(self, playlist, position, message, userdata):
        """
        Callback

        Called when message attribute for a playlist entry changes.

        :param playlist:    playlist on which the event occured
        :type playlist:     :class:`spotify.Playlist`
        :param position:    track's position in the playlist
        :type position:     :class:`int`
        :param message:     new message
        :type message:      :class:`unicode`
        """
        pass

    def track_seen_changed(self, playlist, position, seen, userdata):
        """
        Callback

        Called when seen attribute for a playlist entry changes.

        :param playlist:    playlist on which the event occured
        :type playlist:     :class:`spotify.Playlist`
        :param position:    track's position in the playlist
        :type position:     :class:`int`
        :param seen:        new seen attribute
        :type seen:         :class:`bool`
        """
        pass

    def description_changed(self, playlist, description, userdata):
        """
        Callback

        Called when playlist description has changed.

        :param playlist:    playlist on which the event occured
        :type playlist:     :class:`spotify.Playlist`
        :param description: new description
        :type description:  :class:`unicode`
        """
        pass

    def subscribers_changed(self, playlist, userdata):
        """
        Callback

        Called when playlist subscribers changes (count or list of names).

        :param playlist:    playlist on which the event occured
        :type playlist:     :class:`spotify.Playlist`
        """
        pass

    def image_changed(self, playlist, image, userdata):
        """
        Callback

        Called when playlist image has changed.

        :param playlist:    playlist on which the event occured
        :type playlist:     :class:`spotify.Playlist`
        :param image:       image id of the new image
        :type image:        :class:`str`
        """
        pass
