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

#include "spshell.h"
#include "cmd.h"

/**
 *
 */
static void star_usage(const char *prefix)
{
	fprintf(stderr, "Usage: %sstar <track-uri>\n", prefix);
}


/**
 *
 */
static int dostar(int argc, char **argv, int set)
{
	sp_link *link;
	const sp_track *track;

	if (argc != 2) {
		star_usage(set ? "" : "un");
		return -1;
	}
	
	link = sp_link_create_from_string(argv[1]);
	
	if (!link) {
		fprintf(stderr, "Not a spotify link\n");
		return -1;
	}

	if (sp_link_type(link) != SP_LINKTYPE_TRACK) {
		fprintf(stderr, "Not a track link\n");
		sp_link_release(link);
		return -1;
	}

	track = sp_link_as_track(link);
	sp_track_set_starred(g_session, &track, 1, set);
	sp_link_release(link);
	return -1;
}


/**
 *
 */
int cmd_star(int argc, char **argv)
{
	return dostar(argc, argv, 1);
}


/**
 *
 */
int cmd_unstar(int argc, char **argv)
{
	return dostar(argc, argv, 0);
}

/**
 *
 */
int cmd_starred(int argc, char **argv)
{
	browse_playlist(sp_session_starred_create(g_session));
	return 0;
}
