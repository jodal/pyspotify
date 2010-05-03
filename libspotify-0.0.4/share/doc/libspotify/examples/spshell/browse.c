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

static sp_track *track_browse;
static sp_playlist *playlist_browse;
static sp_playlist_callbacks pl_callbacks;

/**
 * Print the given track title together with some trivial metadata
 *
 * @param  track   The track object
 */
void print_track(sp_track *track)
{
	int duration = sp_track_duration(track);
	char url[256];
	sp_link *l;

#if WIN32
	printf(" %s ", sp_track_is_starred(track) ? "*" : " ");
#else
	printf(" %s ", sp_track_is_starred(track) ? "★" : "☆");
#endif
	printf("Track %s [%d:%02d] has %d artist(s), %d%% popularity",
	       sp_track_name(track),
	       duration / 60000,
	       (duration / 1000) / 60,
	       sp_track_num_artists(track),
	       sp_track_popularity(track));
	
	if(sp_track_disc(track)) 
		printf(", %d on disc %d",
		       sp_track_index(track),
		       sp_track_disc(track));
	printf("\n");

	l = sp_link_create_from_track(track, 0);
	sp_link_as_string(l, url, sizeof(url));
	printf("\t\t%s\n", url);
	sp_link_release(l);
}

/**
 * Print the given album browse result and as much information as possible
 *
 * @param  browse  The browse result
 */
static void print_albumbrowse(sp_albumbrowse *browse)
{
	int i;

	printf("Album browse of \"%s\" (%d)\n", 
	       sp_album_name(sp_albumbrowse_album(browse)), 
	       sp_album_year(sp_albumbrowse_album(browse)));

	for (i = 0; i < sp_albumbrowse_num_copyrights(browse); ++i)
		printf("  Copyright: %s\n", sp_albumbrowse_copyright(browse, i));

	printf("  Tracks: %d\n", sp_albumbrowse_num_tracks(browse));
	printf("  Review: %.60s...\n", sp_albumbrowse_review(browse));
	puts("");

	for (i = 0; i < sp_albumbrowse_num_tracks(browse); ++i)
		print_track(sp_albumbrowse_track(browse, i));

	puts("");
}

/**
 * Print the given artist browse result and as much information as possible
 *
 * @param  browse  The browse result
 */
static void print_artistbrowse(sp_artistbrowse *browse)
{
	int i;

	printf("Artist browse of \"%s\"\n", sp_artist_name(sp_artistbrowse_artist(browse)));

	for (i = 0; i < sp_artistbrowse_num_similar_artists(browse); ++i)
		printf("  Similar artist: %s\n", sp_artist_name(sp_artistbrowse_similar_artist(browse, i)));

	printf("  Portraits: %d\n", sp_artistbrowse_num_portraits(browse));
	printf("  Tracks   : %d\n", sp_artistbrowse_num_tracks(browse));
	printf("  Biography: %.60s...\n", sp_artistbrowse_biography(browse));
	puts("");

	for (i = 0; i < sp_artistbrowse_num_tracks(browse); ++i)
		print_track(sp_artistbrowse_track(browse, i));

	puts("");
}



/**
 * Callback for libspotify
 *
 * @param browse    The browse result object that is now done
 * @param userdata  The opaque pointer given to sp_albumbrowse_create()
 */
static void browse_album_callback(sp_albumbrowse *browse, void *userdata)
{
	if (sp_albumbrowse_error(browse) == SP_ERROR_OK)
		print_albumbrowse(browse);
	else
		fprintf(stderr, "Failed to browse album: %s\n",
		        sp_error_message(sp_albumbrowse_error(browse)));

	sp_albumbrowse_release(browse);
	cmd_done();
}


/**
 * Callback for libspotify
 *
 * @param browse    The browse result object that is now done
 * @param userdata  The opaque pointer given to sp_artistbrowse_create()
 */
static void browse_artist_callback(sp_artistbrowse *browse, void *userdata)
{
	if (sp_artistbrowse_error(browse) == SP_ERROR_OK)
		print_artistbrowse(browse);
	else
		fprintf(stderr, "Failed to browse artist: %s\n",
		        sp_error_message(sp_artistbrowse_error(browse)));

	sp_artistbrowse_release(browse);
	cmd_done();
}



/**
 *
 */
static void track_browse_try(void)
{
	switch (sp_track_error(track_browse)) {
	case SP_ERROR_OK:
		print_track(track_browse);
		break;

	case SP_ERROR_IS_LOADING:
		return; // Still pending

	default:
		fprintf(stderr, "Unable to resolve track: %s\n", sp_error_message(sp_track_error(track_browse)));
		break;
	}
	
	metadata_updated_fn = NULL;
	cmd_done();
	sp_track_release(track_browse);
}



/**
 *
 */
static void playlist_browse_try(void)
{
	int i, tracks;

	metadata_updated_fn = playlist_browse_try;
	if(!sp_playlist_is_loaded(playlist_browse))
		return;

	tracks = sp_playlist_num_tracks(playlist_browse);
	for(i = 0; i < tracks; i++) {
		sp_track *t = sp_playlist_track(playlist_browse, i);
		if (!sp_track_is_loaded(t))
			return;
	}

	printf("\tPlaylist and metadata loaded\n");

	for(i = 0; i < tracks; i++) {
		sp_track *t = sp_playlist_track(playlist_browse, i);
		
		printf(" %5d: ", i + 1);
		print_track(t);
	}
	sp_playlist_remove_callbacks(playlist_browse, &pl_callbacks, NULL);

	sp_playlist_release(playlist_browse);
	playlist_browse = NULL;
	metadata_updated_fn = NULL;
	cmd_done();
}

/**
 *
 */
static void pl_tracks_added(sp_playlist *pl, sp_track * const * tracks,
			    int num_tracks, int position, void *userdata)
{
	printf("\t%d tracks added\n", num_tracks);
}

/**
 *
 */
static void pl_tracks_removed(sp_playlist *pl, const int *tracks,
			      int num_tracks, void *userdata)
{
	printf("\t%d tracks removed\n", num_tracks);
}

/**
 *
 */
static void pl_tracks_moved(sp_playlist *pl, const int *tracks,
			    int num_tracks, int new_position, void *userdata)
{
	printf("\t%d tracks moved\n", num_tracks);
}

/**
 *
 */
static void pl_renamed(sp_playlist *pl, void *userdata)
{
	printf("\tList name: %s\n",  sp_playlist_name(pl));
}

/**
 *
 */
static void pl_state_change(sp_playlist *pl, void *userdata)
{
	playlist_browse_try();
}

static sp_playlist_callbacks pl_callbacks = {
	pl_tracks_added,
	pl_tracks_removed,
	pl_tracks_moved,
	pl_renamed,
	pl_state_change,
};


void browse_playlist(sp_playlist *pl)
{
	playlist_browse = pl;
	sp_playlist_add_callbacks(playlist_browse, &pl_callbacks, NULL);
	playlist_browse_try();
}

/**
 *
 */
static void browse_usage(void)
{
	fprintf(stderr, "Usage: browse <spotify-uri>\n");
}


/**
 *
 */
int cmd_browse(int argc, char **argv)
{
	sp_link *link;

	if (argc != 2) {
		browse_usage();
		return -1;
	}

	
	link = sp_link_create_from_string(argv[1]);
	
	if (!link) {
		fprintf(stderr, "Not a spotify link\n");
		return -1;
	}

	switch(sp_link_type(link)) {
	default:
		fprintf(stderr, "Can not handle link");
		sp_link_release(link);
		return -1;

	case SP_LINKTYPE_ALBUM:
		sp_albumbrowse_create(g_session, sp_link_as_album(link), browse_album_callback, NULL);
		break;

	case SP_LINKTYPE_ARTIST:
		sp_artistbrowse_create(g_session, sp_link_as_artist(link), browse_artist_callback, NULL);
		break;

	case SP_LINKTYPE_TRACK:
		track_browse = sp_link_as_track(link);
		metadata_updated_fn = track_browse_try;
		sp_track_add_ref(track_browse);
		track_browse_try();
		break;

	case SP_LINKTYPE_PLAYLIST:
		browse_playlist(sp_playlist_create(g_session, link));
		break;
	}

	sp_link_release(link);
	return 0;
}
