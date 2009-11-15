#!/usr/bin/env python

import cmd
import readline
import sys
import traceback
import time
import threading

from spotify.manager import SpotifySessionManager
from spotify.alsahelper import AlsaController

class JukeboxUI(cmd.Cmd, threading.Thread):

    prompt = "jukebox> "

    def __init__(self, jukebox):
        cmd.Cmd.__init__(self)
        threading.Thread.__init__(self)
        self.jukebox = jukebox
        self.playlist = None
        self.track = None

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
        try:
            playlist, track = map(int, line.split(' ', 1))
        except ValueError:
            print "Usage: play playlist track"
            return
        self.jukebox.load(playlist, track)
        self.jukebox.play()

    def do_stop(self, line):
        self.jukebox.stop()

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
        print "Logging in, please wait..."

    def logged_in(self, session, error):
        self.session = session
        try:
            self.ctr = session.playlist_container()
            self.ui.start()
        except:
            traceback.print_exc()

    def load(self, playlist, track):
        self.session.load(self.ctr[playlist][track])
        print "Loading %s from %s" % (self.ctr[playlist][track].name(), self.ctr[playlist].name())

    def play(self):
        self.session.play(1)
        print "Playing"

    def stop(self):
        self.session.play(0)
        print "Stopping"

    def music_delivery(self, *a, **kw):
        return self.audio.music_delivery(*a, **kw)

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

