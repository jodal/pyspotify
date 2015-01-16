#include "libmockspotify.h"
#include "util.h"

sp_albumbrowse *
mocksp_albumbrowse_create(sp_error error, int request_duration, sp_album *album, sp_artist *artist,
                          int num_copyrights, const char **copyrights, int num_tracks,
                          sp_track **tracks, const char *review, albumbrowse_complete_cb *cb,
                          void *userdata)
{
  int i = 0;
  sp_albumbrowse *albumbrowse = ALLOC(sp_albumbrowse);

  albumbrowse->error  = error;
  albumbrowse->album  = album;
  albumbrowse->artist = artist;

  albumbrowse->copyrights     = ALLOC_N(char*, num_copyrights);
  albumbrowse->num_copyrights = num_copyrights;
  for (i = 0; i < num_copyrights; ++i)
  {
    albumbrowse->copyrights[i] = strclone(copyrights[i]);
  }

  albumbrowse->tracks     = ALLOC_N(sp_track*, num_tracks);
  albumbrowse->num_tracks = num_tracks;
  MEMCPY_N(albumbrowse->tracks, tracks, sp_track *, num_tracks);

  albumbrowse->review    = strclone(review);
  albumbrowse->backend_request_duration = request_duration;

  albumbrowse->callback = cb;
  albumbrowse->userdata = userdata;

  return albumbrowse;
}

DEFINE_REFCOUNTERS_FOR(albumbrowse);
DEFINE_READER(albumbrowse, error, sp_error);
DEFINE_READER(albumbrowse, backend_request_duration, int);
DEFINE_READER(albumbrowse, album, sp_album *);
DEFINE_READER(albumbrowse, artist, sp_artist *);
DEFINE_READER(albumbrowse, num_copyrights, int);
DEFINE_ARRAY_READER(albumbrowse, copyright, const char *);
DEFINE_READER(albumbrowse, num_tracks, int);
DEFINE_ARRAY_READER(albumbrowse, track, sp_track *);
DEFINE_READER(albumbrowse, review, const char *);

bool
sp_albumbrowse_is_loaded(sp_albumbrowse *albumbrowse)
{
  return albumbrowse->error == SP_ERROR_OK;
}

sp_albumbrowse *
sp_albumbrowse_create(sp_session *UNUSED(session), sp_album *album, albumbrowse_complete_cb cb, void *userdata)
{
  sp_link *link = sp_link_create_from_album(album);
  char *albumbrowse_link;
  sp_albumbrowse *browser;

  if (link == NULL || sp_link_type(link) != SP_LINKTYPE_ALBUM)
  {
    return NULL;
  }

  albumbrowse_link = ALLOC_STR(strlen("spotify:albumbrowse:1xvnWMz2PNFf7mXOSRuLws"));
  sprintf(albumbrowse_link, "spotify:albumbrowse:%s", link->data + strlen("spotify:album:"));
  browser = (sp_albumbrowse *)registry_find(albumbrowse_link);
  if (cb)
      cb(browser, userdata);
  return browser;
}
