#include "libmockspotify.h"
#include "util.h"

sp_artistbrowse *
mocksp_artistbrowse_create(sp_error error, int request_duration, sp_artist *artist,
                           int num_portraits, const byte **portraits,
                           int num_tracks, sp_track **tracks,
                           int num_albums, sp_album **albums,
                           int num_similar_artists, sp_artist **similar_artists,
                           int num_tophit_tracks, sp_track **tophit_tracks,
                           const char *biography, sp_artistbrowse_type type,
                           artistbrowse_complete_cb *cb, void *userdata)
{
  int i = 0;
  sp_artistbrowse *artistbrowse = ALLOC(sp_artistbrowse);

  artistbrowse->error = error;
  artistbrowse->backend_request_duration = request_duration;
  artistbrowse->artist = artist;

  artistbrowse->portraits     = ALLOC_N(byte *, num_portraits);
  artistbrowse->num_portraits = num_portraits;
  for (i = 0; i < num_portraits; ++i)
  {
    artistbrowse->portraits[i] = ALLOC_N(byte, 20); // image_id = 20 bytes
    MEMCPY_N(artistbrowse->portraits[i], portraits[i], byte, 20);
  }

  artistbrowse->tracks     = ALLOC_N(sp_track *, num_tracks);
  artistbrowse->num_tracks = num_tracks;
  MEMCPY_N(artistbrowse->tracks, tracks, sp_track *, num_tracks);

  artistbrowse->albums     = ALLOC_N(sp_album *, num_albums);
  artistbrowse->num_albums = num_albums;
  MEMCPY_N(artistbrowse->albums, albums, sp_album *, num_albums);

  artistbrowse->similar_artists     = ALLOC_N(sp_artist *, num_similar_artists);
  artistbrowse->num_similar_artists = num_similar_artists;
  MEMCPY_N(artistbrowse->similar_artists, similar_artists, sp_artist *, num_similar_artists);

  artistbrowse->tophit_tracks     = ALLOC_N(sp_track *, num_tophit_tracks);
  artistbrowse->num_tophit_tracks = num_tophit_tracks;
  MEMCPY_N(artistbrowse->tophit_tracks, tophit_tracks, sp_track *, num_tophit_tracks);

  artistbrowse->biography = strclone(biography);
  artistbrowse->type      = type;

  artistbrowse->callback = cb;
  artistbrowse->userdata = userdata;

  return artistbrowse;
}

DEFINE_REFCOUNTERS_FOR(artistbrowse);
DEFINE_READER(artistbrowse, error, sp_error);
DEFINE_READER(artistbrowse, backend_request_duration, int);
DEFINE_READER(artistbrowse, artist, sp_artist *);
DEFINE_READER(artistbrowse, num_portraits, int);
DEFINE_ARRAY_READER(artistbrowse, portrait, const byte *);
DEFINE_READER(artistbrowse, num_tracks, int);
DEFINE_ARRAY_READER(artistbrowse, track, sp_track *);
DEFINE_READER(artistbrowse, num_albums, int);
DEFINE_ARRAY_READER(artistbrowse, album, sp_album *);
DEFINE_READER(artistbrowse, num_similar_artists, int);
DEFINE_ARRAY_READER(artistbrowse, similar_artist, sp_artist *);
DEFINE_READER(artistbrowse, num_tophit_tracks, int);
DEFINE_ARRAY_READER(artistbrowse, tophit_track, sp_track *);
DEFINE_READER(artistbrowse, biography, const char *);

bool
sp_artistbrowse_is_loaded(sp_artistbrowse *artistbrowse)
{
  return artistbrowse->error == SP_ERROR_OK;
}

sp_artistbrowse *
sp_artistbrowse_create(sp_session *UNUSED(session), sp_artist *artist, sp_artistbrowse_type UNUSED(type), artistbrowse_complete_cb *callback, void *userdata)
{
  sp_link *link = sp_link_create_from_artist(artist);
  char *artistbrowse_link;
  sp_artistbrowse *browser;

  if (link == NULL || sp_link_type(link) != SP_LINKTYPE_ARTIST)
  {
    return NULL;
  }

  artistbrowse_link = ALLOC_STR(strlen("spotify:artistbrowse:1xvnWMz2PNFf7mXOSRuLws"));
  sprintf(artistbrowse_link, "spotify:artistbrowse:%s", link->data + strlen("spotify:artist:"));
  browser = (sp_artistbrowse *)registry_find(artistbrowse_link);
  if (callback)
      callback(browser, userdata);
  return browser;
}
