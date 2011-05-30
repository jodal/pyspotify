# Copyright 2011 Antoine Pierlot-Garcin
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

class SpotifyPlaylistManager:
    """
    Handles Spotify playlists callbacks. To implement you own callbacks,
    inherit from this class.
    """

    def __init__(self):
        pass

    def watch(self, playlist, userdata=None):
        """
        Listen to modifications events on a playlist.
        """
        playlist.add_tracks_added_callback(self.tracks_added, self, userdata)
        playlist.add_tracks_moved_callback(self.tracks_moved, self, userdata)
        playlist.add_tracks_removed_callback(self.tracks_removed, self,
                                                                    userdata)

    def unwatch(self, playlist, userdata=None):
        """
        Stop listenning to events on the playlist.
        """
        try:
            playlist.remove_callback(self.tracks_added, userdata)
            playlist.remove_callback(self.tracks_moved, userdata)
            playlist.remove_callback(self.tracks_removed, userdata)
        except:
            pass

######## CALLBACKS ########

    def tracks_added(self, playlist, tracks, position, userdata):
        """
        Callback

        :param playlist:    playlist on which the event occured
        :type playlist:     :class:`spotify.Playlist`
        :param tracks:      list of added tracks
        :type tracks:       :class:`spotify.Track`
        :param position:    position in which the tracks where inserted
        :type position:     :class:`int`

        Called when tracks are inserted in the playlist.
        """
        pass

    def tracks_moved(self, playlist, tracks, new_position, userdata):
        """
        Callback

        :param playlist:    playlist on which the event occured
        :type playlist:     :class:`spotify.Playlist`
        :param tracks:      list of moved tracks
        :type tracks:       :class:`spotify.Track`
        :param new_position: new position of the tracks
        :type new_position:     :class:`int`

        Called when tracks are moved in the playlist.
        """
        pass

    def tracks_removed(self, playlist, tracks, userdata):
        """
        Callback

        :param playlist:    playlist on which the event occured
        :type playlist:     :class:`spotify.Playlist`
        :param tracks:      list of removed tracks
        :type tracks:       :class:`spotify.Track`

        Called when tracks are removed from the playlist.
        """
        pass

    def playlist_renamed(self, playlist, userdata):
        """
        Callback

        :param playlist:    playlist on which the event occured
        :type playlist:     :class:`spotify.Playlist`

        Called when a playlist has been renamed.
        :meth:`spotify.Playlist.name()` can be used to find out the new name.
        """
        pass

    def playlist_state_changed(self, playlist, userdata):
        """
        Callback

        :param playlist:    playlist on which the event occured
        :type playlist:     :class:`spotify.Playlist`

        Called when state changed for a playlist.

        There are three states that trigger this callback:

            - Collaboration for this playlist has been turned on or off
            - The playlist started having pending changes, or all pending
                changes have now been committed
            - The playlist started loading, or finished loading
        """
        pass

    def playlist_update_in_progress(self, playlist, done, userdata):
        """
        Callback

        :param playlist:    playlist on which the event occured
        :type playlist:     :class:`spotify.Playlist`
        :param done:        wether the update is finished
        :type done:         :class:`bool`

        Called when a playlist is updating or is done updating.

        This is called before and after a series of changes are applied to the
        playlist. It allows e.g. the user interface to defer updating until the
        entire operation is complete.
        """
        pass

    def playlist_metadata_updated(self, playlist, userdata):
        """
        Callback

        :param playlist:    playlist on which the event occured
        :type playlist:     :class:`spotify.Playlist`

        Called when metadata for one or more tracks in a playlist has been
        updated.
        """
        pass

    def track_created_changed(self, playlist, position, user, when, userdata):
        """
        Callback

        :param playlist:    playlist on which the event occured
        :type playlist:     :class:`spotify.Playlist`
        :param position:    track's position in the playlist
        :type position:     :class:`int`
        :param user:        creator of the playlist
        :type user:         :class:`spotify.User`
        :param when:        time in seconds since the UNIX Epoch
        :type when:         :class:`int`

        Called when create time and/or creator for a playlist entry changes.
        """
        pass

    def track_message_changed(self, playlist, position, message, userdata):
        """
        Callback

        :param playlist:    playlist on which the event occured
        :type playlist:     :class:`spotify.Playlist`
        :param position:    track's position in the playlist
        :type position:     :class:`int`
        :param message:     new message
        :type message:      :class:`unicode`

        Called when message attribute for a playlist entry changes.
        """
        pass

    def track_seen_changed(self, playlist, position, seen, userdata):
        """
        Callback

        :param playlist:    playlist on which the event occured
        :type playlist:     :class:`spotify.Playlist`
        :param position:    track's position in the playlist
        :type position:     :class:`int`
        :param seen:        new seen attribute
        :type seen:         :class:`bool`

        Called when seen attribute for a playlist entry changes.
        """
        pass

    def description_changed(self, playlist, description, userdata):
        """
        Callback

        :param playlist:    playlist on which the event occured
        :type playlist:     :class:`spotify.Playlist`
        :param description: new description
        :type description:  :class:`unicode`

        Called when playlist description has changed.
        """
        pass

    def subscribers_changed(self, playlist, userdata):
        """
        Callback

        :param playlist:    playlist on which the event occured
        :type playlist:     :class:`spotify.Playlist`

        Called when playlist subscribers changes (count or list of names).
        """
        pass

    def image_changed(self, playlist, image, userdata):
        """
        Callback

        :param playlist:    playlist on which the event occured
        :type playlist:     :class:`spotify.Playlist`
        :param image:       image id of the new image
        :type image:        :class:`str`

        Called when playlist image has changed.
        """
        pass
