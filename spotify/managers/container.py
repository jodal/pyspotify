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

class SpotifyContainerManager:
    """
    Handles Spotify playlist container callbacks. To implement you own callbacks,
    inherit from this class.
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
        container.add_playlist_removed_callback(self.playlist_removed, userdata)

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

######## CALLBACKS ########

    def container_loaded(container, userdata):
        """
        Callback

        :param container:   a playlist container
        :type container:    :class:`spotify.PlaylistContainer`

        This callback is called when the container has finished loading. This
        event happens after a successful login, or after a modification on the
        container (after the 3 callbacks described below).
        """
        pass

    def playlist_added(container, playlist, position, userdata):
        """
        Callback

        :param container:   a playlist container
        :type container:    :class:`spotify.PlaylistContainer`
        :param playlist:    playlist added to the container
        :type playlist:     :class:`spotify.Playlist`
        :param position:    new position of the playlist
        :type position:     :class:`int`

        Called when a new playlist is added to the container.
        """
        pass

    def playlist_moved(container, playlist, position, new_position,  userdata):
        """
        Callback

        :param container:   a playlist container
        :type container:    :class:`spotify.PlaylistContainer`
        :param playlist:    playlist moved
        :type playlist:     :class:`spotify.Playlist`
        :param position:    old position
        :type position:     :class:`int`
        :param new_position:
        :type new_position: :class:`int`

        Called when a playlist is moved in the container.
        """
        pass

    def playlist_removed(container, playlist, position, userdata):
        """
        Callback

        :param container:   a playlist container
        :type container:    :class:`spotify.PlaylistContainer`
        :param playlist:    playlist removed
        :type playlist:     :class:`spotify.Playlist`
        :param position:    old position
        :type position:     :class:`int`

        Called when a playlist is removed from the container.
        """
        pass
