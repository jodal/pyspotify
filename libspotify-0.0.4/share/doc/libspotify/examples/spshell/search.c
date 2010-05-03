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
 * Print the given album metadata
 *
 * @param  album  The album object
 */
static void print_album(sp_album *album)
{
	printf("  Album \"%s\" (%d)\n",
	       sp_album_name(album),
	       sp_album_year(album));
}

/**
 * Print the given artist metadata
 *
 * @param  artist  The artist object
 */
static void print_artist(sp_artist *artist)
{
	printf("  Artist \"%s\"\n", sp_artist_name(artist));
}

/**
 * Print the given search result with as much information as possible
 *
 * @param  search   The search result
 */
static void print_search(sp_search *search)
{
	int i;

	printf("Query          : %s\n", sp_search_query(search));
	printf("Did you mean   : %s\n", sp_search_did_you_mean(search));
	printf("Tracks in total: %d\n", sp_search_total_tracks(search));
	puts("");

	for (i = 0; i < sp_search_num_tracks(search); ++i)
		print_track(sp_search_track(search, i));

	puts("");

	for (i = 0; i < sp_search_num_albums(search); ++i)
		print_album(sp_search_album(search, i));

	puts("");

	for (i = 0; i < sp_search_num_artists(search); ++i)
		print_artist(sp_search_artist(search, i));

	puts("");
}

/**
 * Callback for libspotify
 *
 * @param browse    The browse result object that is now done
 * @param userdata  The opaque pointer given to sp_artistbrowse_create()
 */
static void search_complete(sp_search *search, void *userdata)
{
	if (sp_search_error(search) == SP_ERROR_OK)
		print_search(search);
	else
		fprintf(stderr, "Failed to search: %s\n",
		        sp_error_message(sp_search_error(search)));

	sp_search_release(search);
	cmd_done();
}



/**
 *
 */
static void search_usage(void)
{
	fprintf(stderr, "Usage: search <query>\n");
}


/**
 *
 */
int cmd_search(int argc, char **argv)
{
	char query[1024];
	int i;

	if (argc < 2) {
		search_usage();
		return -1;
	}

	query[0] = 0;
	for(i = 1; i < argc; i++)
		snprintf(query + strlen(query), sizeof(query) - strlen(query), "%s%s",
			 i == 1 ? "" : " ", argv[i]);

	sp_search_create(g_session, query, 0, 100, 0, 100, 0, 100, &search_complete, NULL);
	return 0;
}


/**
 *
 */
int cmd_whatsnew(int argc, char **argv)
{
	sp_search_create(g_session, "tag:new", 0, 0, 0, 250, 0, 0, &search_complete, NULL);
	return 0;
}



/**
 *
 */
struct {
	const char *name;
	sp_radio_genre id;
} radiogenres[] = {
	{ "AltPopRock",     SP_RADIO_GENRE_ALT_POP_ROCK },
	{ "Blues",          SP_RADIO_GENRE_BLUES        },
	{ "Country",        SP_RADIO_GENRE_COUNTRY      },
	{ "Disco",          SP_RADIO_GENRE_DISCO        },
	{ "Funk",           SP_RADIO_GENRE_FUNK         },
	{ "Hardrock",       SP_RADIO_GENRE_HARD_ROCK    },
	{ "HeavyMetal",     SP_RADIO_GENRE_HEAVY_METAL  },
	{ "Rap",            SP_RADIO_GENRE_RAP          },
	{ "House",          SP_RADIO_GENRE_HOUSE        },
	{ "Jazz",           SP_RADIO_GENRE_JAZZ         },
	{ "NewWave",        SP_RADIO_GENRE_NEW_WAVE     },
	{ "RnB",            SP_RADIO_GENRE_RNB          },
	{ "Pop",            SP_RADIO_GENRE_POP          },
	{ "Punk",           SP_RADIO_GENRE_PUNK         },
	{ "Reggae",         SP_RADIO_GENRE_REGGAE       },
	{ "PopRock",        SP_RADIO_GENRE_POP_ROCK     },
	{ "Soul",           SP_RADIO_GENRE_SOUL         },
	{ "Techno",         SP_RADIO_GENRE_TECHNO       },
};



/**
 *
 */
static void radio_usage(void)
{
	int i;
	fprintf(stderr, "Usage: radio <startyear> <stopyear> [<genre> ...]\n");
	fprintf(stderr, "  Genres:\n");
	for(i = 0; i < sizeof(radiogenres) / sizeof(radiogenres[0]); i++)
		fprintf(stderr, "\t%s\n", radiogenres[i].name);
}

/**
 *
 */
int cmd_radio(int argc, char **argv)
{
	sp_radio_genre mask = 0;
	int i, j;

	if (argc < 3) {
		radio_usage();
		return -1;
	}

	for(i = 3; i < argc; i++)
		for(j = 0; j < sizeof(radiogenres) / sizeof(radiogenres[0]); j++)
			if (!strcasecmp(radiogenres[j].name, argv[i]))
				mask |= radiogenres[j].id;

	sp_radio_search_create(g_session, atoi(argv[1]), atoi(argv[2]), mask, &search_complete, NULL);
	return 0;
}
