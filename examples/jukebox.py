#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import cmd
import logging
import threading
import time

from spotify import ArtistBrowser, Link, Album, Playlist, ToplistBrowser, \
    SpotifyError
from spotify.audiosink import import_audio_sink
from spotify.manager import (
    SpotifySessionManager, SpotifyPlaylistManager, SpotifyContainerManager)

selected_sink = ()
container_loaded = threading.Event()


class JukeboxUI(cmd.Cmd, threading.Thread):

    prompt = "jukebox> "

    def __init__(self, jukebox):
        cmd.Cmd.__init__(self)
        threading.Thread.__init__(self)
        self.jukebox = jukebox
        self.results = False

    def run(self):
        container_loaded.wait()
        container_loaded.clear()
        try:
            self.cmdloop()
        finally:
            self.do_quit(None)

    def validate_playlist(self, playlist):
        if playlist < 0 or playlist > len(self.jukebox.ctr):
            s = 'Invalid playlist, must be between 0 and {}'
            print(s.format(len(self.jukebox.ctr) + 1))
            return False
        else:
            return True

    def validate_track(self, playlist, track):
        if track < 0 or track > (len(self.jukebox.ctr[playlist]) - 1):
            s = 'Invalid track, must be between 0 and {}'
            print(s.format(len(self.jukebox.ctr[playlist])))
            return False
        else:
            return True

    def do_logout(self, line):
        """Logout and store username/password credentials"""
        self.jukebox.session.logout()

    def do_quit(self, line):
        """"Quit jukebox without saving credentials (use logout to
        save them)"""
        self.do_logout(None)
        self.jukebox.stop()
        self.jukebox.disconnect()
        print('Goodbye!')
        return True

    def do_list(self, line):
        """Usage: list [playlist]
        list  - List all playlists
        list [playlist]  - List tracks in playlist"""
        if not line:
            i = -1
            for i, p in enumerate(self.jukebox.ctr):
                if p.is_loaded():
                    if (isinstance(p, Playlist) and
                            Link.from_playlist(p).type() == Link.LINK_STARRED):
                        name = "Starred by {}".format(p.owner())
                        print('{:>3d} {:<20}'.format(i, name))
                    else:
                        name = p.name()
                        print('{:>3d} {:<20} ({} tracks)'.format(i, name,
                              len(p)))
                else:
                    print('{:>3d} loading...'.format(i))
            s = '{:>3d} Starred tracks       ({} tracks)'
            print(s.format(i + 1, len(self.jukebox.starred)))
        else:
            try:
                p = int(line)
            except ValueError:
                print('That is not a number!')
                return
            if not self.validate_playlist(p):
                return
            if p < len(self.jukebox.ctr):
                playlist = self.jukebox.ctr[p]
            else:
                playlist = self.jukebox.starred
            print('Listing playlist #{} ({})'.format(p, playlist.name()))
            for i, t in enumerate(playlist):
                if t.is_loaded():
                    s = '{:>3d} {} - {} [{}]'
                    print(s.format(i, t.artists()[0].name(), t.name(),
                          self.pretty_duration(t.duration())))
                else:
                    print('{:>3d} loading...'.format(i))

    def pretty_duration(self, milliseconds):
        seconds = milliseconds // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        duration = '{:02d}:{:02d}'.format(minutes, seconds)
        return duration

    def do_play(self, line):
        """Usage: play [track_link] | [playlist track] | [playlist]
        play  - Resume playback
        play [track_link]  - Play track_link
        play [playlist]  - Play all tracks from playlist
        play [playlist track]  - Play track from playlist"""
        if line:
            try:
                if line.startswith("spotify:"):
                    # spotify url
                    l = Link.from_string(line)
                    if not l.type() == Link.LINK_TRACK:
                        print('You can only play tracks!')
                        return
                    self.jukebox.load_track(l.as_track())
                else:
                    try:
                        playlist, track = map(int, line.split(' ', 1))
                        if (not self.validate_playlist(playlist) or
                                not self.validate_track(playlist, track)):
                            return

                        self.jukebox.load(playlist, track)
                    except ValueError:
                        try:
                            playlist = int(line)
                            if not self.validate_playlist(playlist):
                                return
                            self.jukebox.load_playlist(playlist)
                        except ValueError:
                            print('Usage: play [track_link] | '
                                  '[playlist track] | [playlist]')
                            return
            except SpotifyError as e:
                print('Unable to load track:', e)
                return
        self.jukebox.play()

    def do_browse(self, line):
        """Usage: browse spotify:<URI>  - browse album or artist URI"""
        if not line or not line.startswith("spotify:"):
            print('Usage: browse spotify:<URI>  - browse album or artist URI')
            return
        l = Link.from_string(line)
        if not l.type() in [Link.LINK_ALBUM, Link.LINK_ARTIST]:
            print('You can only browse albums and artists')
            return

        def browse_finished(browser, userdata):
            pass

        self.jukebox.browse(l, browse_finished)

    def print_search_results(self):
        print('Artists:')
        for a in self.results.artists():
            print('    {} {}'.format(Link.from_artist(a), a.name()))
        print('Albums:')
        for a in self.results.albums():
            print('    {} {}'.format(Link.from_album(a), a.name()))
        print('Tracks:')
        for a in self.results.tracks():
            print('    {} {}'.format(Link.from_track(a), a.name()))
        print(self.results.total_tracks() - len(self.results.tracks()),
              'Tracks not shown')

    def do_search(self, line):
        """Usage: search [needle]
        search  - print search status
        search [needle]  - search for needle"""
        if not line:
            if self.results is False:
                print('No search is in progress')
            elif self.results is None:
                print('Searching is in progress')
            else:
                self.print_search_results()
        else:
            line = line.decode('utf-8')
            self.results = None

            def search_finished(results, userdata):
                print('\nSearch results received')
                self.results = results
                self.print_search_results()

            self.jukebox.search(line, search_finished)

    def do_queue(self, line):
        """Usage: queue [playlist track]
        queue  - print queue
        queue clear  - clear queue
        queue [playlist track]  - queue 'track' from 'playlist' \
(both should be >=0)"""
        if not line:
            if self.jukebox._queue:
                for playlist, track in self.jukebox._queue:
                    print(playlist, track)
            else:
                print('Queue empty')
        else:
            if line == "clear":
                self.jukebox._queue = []
                print('Queue cleared')
            else:
                try:
                    playlist, track = map(int, line.split(' ', 1))
                    if (not self.validate_playlist(playlist) or
                            not self.validate_track(playlist, track)):
                        return
                    self.jukebox.queue(playlist, track)
                except ValueError:
                    print('Usage: queue playlist track')
                    return

    def do_stop(self, line):
        """Stop playback"""
        self.jukebox.stop()

    def do_pause(self, line):
        """Pause playback"""
        self.jukebox.pause()

    def do_next(self, line):
        """Next track in queue"""
        self.jukebox.next()

    def emptyline(self):
        pass

    def do_watch(self, line):
        """Usage: watch [playlist]  - enable notifications for tracks added,
        moved or removed from the playlist."""
        if not line:
            print("""Usage: watch [playlist]  - enable notifications for tracks
            added, moved or removed from the playlist.""")
        else:
            try:
                p = int(line)
            except ValueError:
                print('That is not a number!')
                return
            if not self.validate_playlist(p):
                return
            self.jukebox.watch(self.jukebox.ctr[p])

    def do_unwatch(self, line):
        """Usage: unwatch [playlist]  - disable notifications on playlist"""
        if not line:
            print('Usage: unwatch [playlist]')
        else:
            try:
                p = int(line)
            except ValueError:
                print('That is not a number!')
                return
            if not self.validate_playlist(p):
                return
            self.jukebox.watch(self.jukebox.ctr[p], True)

    def do_get_offline_status(self, line):
        """Usage: get_offline_status [playlist]"""
        if not line:
            print('Usage: get_offline_status [playlist]')
        else:
            try:
                p = int(line)
            except ValueError:
                print('That is not a number!')
                return
            if not self.validate_playlist(p):
                return
            self.jukebox.get_offline_status(self.jukebox.ctr[p])

    def do_set_offline_on(self, line):
        """Usage: set_offline_on [playlist]"""
        if not line:
            print('Usage: set_offline_on [playlist]')
        else:
            try:
                p = int(line)
            except ValueError:
                print('That is not a number!')
                return
            if not self.validate_playlist(p):
                return
            self.jukebox.set_offline_mode(self.jukebox.ctr[p], True)

    def do_set_offline_off(self, line):
        """Usage: set_offline_off [playlist]  - remove playlist from
        offline cache"""
        if not line:
            print("""Usage: set_offline_off [playlist]  - remove playlist
                from offline cache""")
        else:
            try:
                p = int(line)
            except ValueError:
                print('That is not a number!')
                return
            if not self.validate_playlist(p):
                return
            self.jukebox.set_offline_mode(self.jukebox.ctr[p], False)

    def do_get_offline_download_completed(self, line):
        """Usage: set_offline_off [playlist]"""
        if not line:
            print('Usage: set_offline_off [playlist]')
        else:
            try:
                p = int(line)
            except ValueError:
                print('That is not a number!')
                return
            if not self.validate_playlist(p):
                return
            self.jukebox.get_offline_download_completed(self.jukebox.ctr[p])

    def do_toplist(self, line):
        """Usage: toplist (albums|artists|tracks) (GB|FR|..|all|current)"""
        usage = """Usage: toplist (albums|artists|tracks) \
(GB|FR|..|all|current)"""
        if not line:
            print(usage)
        else:
            args = line.split(' ')
            if len(args) != 2:
                print(usage)
            else:
                self.jukebox.toplist(*args)

    def do_shell(self, line):
        """Drop into a python shell for debugging"""
        self.jukebox.shell()

    def do_add_new_playlist(self, line):
        """Usage: add_new_playlist <name>"""
        if not line:
            print('Usage: add_new_playlist <name>')
        else:
            self.jukebox.ctr.add_new_playlist(
                line.decode('utf-8'))

    def do_remove_playlist(self, line):
        """Usage: remove_playlist <index> [<count>]"""
        if not line:
            print('Usage: remove_playlist <index> [<count>]')
        else:
            c = 1
            try:
                args = line.split(' ')
                p = int(args[0])
                if len(args) > 1:
                    c = int(args[1])
            except ValueError:
                print('That is not a number!')
                return
            if not self.validate_playlist(p):
                return
            for i in range(p + c - 1, p - 1, -1):
                if self.jukebox.ctr[i].is_loaded():
                    print('Removing playlist #{}'.format(i))
                    self.jukebox.ctr.remove_playlist(i)
                    time.sleep(0.5)
                c = c-1

    def do_add_to_playlist(self, line):
        """Usage: add_to_playlist <playlist_index> <insert_point>
                <search_result_indecies>  - add search results to playlist"""
        usage = """Usage: add_to_playlist <playlist_index> <insert_point>
                <search_result_indecies>  - add search results to playlist"""
        if not line:
            print(usage)
            return
        args = line.split(' ')
        if len(args) < 3:
            print(usage)
        else:
            if not self.results:
                print('No search results')
            else:
                index = int(args.pop(0))
                insert = int(args.pop(0))
                tracks = self.results.tracks()
                for i in args:
                    for a in tracks[int(i)].artists():
                        print('{0}. {1} - {2} '.format(
                            i, a.name(), tracks[int(i)].name()))
                print('adding them to {0} '.format(
                    self.jukebox.ctr[index].name()))
                self.jukebox.ctr[index].add_tracks(
                    insert, [tracks[int(i)] for i in args])

    do_ls = do_list
    do_EOF = do_quit


class JukeboxPlaylistManager(SpotifyPlaylistManager):
    def tracks_added(self, p, t, i, u):
        print('Tracks added to playlist {}'.format(p.name()))

    def tracks_moved(self, p, t, i, u):
        print('Tracks moved in playlist {}'.format(p.name()))

    def tracks_removed(self, p, t, u):
        print('Tracks removed from playlist {}'.format(p.name()))

    def playlist_renamed(self, p, u):
        print('Playlist renamed to {}'.format(p.name()))


class JukeboxContainerManager(SpotifyContainerManager):
    def container_loaded(self, c, u):
        container_loaded.set()

    def playlist_added(self, c, p, i, u):
        print('Container: playlist "{}" added.'.format(p.name()))

    def playlist_moved(self, c, p, oi, ni, u):
        print('Container: playlist "{}" moved.'.format(p.name()))

    def playlist_removed(self, c, p, i, u):
        print('Container: playlist "{}" removed.'.format(p.name()))


class Jukebox(SpotifySessionManager):

    def __init__(self, *a, **kw):
        SpotifySessionManager.__init__(self, *a, **kw)

        try:
            AudioSink = import_audio_sink(selected_sink)
        except ImportError:
            print('Selected audiosink failed to be imported,'
                  'please try a different one')
            sys.exit(1)

        self.audio = AudioSink(backend=self)
        self.ui = JukeboxUI(self)
        self.ctr = None
        self.playing = False
        self._queue = []
        self.logfile = open('log.txt', 'w', 0)
        self.playlist_manager = JukeboxPlaylistManager()
        self.container_manager = JukeboxContainerManager()
        print('Logging in, please wait...')

    def write_log(self, logstring):
        self.logfile.write(logstring)

    def close_log(self):
        if not self.logfile.closed:
            self.logfile.close()

    def logged_in(self, session, error):
        if error:
            print(error)
            return
        print('Logged in!')
        self.ctr = session.playlist_container()
        self.container_manager.watch(self.ctr)
        self.starred = session.starred()
        if not self.ui.is_alive():
            self.ui.start()

    def logged_out(self, session):
        self.close_log()
        print('Logged out!')

    def play_token_lost(self, session):
        print('Same account used elsewhere, stopping playback')
        self.stop()

    def credentials_blob_updated(self, session, blob):
        with open('spotify_cred_blob.txt', 'w') as cred_file:
            cred_file.write(blob)
        self.write_log('Credentials blob updated: {}\n'.format(blob))

    def log_message(self, session, logmessage):
        self.write_log('Spotify: {}'.format(logmessage))

    def connection_error(self, session, logmessage):
        self.write_log('Error: {}'.format(logmessage))

    def message_to_user(self, session, logmessage):
        self.write_log('User: {}'.format(logmessage))

    def load_track(self, track):
        print('Loading track...')
        while not track.is_loaded():
            time.sleep(0.1)
        if track.is_autolinked():  # if linked, load the target track instead
            print('Autolinked track, loading the linked-to track')
            return self.load_track(track.playable())
        if track.availability() != 1:
            print('Track not available ({})'.format(track.availability()))
        if self.playing:
            self.stop()
        self.session.load(track)
        print('Loaded track: {}'.format(track.name()))

    def load(self, playlist, track):
        if self.playing:
            self.stop()
        if 0 <= playlist < len(self.ctr):
            pl = self.ctr[playlist]
        elif playlist == len(self.ctr):
            pl = self.starred
        spot_track = pl[track]
        try:
            self.session.load(spot_track)
            print('Loading "{} - {}" from {}'.format(spot_track.artists()[0],
                                                     spot_track.name(),
                                                     pl.name()))
        except SpotifyError as e:
            print('Unable to load track: {}'.format(e))
            print('Skipping track - continue playing')

    def load_playlist(self, playlist):
        if self.playing:
            self.stop()
        if 0 <= playlist < len(self.ctr):
            pl = self.ctr[playlist]
        elif playlist == len(self.ctr):
            pl = self.starred
        print('Loading playlist "{}"'.format(pl.name()))
        if len(pl):
            print('Loading "{}" from "{}"'.format(pl[0].name(), pl.name()))
            self.session.load(pl[0])
        print("Queueing remaining {} tracks".format(len(pl) - 1))
        for i, track in enumerate(pl):
            if i == 0:
                continue
            self._queue.append((playlist, i))

    def queue(self, playlist, track):
        if self.playing:
            self._queue.append((playlist, track))
        else:
            self.load(playlist, track)
            self.play()

    def play(self):
        if self.playing:
            return
        self.audio.start()
        self.session.play(1)
        self.playing = True
        print('Playing')

    def pause(self):
        self.playing = False
        self.session.play(0)
        self.audio.pause()
        print('Pausing')

    def stop(self):
        self.playing = False
        self.session.play(0)
        self.audio.stop()
        print('Stopping')

    def music_delivery_safe(self, *args, **kwargs):
        try:
            return self.audio.music_delivery(*args, **kwargs)
        except IOError as e:
            # TODO: Find way to terminate nicely, perhaps set a flag?
            print(e)
            print('Selected audio sink not functional - please try a different'
                  'one')
            return 0

    def next(self):
        self.stop()
        if self._queue:
            t = self._queue.pop(0)
            self.load(*t)
            self.play()
        else:
            print('Queue empty, stopping playback')
            self.stop()

    def end_of_track(self, sess):
        print('Track end')
        self.audio.end_of_track()

    def search(self, *args, **kwargs):
        self.session.search(*args, **kwargs)

    def get_album_type(self, album):
        album_type = {
            Album.ALBUM: "Album",
            Album.SINGLE: "Single",
            Album.COMPILATION: "Compilation",
            Album.UNKNOWN: "(?)"
        }
        return album_type[album.type()]

    def browse(self, link, callback):
        if link.type() == link.LINK_ALBUM:
            browser = self.session.browse_album(link.as_album(), callback)
            while not browser.is_loaded():
                time.sleep(0.1)
            print('Tracks: ({count})'.format(count=len(browser)))
            for track in browser:
                s = '  {name:<20} | {link}'
                print(s.format(link=Link.from_track(track), name=track.name()))

        if link.type() == link.LINK_ARTIST:
            browser = ArtistBrowser(link.as_artist())
            while not browser.is_loaded():
                time.sleep(0.1)
            print('=== Top 10 tracks:')
            for i, track in enumerate(browser.tophit_tracks()):
                if i >= 10:
                    break
                s = '{0:>3d} {name:<25} ({duration}) {link})'
                print(s.format(i + 1, link=Link.from_track(track),
                      name=track.name(),
                      duration=self.ui.pretty_duration(track.duration())))
            print('=== Albums:')
            print(' Name            | Year | Tracks | Type        | \
Spotify URI')
            print('-----------------------------------------------------------\
---------------------')
            for album in browser.albums():
                album_browser = self.session.browse_album(album, callback)
                while not album_browser.is_loaded():
                    time.sleep(0.1)
                s = ' {name:<15} | {year} | {count:<6d} | {type:<11} | {link}'
                print(s.format(link=Link.from_album(album), name=album.name(),
                      count=len(album_browser), year=album.year(),
                      type=self.get_album_type(album)))

    def watch(self, p, unwatch=False):
        if not unwatch:
            print('Watching playlist: {}'.format(p.name()))
            self.playlist_manager.watch(p)
        else:
            print('Unwatching playlist: {}'.format(p.name()))
            self.playlist_manager.unwatch(p)

    def toplist(self, tl_type, tl_region):
        print(repr(tl_type))
        print(repr(tl_region))

        def callback(tb, ud):
            for i in xrange(len(tb)):
                print('{:>3d}: {}'.format((i+1, tb[i].name())))

        ToplistBrowser(tl_type, tl_region, callback)

    def get_offline_status(self, playlist):
        print(playlist.get_offline_status())

    def set_offline_mode(self, playlist, offline):
        playlist.set_offline_mode(offline)

    def get_offline_download_completed(self, playlist):
        s = '{} %% of download completed'
        print(s.format(playlist.get_offline_download_completed()))

    def shell(self):
        import code
        shell = code.InteractiveConsole(globals())
        shell.interact()

if __name__ == '__main__':
    import argparse
    import sys

    appkey_available = False
    blob = ''

    audiosinks = {
        'alsa': (('spotify.audiosink.gstreamer', 'GstreamerSink'),),
        'oss': (('spotify.audiosink.oss', 'OssSink'),),
        'portaudio': (('spotify.audiosink.portaudio', 'PortAudioSink'),),
        'gstreamer': (('spotify.audiosink.gstreamer', 'GstreamerSink'),)
    }

    try:
        # session.py will automagically try to load 'spotify_appkey.key' so
        # this is just a test to catch this error early
        if b'appkey_good' not in open('spotify_appkey.key').read():
            print("Appkey present...")
            appkey_available = True
    except IOError:
        print("""ERROR: 'spotify_appkey.key' not present

The file is needed to run this example script
Please go to https://developer.spotify.com/technologies/libspotify/keys/ and
download the binary key and move it to the directory with the example code""")
        sys.exit(1)

    try:
        # Allow user to login with username+blob
        with open('spotify_cred_blob.txt') as cred_file:
            blob = cred_file.read()
    except IOError:
        print("""Info: 'spotify_cred_blob.txt' not present
            Must have previously used "-r" (see help) or must have
            username+password or username+credentials blob""")

    parser = argparse.ArgumentParser(description='Example code showing how '
                                     'to use pyspotify')
    parser.add_argument('-a', '--audiosink', metavar='audiosink',
                        help='Select audiosink.', required=False,
                        choices=audiosinks.keys())
    parser.add_argument('-r', '--remember-me', action='store_true',
                        help='Save login details')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Show debug information')
    parser.add_argument('--version', action='version', version='%(prog)s 0.2')

    parser.add_argument('-u', '--username', metavar='username',
                        help='Spotify username', required=False)
    parser.add_argument('-p', '--password', metavar='password',
                        help='Spotify password', required=False)
    options = parser.parse_args()

    if options.audiosink is None:
        selected_sink = audiosinks['alsa']
    else:
        selected_sink = audiosinks[options.audiosink]

    if options.verbose:
        logging.basicConfig(level=logging.DEBUG)
    session_m = Jukebox(username=options.username,
                        password=options.password,
                        remember_me=True,
                        login_blob=blob)
    session_m.connect()
