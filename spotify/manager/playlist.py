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
