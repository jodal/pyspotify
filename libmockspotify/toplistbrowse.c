#include "libmockspotify.h"
#include "util.h"

sp_toplistbrowse *
mocksp_toplistbrowse_create(sp_error error, int request_duration,
                            int num_artists, sp_artist **artists,
                            int num_albums, sp_album **albums,
                            int num_tracks, sp_track **tracks,
                            toplistbrowse_complete_cb *callback, void *userdata)
{
  sp_toplistbrowse *toplistbrowse = ALLOC(sp_toplistbrowse);

  toplistbrowse->error = error;

  toplistbrowse->artists     = ALLOC_N(sp_artist *, num_artists);
  toplistbrowse->num_artists = num_artists;
  MEMCPY_N(toplistbrowse->artists, artists, sp_artist *, num_artists);

  toplistbrowse->albums     = ALLOC_N(sp_album *, num_albums);
  toplistbrowse->num_albums = num_albums;
  MEMCPY_N(toplistbrowse->albums, albums, sp_album *, num_albums);

  toplistbrowse->tracks     = ALLOC_N(sp_track *, num_tracks);
  toplistbrowse->num_tracks = num_tracks;
  MEMCPY_N(toplistbrowse->tracks, tracks, sp_track *, num_tracks);

  toplistbrowse->backend_request_duration = request_duration;

  toplistbrowse->callback = callback;
  toplistbrowse->userdata = userdata;

  return toplistbrowse;
}

DEFINE_REFCOUNTERS_FOR(toplistbrowse);
DEFINE_READER(toplistbrowse, error, sp_error);
DEFINE_READER(toplistbrowse, backend_request_duration, int);
DEFINE_READER(toplistbrowse, num_artists, int);
DEFINE_ARRAY_READER(toplistbrowse, artist, sp_artist *);
DEFINE_READER(toplistbrowse, num_albums, int);
DEFINE_ARRAY_READER(toplistbrowse, album, sp_album *);
DEFINE_READER(toplistbrowse, num_tracks, int);
DEFINE_ARRAY_READER(toplistbrowse, track, sp_track *);

bool
sp_toplistbrowse_is_loaded(sp_toplistbrowse *toplistbrowse)
{
  return toplistbrowse->error == SP_ERROR_OK;
}

sp_toplistbrowse *
sp_toplistbrowse_create(sp_session *UNUSED(session), sp_toplisttype type, sp_toplistregion region, const char *username, toplistbrowse_complete_cb *callback, void *userdata)
{
  char *toplistbrowse_link;
  sp_toplistbrowse *browser;
  const char *str_types[3] = {"artists", "albums", "tracks"};
  const char *real_type = str_types[type];

  if (region == SP_TOPLIST_REGION_USER)
  {
    const char *user = username == NULL ? "current" : username;
    toplistbrowse_link = ALLOC_STR(strlen("spotify:toplist:user::") + strlen(user) + strlen(real_type));
    sprintf(toplistbrowse_link, "spotify:toplist:user:%s:%s", user, real_type);
  }
  else // everywhere or by a country
  {
    const char *real_region = region == SP_TOPLIST_REGION_EVERYWHERE ? "everywhere" : unregion(region);

    // longest possible string: artists everywhere
    toplistbrowse_link = ALLOC_STR(strlen("spotify:toplist::") + strlen(real_type) + strlen(real_region));
    sprintf(toplistbrowse_link, "spotify:toplist:%s:%s", real_type, real_region);
  }

  browser = (sp_toplistbrowse *)registry_find(toplistbrowse_link);
  if (browser && callback)
    callback(browser, userdata);

  return browser;
}
