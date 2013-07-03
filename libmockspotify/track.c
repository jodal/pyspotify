#include "libmockspotify.h"
#include "util.h"

sp_track *
mocksp_track_create(const char *name, int num_artists, sp_artist **artists, sp_album *album,
                    int duration, int popularity, int disc, int index, sp_error error,
                    bool is_loaded, sp_track_availability availability, sp_track_offline_status status,
                    bool is_local, bool is_autolinked, sp_track *playable,
                    bool is_starred, bool is_placeholder)
{
  sp_track *track = ALLOC(sp_track);

  if ( ! playable)
  {
    playable = track;
  }

  track->name          = strclone(name);
  track->album         = album;
  track->duration      = duration;
  track->popularity    = popularity;
  track->disc          = disc;
  track->index         = index;
  track->error         = error;
  track->is_loaded     = is_loaded;
  track->availability  = availability;
  track->offline_status = status;
  track->is_local      = is_local;
  track->is_autolinked = is_autolinked;
  track->get_playable  = playable;
  track->is_starred    = is_starred;
  track->is_placeholder = is_placeholder;

  track->artists     = ALLOC_N(sp_artist *, num_artists);
  track->num_artists = num_artists;
  MEMCPY_N(track->artists, artists, sp_artist*, num_artists);

  return track;
}

DEFINE_REFCOUNTERS_FOR(track);
DEFINE_READER(track, name, const char *);
DEFINE_READER(track, album, sp_album *);
DEFINE_READER(track, duration, int);
DEFINE_READER(track, popularity, int);
DEFINE_READER(track, disc, int);
DEFINE_READER(track, index, int);
DEFINE_READER(track, error, sp_error);
DEFINE_READER(track, is_loaded, bool);
DEFINE_READER(track, is_placeholder, bool);
DEFINE_SESSION_READER(track, get_playable, sp_track *);
DEFINE_SESSION_READER(track, is_local, bool);
DEFINE_SESSION_READER(track, is_autolinked, bool);
DEFINE_SESSION_READER(track, is_starred, bool);
DEFINE_READER(track, num_artists, int);
DEFINE_ARRAY_READER(track, artist, sp_artist *);

sp_track_availability
sp_track_get_availability(sp_session *UNUSED(session), sp_track *track)
{
  return sp_track_is_loaded(track) ? track->availability : SP_TRACK_AVAILABILITY_UNAVAILABLE;
}

sp_track *
sp_localtrack_create(const char *artist, const char *title, const char *album, int length)
{
  sp_artist *partist = mocksp_artist_create(artist, NULL, true);
  sp_album  *palbum  = NULL;

  if (strlen(album) > 0)
  {
    palbum  = mocksp_album_create(album, partist, 2011, NULL, SP_ALBUMTYPE_UNKNOWN, 1, 1);
  }

  return mocksp_track_create(title, 1, &partist, palbum, length, 0, 0, 0, SP_ERROR_OK, true, SP_TRACK_AVAILABILITY_AVAILABLE, SP_TRACK_OFFLINE_DONE, true, false, NULL, false, false);
}

sp_error
sp_track_set_starred(sp_session *UNUSED(session), sp_track *const *tracks, int num_tracks, bool starred)
{
  int i;

  for (i = 0; i < num_tracks; i++)
  {
    tracks[i]->is_starred = starred;
  }
  return SP_ERROR_OK;
}

sp_track_offline_status
sp_track_offline_get_status(sp_track *track)
{
  return track->offline_status;
}
