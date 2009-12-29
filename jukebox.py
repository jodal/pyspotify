#!/usr/bin/env python
#
# $Id$
#
# Copyright 2009 Doug Winter
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

import cmd
import readline
import sys
import traceback
import time
import threading

from spotify.manager import SpotifySessionManager
from spotify.alsahelper import AlsaController
from spotify import Link

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
            for i, t in enumerate(self.jukebox.ctr[p]):
                if t.is_loaded():
                    print "%3d %s" % (i, t.name())
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
                self.results = False
        else:
            self.results = None
            def _(results, userdata):
                print "\nSearch results received"
                self.results = results
            self.jukebox.search(line, _)

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

    do_ls = do_list
    do_EOF = do_quit

class Jukebox(SpotifySessionManager):

    queued = False
    playlist = 2
    track = 0

    def __init__(self, *a, **kw):
        SpotifySessionManager.__init__(self, *a, **kw)
        self.audio = AlsaController()
        self.ui = JukeboxUI(self)
        self.ctr = None
        self.playing = False
        self._queue = []
        print "Logging in, please wait..."

    def logged_in(self, session, error):
        self.session = session
        try:
            self.ctr = session.playlist_container()
            self.ui.start()
        except:
            traceback.print_exc()
            
    def load_track(self, track):
        if self.playing:
            self.stop()
        
        self.session.load(track)
        print "Loading %s" % track.name()
        
    def load(self, playlist, track):
        if self.playing:
            self.stop()
        self.session.load(self.ctr[playlist][track])
        print "Loading %s from %s" % (self.ctr[playlist][track].name(), self.ctr[playlist].name())

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

    def search(self, query, callback):
        self.session.search(query, callback)

if __name__ == '__main__':
    import optparse
    op = optparse.OptionParser(version="%prog 0.1")
    op.add_option("-u", "--username", help="spotify username")
    op.add_option("-p", "--password", help="spotify password")
    (options, args) = op.parse_args()
    if not options.username or not options.password:
        op.print_help()
        raise SystemExit
    s = Jukebox(options.username, options.password)
    s.connect()

