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

#include <string.h>

#include "spshell.h"
#include "cmd.h"

/**
 *
 */
static void print_album(int index, sp_album *album)
{
	printf("  Album %3d: \"%s\" by \"%s\"\n", index, sp_album_name(album), 
	       sp_artist_name(sp_album_artist(album)));
}

/**
 *
 */
static void print_artist(int index, sp_artist *artist)
{
	printf("  Artist %3d: \"%s\"\n", index, sp_artist_name(artist));
}


/**
 * Callback for libspotify
 *
 * @param result    The toplist result object that is now done
 * @param userdata  The opaque pointer given to sp_toplistbrowse_create()
 */
static void got_toplist(sp_toplistbrowse *result, void *userdata)
{
	int i;

	// We print from all types. Only one of the loops will acually yield anything.

	for(i = 0; i < sp_toplistbrowse_num_artists(result); i++)
		print_artist(i + 1, sp_toplistbrowse_artist(result, i));

	for(i = 0; i < sp_toplistbrowse_num_albums(result); i++)
		print_album(i + 1, sp_toplistbrowse_album(result, i));

	for(i = 0; i < sp_toplistbrowse_num_tracks(result); i++) {
		printf("%3d: ", i + 1);
		print_track(sp_toplistbrowse_track(result, i));
	}

	sp_toplistbrowse_release(result);
	cmd_done();
}



/**
 *
 */
static void toplist_usage(void)
{
	fprintf(stderr, "Usage: toplist (tracks | albums | artists) (global | region <countrycode> | user)\n");
}

/**
 *
 */
int cmd_toplist(int argc, char **argv)
{
	sp_toplisttype type;
	sp_toplistregion region;

	if(argc < 3) {
		toplist_usage();
		return -1;
	}

	if(!strcasecmp(argv[1], "artists"))
		type = SP_TOPLIST_TYPE_ARTISTS;
	else if(!strcasecmp(argv[1], "albums"))
		type = SP_TOPLIST_TYPE_ALBUMS;
	else if(!strcasecmp(argv[1], "tracks"))
		type = SP_TOPLIST_TYPE_TRACKS;
	else {
		toplist_usage();
		return -1;
	}


	if(!strcasecmp(argv[2], "global"))
		region = SP_TOPLIST_REGION_EVERYWHERE;
	else if(!strcasecmp(argv[2], "user"))
		region = SP_TOPLIST_REGION_USER;
	else if(!strcasecmp(argv[2], "region")) {

		if(argc != 4 || strlen(argv[3]) != 2) {
			toplist_usage();
			return -1;
		}
		region = SP_TOPLIST_REGION(argv[3][0], argv[3][1]);
	} else {
		toplist_usage();
		return -1;
	}

	sp_toplistbrowse_create(g_session, type, region, got_toplist, NULL);
	return 0;
}
