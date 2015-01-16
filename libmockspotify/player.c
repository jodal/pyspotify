#include "libmockspotify.h"
#include "util.h"

sp_error
sp_session_player_load(sp_session *session, sp_track *track)
{
  session->player.track = track;
  return SP_ERROR_OK;
}

sp_error
sp_session_player_seek(sp_session *session, int offset)
{
  session->player.position = offset;
  return SP_ERROR_OK;
}

sp_error
sp_session_player_play(sp_session *session, bool play)
{
  session->player.playing = play;
  return SP_ERROR_OK;
}

sp_error
sp_session_player_unload(sp_session *session)
{
  session->player.track = NULL;
  return SP_ERROR_OK;
}

sp_error
sp_session_player_prefetch(sp_session *UNUSED(session), sp_track *UNUSED(track))
{
  return SP_ERROR_OK;
}
