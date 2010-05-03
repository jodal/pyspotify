/**
 * Copyright (c) 2006-2010 Spotify Ltd
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 *
 */

#ifndef CMD_H__
#define CMD_H__

extern void cmd_exec_unparsed(char *l);

extern void cmd_dispatch(int argc, char **argv);

extern void cmd_done(void);



extern int cmd_logout(int argc, char **argv);
extern int cmd_browse(int argc, char **argv);
extern int cmd_search(int argc, char **argv);
extern int cmd_radio(int argc, char **argv);
extern int cmd_whatsnew(int argc, char **argv);
extern int cmd_toplist(int argc, char **argv);
extern int cmd_post(int argc, char **argv);
extern int cmd_star(int argc, char **argv);
extern int cmd_unstar(int argc, char **argv);
extern int cmd_starred(int argc, char **argv);
extern int cmd_inbox(int argc, char **argv);



/* Shared functions */
void browse_playlist(sp_playlist *pl);
void print_track(sp_track *track);

#endif // CMD_H__
