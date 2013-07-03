#include "libmockspotify.h"
#include "util.h"

sp_search *
mocksp_search_create(sp_error error, const char *query, const char *did_you_mean,
                     int total_tracks, int num_tracks, const sp_track **tracks,
                     int total_albums, int num_albums, const sp_album **albums,
                     int total_artists, int num_artists, const sp_artist **artists,
                     int total_playlists, int num_playlists, const sp_playlist **playlists,
                     search_complete_cb *callback, void *userdata)
{
  sp_search *search = ALLOC(sp_search);

  search->error = error;
  search->query = strclone(query);

  if (did_you_mean)
  {
    search->did_you_mean = strclone(did_you_mean);
  }

  search->total_tracks  = total_tracks;
  search->total_artists = total_artists;
  search->total_albums  = total_albums;
  search->total_playlists = total_playlists;

  search->num_tracks  = num_tracks;
  search->num_artists = num_artists;
  search->num_albums  = num_albums;
  search->num_playlists = num_playlists;

  search->tracks  = ALLOC_N(sp_track *, num_tracks);
  search->artists = ALLOC_N(sp_artist *, num_artists);
  search->albums  = ALLOC_N(sp_album *, num_artists);
  search->playlists = ALLOC_N(sp_playlist *, num_playlists);

  MEMCPY_N(search->tracks, tracks, sp_track *, num_tracks);
  MEMCPY_N(search->artists, artists, sp_artist *, num_artists);
  MEMCPY_N(search->albums, albums, sp_album *, num_albums);
  MEMCPY_N(search->playlists, playlists, sp_playlist *, num_playlists);

  search->callback = callback;
  search->userdata = userdata;

  return search;
}

DEFINE_REFCOUNTERS_FOR(search);

DEFINE_READER(search, query, const char *);
DEFINE_READER(search, did_you_mean, const char *);
DEFINE_READER(search, error, sp_error);

DEFINE_READER(search, num_artists, int);
DEFINE_ARRAY_READER(search, artist, sp_artist *);
DEFINE_READER(search, total_artists, int);

DEFINE_READER(search, num_albums, int);
DEFINE_ARRAY_READER(search, album, sp_album *);
DEFINE_READER(search, total_albums, int);

DEFINE_READER(search, num_tracks, int);
DEFINE_ARRAY_READER(search, track, sp_track *);
DEFINE_READER(search, total_tracks, int);

sp_search *
sp_search_create(sp_session *UNUSED(session), const char *query,
                 int UNUSED(tracks_offset), int UNUSED(tracks),
                 int UNUSED(albums_offset), int UNUSED(albums),
                 int UNUSED(artists_offset), int UNUSED(artists),
                 int UNUSED(playlist_offset), int UNUSED(playlists),
                 sp_search_type type,
                 search_complete_cb *UNUSED(cb), void *UNUSED(userdata))
{
  sp_link   *link;
  sp_search *search;

  search = ALLOC(sp_search);
  search->query = strclone(query);
  search->type  = type;
  link = sp_link_create_from_search(search);

  return (sp_search *)registry_find(link->data);
}

bool
sp_search_is_loaded(sp_search *search)
{
  return search->error == SP_ERROR_OK;
}
