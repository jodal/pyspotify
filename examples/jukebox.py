#!/usr/bin/env python

import cmd
import readline
import sys
import traceback
import time
import threading
import os

import spotify
from spotify.manager import SpotifySessionManager, SpotifyPlaylistManager, \
    SpotifyContainerManager
try:
    from spotify.alsahelper import AlsaController
except ImportError:
    from spotify.osshelper import OssController as AlsaController
from spotify import Link, SpotifyError, ToplistBrowser

class JukeboxUI(cmd.Cmd, threading.Thread):

    prompt = "jukebox> "

    def __init__(self, jukebox):
        cmd.Cmd.__init__(self)
        threading.Thread.__init__(self)
        self.jukebox = jukebox
        self.playlist = None
        self.track = None
        self.results = False

    def run(self):
        self.cmdloop()

    def do_logout(self, line):
        self.jukebox.session.logout()

    def do_quit(self, line):
        print "Goodbye!"
        self.jukebox.terminate()
        return True

    def do_list(self, line):
        """ List the playlists, or the contents of a playlist """
        if not line:
            for i, p in enumerate(self.jukebox.ctr):
                if p.is_loaded():
                    print "%3d %s" % (i, p.name())
                else:
                    print "%3d %s" % (i, "loading...")
            print "%3d Starred tracks" % (i + 1,)

        else:
            try:
                p = int(line)
            except ValueError:
                print "that's not a number!"
                return
            if p < 0 or p > len(self.jukebox.ctr):
                print "That's out of range!"
                return
            print "Listing playlist #%d" % p
            if p < len(self.jukebox.ctr):
                playlist = self.jukebox.ctr[p]
            else:
                playlist = self.jukebox.starred
            for i, t in enumerate(playlist):
                if t.is_loaded():
                    print "%3d %s - %s" % (i, t.artists()[0].name(), t.name())
                else:
                    print "%3d %s" % (i, "loading...")

    def do_play(self, line):
        if not line:
            self.jukebox.play()
            return
        if line.startswith("spotify:"):
            # spotify url
            l = Link.from_string(line)
            if not l.type() == Link.LINK_TRACK:
                print "You can only play tracks!"
                return
            self.jukebox.load_track(l.as_track())
        else:
            try:
                playlist, track = map(int, line.split(' ', 1))
            except ValueError:
                print "Usage: play [track_link] | [playlist] [track]"
                return
            self.jukebox.load(playlist, track)
        self.jukebox.play()

    def do_browse(self, line):
        if not line or not line.startswith("spotify:"):
            print "Invalid id provided"
            return
        l = Link.from_string(line)
        if not l.type() in [Link.LINK_ALBUM, Link.LINK_ARTIST]:
            print "You can only browse albums and artists"
            return
        def browse_finished(browser):
            print "Browse finished"
        self.jukebox.browse(l, browse_finished)

    def do_search(self, line):
        if not line:
            if self.results is False:
                print "No search is in progress"
            elif self.results is None:
                print "Searching is in progress"
            else:
                print "Artists:"
                for a in self.results.artists():
                    print "    ", Link.from_artist(a), a.name()
                print "Albums:"
                for a in self.results.albums():
                    print "    ", Link.from_album(a), a.name()
                print "Tracks:"
                for a in self.results.tracks():
                    print "    ", Link.from_track(a, 0), a.name()
                print self.results.total_tracks() - len(self.results.tracks()), "Tracks not shown"
        else:
            self.results = None
            def search_finished(results, userdata):
                print "\nSearch results received"
                self.results = results
            self.jukebox.search(line, search_finished)

    def do_queue(self, line):
        if not line:
            for playlist, track in self.jukebox._queue:
                print playlist, track
            return
        try:
            playlist, track = map(int, line.split(' ', 1))
        except ValueError:
            print "Usage: play playlist track"
            return
        self.jukebox.queue(playlist, track)

    def do_stop(self, line):
        self.jukebox.stop()

    def do_next(self, line):
        self.jukebox.next()

    def emptyline(self):
        pass

    def do_watch(self, line):
        if not line:
            print """Usage: watch [playlist]
You will be notified when tracks are added, moved or removed from the playlist."""
        else:
            try:
                p = int(line)
            except ValueError:
                print "That's not a number!"
                return
            if p < 0 or p >= len(self.jukebox.ctr):
                print "That's out of range!"
                return
            self.jukebox.watch(self.jukebox.ctr[p])

    def do_unwatch(self, line):
        if not line:
            print "Usage: unwatch [playlist]"
        else:
            try:
                p = int(line)
            except ValueError:
                print "That's not a number!"
                return
            if p < 0 or p >= len(self.jukebox.ctr):
                print "That's out of range!"
                return
            self.jukebox.watch(self.jukebox.ctr[p], True)

    def do_toplist(self, line):
        usage = "Usage: toplist (albums|artists|tracks) (GB|FR|..|NO|all|current)"
        if not line:
            print usage
        else:
            args = line.split(' ')
            if len(args) != 2:
                print usage
            else:
                self.jukebox.toplist(*args)

    def do_shell(self, line):
        self.jukebox.shell()

    def do_add_new_playlist(self, line):
        if not line:
            print "Usage: add_new_playlist <name>"
        else:
          new_playlist = self.jukebox.ctr.add_new_playlist(line.decode('utf-8'))

    def do_add_to_playlist(self, line):
        usage = "Usage: add_to_playlist <playlist_index> <insert_point>" + \
                " <search_result_indecies>"
        if not line:
            print usage
            return
        args = line.split(' ')
        if len(args) < 3:
            print usage
        else:
            if not self.results:
                print "No search results"
            else:
                index = int(args.pop(0))
                insert = int(args.pop(0))
                artists = self.results.artists()
                tracks = self.results.tracks()
                for i in args:
                    for a in tracks[int(i)].artists():
                        print u'{}. {} - {} '.format(i,a.name(),tracks[int(i)].name())
                print u'adding them to {} '.format(self.jukebox.ctr[index].name())
                self.jukebox.ctr[index].add_tracks(insert,[tracks[int(i)] for i in args])

    do_ls = do_list
    do_EOF = do_quit


## playlist callbacks ##
class JukeboxPlaylistManager(SpotifyPlaylistManager):
    def tracks_added(self, p, t, i, u):
        print 'Tracks added to playlist %s' % p.name()

    def tracks_moved(self, p, t, i, u):
        print 'Tracks moved in playlist %s' % p.name()

    def tracks_removed(self, p, t, u):
        print 'Tracks removed from playlist %s' % p.name()

## container calllbacks ##
class JukeboxContainerManager(SpotifyContainerManager):
    def container_loaded(self, c, u):
        print 'Container loaded !'

    def playlist_added(self, c, p, i, u):
        print 'Container: playlist "%s" added.' % p.name()

    def playlist_moved(self, c, p, oi, ni, u):
        print 'Container: playlist "%s" moved.' % p.name()

    def playlist_removed(self, c, p, i, u):
        print 'Container: playlist "%s" removed.' % p.name()

class Jukebox(SpotifySessionManager):

    queued = False
    playlist = 2
    track = 0
    appkey_file = os.path.join(os.path.dirname(__file__), 'spotify_appkey.key')

    def __init__(self, *a, **kw):
        SpotifySessionManager.__init__(self, *a, **kw)
        self.audio = AlsaController()
        self.ui = JukeboxUI(self)
        self.ctr = None
        self.playing = False
        self._queue = []
        self.playlist_manager = JukeboxPlaylistManager()
        self.container_manager = JukeboxContainerManager()
        print "Logging in, please wait..."


    def logged_in(self, session, error):
        if error:
            print error
            return
        self.session = session
        try:
            self.ctr = session.playlist_container()
            self.container_manager.watch(self.ctr)
            self.starred = session.starred()
            self.ui.start()
        except:
            traceback.print_exc()

    def logged_out(self, session):
        self.ui.cmdqueue.append("quit")

    def load_track(self, track):
        if self.playing:
            self.stop()
        self.session.load(track)
        print "Loading %s" % track.name()

    def load(self, playlist, track):
        if self.playing:
            self.stop()
        if 0 <= playlist < len(self.ctr):
            pl = self.ctr[playlist]
        elif playlist == len(self.ctr):
            pl = self.starred
        self.session.load(pl[track])
        print "Loading %s from %s" % (pl[track].name(), pl.name())

    def queue(self, playlist, track):
        if self.playing:
            self._queue.append((playlist, track))
        else:
            self.load(playlist, track)
            self.play()

    def play(self):
        self.session.play(1)
        print "Playing"
        self.playing = True

    def stop(self):
        self.session.play(0)
        print "Stopping"
        self.playing = False

    def music_delivery(self, *a, **kw):
        return self.audio.music_delivery(*a, **kw)

    def next(self):
        self.stop()
        if self._queue:
            t = self._queue.pop()
            self.load(*t)
            self.play()
        else:
            self.stop()

    def end_of_track(self, sess):
        print "track ends."
        self.next()

    def search(self, *args, **kwargs):
        self.session.search(*args, **kwargs)

    def browse(self, link, callback):
        if link.type() == link.LINK_ALBUM:
            browser = self.session.browse_album(link.as_album(), callback)
            while not browser.is_loaded():
                time.sleep(0.1)
            for track in browser:
                print track
        if link.type() == link.LINK_ARTIST:
            browser = self.session.browse_artist(link.as_artist(), callback)
            while not browser.is_loaded():
                time.sleep(0.1)
            for album in browser:
                print album.name()
        callback(browser)

    def watch(self, p, unwatch=False):
        if not unwatch:
            print "Watching playlist: %s" % p.name()
            self.playlist_manager.watch(p);
        else:
            print "Unatching playlist: %s" % p.name()
            self.playlist_manager.unwatch(p)

    def toplist(self, tl_type, tl_region):
        print repr(tl_type)
        print repr(tl_region)
        def callback(tb, ud):
            for i in xrange(len(tb)):
                print '%3d: %s' % (i+1, tb[i].name())

        tb = ToplistBrowser(tl_type, tl_region, callback)

    def shell(self):
        import code
        shell = code.InteractiveConsole(globals())
        shell.interact()

if __name__ == '__main__':
    import optparse
    op = optparse.OptionParser(version="%prog 0.1")
    op.add_option("-u", "--username", help="spotify username")
    op.add_option("-p", "--password", help="spotify password")
    (options, args) = op.parse_args()
    session_m = Jukebox(options.username, options.password, True)
    session_m.connect()
