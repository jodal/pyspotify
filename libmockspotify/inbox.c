#include "libmockspotify.h"
#include "util.h"

sp_inbox *
sp_inbox_post_tracks(sp_session *UNUSED(session), const char *user, sp_track *const *tracks, int num_tracks, const char *message, inboxpost_complete_cb *callback, void *userdata)
{
  sp_inbox *inbox;

  if (num_tracks <= 0)
  {
    return NULL;
  }

  inbox = ALLOC(sp_inbox);

  inbox->user     = strclone(user);
  inbox->message  = strclone(message);
  inbox->callback = callback;
  inbox->userdata = userdata;

  inbox->tracks = ALLOC_N(sp_track, num_tracks);
  inbox->num_tracks = num_tracks;
  MEMCPY_N(inbox->tracks, tracks, sp_track *, num_tracks);

  return inbox;
}

DEFINE_REFCOUNTERS_FOR(inbox);

sp_error
sp_inbox_error(sp_inbox *UNUSED(inbox))
{
  return SP_ERROR_OK;
}
