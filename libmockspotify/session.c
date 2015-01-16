#include "libmockspotify.h"
#include "util.h"

sp_session *
mocksp_session_create(const sp_session_config *config, sp_connectionstate connectionstate,
                      int offline_time_left, sp_offline_sync_status *sync_status,
                      int offline_num_playlists, int offline_tracks_to_sync, sp_playlist *inbox)
{
  sp_session *session = ALLOC(sp_session);

  sp_session_config *cloned_config = ALLOC(sp_session_config);
  if (config)
  {
    config = MEMCPY(cloned_config, config, sp_session_config);
  }
  cloned_config->application_key = "appkey_good";

  sp_session_create(cloned_config, &session);

  session->connectionstate = connectionstate;

  session->offline_time_left = offline_time_left;

  if (sync_status)
  {
    session->offline_sync_status = ALLOC(sp_offline_sync_status);
    MEMCPY(session->offline_sync_status, sync_status, sp_offline_sync_status);
  }

  session->offline_num_playlists = offline_num_playlists;
  session->offline_tracks_to_sync = offline_tracks_to_sync;

  session->inbox = inbox;

  return session;
}

DEFINE_REFCOUNTERS_FOR(session);
DEFINE_READER(session, connectionstate, sp_connectionstate);

const char * sp_build_id(void)
{
  return "10.1.16.g7a6bc7ea Release Darwin-x86_64 ";
}

sp_playlistcontainer *
sp_session_playlistcontainer(sp_session *session)
{
  return sp_session_publishedcontainer_for_user_create(session, NULL);
}

sp_playlistcontainer *
sp_session_publishedcontainer_for_user_create(sp_session *session, const char *username)
{
  char *link;

  if (sp_session_connectionstate(session) != SP_CONNECTION_STATE_LOGGED_IN)
  {
    return NULL;
  }

  if (username == NULL && session->user)
  {
    username = session->user->canonical_name;
  }

  link = ALLOC_STR(strlen("spotify:container:") + strlen(username));
  sprintf(link, "spotify:container:%s", username);
  return (sp_playlistcontainer *)registry_find(link);
}

sp_error
sp_session_create(const sp_session_config *config, sp_session * *sess)
{
  sp_session *session;

  if (memcmp(config->application_key, "appkey_good", config->application_key_size))
      return SP_ERROR_BAD_APPLICATION_KEY;

  session = *sess = ALLOC(sp_session);

  session->config.api_version       = config->api_version;
  session->config.cache_location    = strclone(config->cache_location);
  session->config.settings_location = strclone(config->settings_location);
  session->config.user_agent        = strclone(config->user_agent);
  session->config.callbacks         = ALLOC(sp_session_callbacks);
  session->config.userdata          = config->userdata;

  session->config.application_key   = ALLOC_N(byte, config->application_key_size);
  memcpy((char *) session->config.application_key, config->application_key, config->application_key_size);

  if (config->callbacks)
  {
    MEMCPY((sp_session_callbacks *) session->config.callbacks, config->callbacks, sp_session_callbacks);
  }

  // sp_session defaults
  session->cache_size = 0;

  // TODO: v0.0.8 (and earlier) directly call `notify_main_thread` callback here, before returning
  if (config->callbacks && config->callbacks->notify_main_thread)
    config->callbacks->notify_main_thread(session);

  return SP_ERROR_OK;
}

sp_error
sp_session_process_events(sp_session *UNUSED(session), int *next_timeout)
{
  *next_timeout = 1;
  return SP_ERROR_OK;
}

sp_error
sp_session_login(sp_session *session, const char *username, const char *UNUSED(password), bool remember_me, const char *UNUSED(blob))
{
  session->user = mocksp_user_create(username, username, true);
  session->connectionstate = SP_CONNECTION_STATE_LOGGED_IN;

  if (remember_me)
  {
    session->username = strclone(username);
  }
  // Call callbacks if they exist
  if (session->config.callbacks != NULL)
  {
    if (session->config.callbacks->logged_in != NULL)
      session->config.callbacks->logged_in(session, SP_ERROR_OK);
    if (session->config.callbacks->notify_main_thread != NULL)
      session->config.callbacks->notify_main_thread(session);
  }
  return SP_ERROR_OK;
}

sp_error
sp_session_relogin(sp_session *session)
{
  if ( ! session->username)
  {
    return SP_ERROR_NO_CREDENTIALS;
  }

  sp_session_login(session, session->username, NULL, true, NULL);
  return SP_ERROR_OK;
}

int
sp_session_remembered_user(sp_session *session, char *buffer, size_t buffer_size)
{
  if ( ! session->username)
  {
    return -1;
  }

  strncpy(buffer, session->username, buffer_size);

  if (buffer_size > 0)
  {
    buffer[buffer_size - 1] = '\0';
  }

  return (int) strlen(session->username);
}

sp_error
sp_session_forget_me(sp_session *session)
{
  session->username = NULL;
  return SP_ERROR_OK;
}

sp_error
sp_session_logout(sp_session *session)
{
  session->connectionstate = SP_CONNECTION_STATE_LOGGED_OUT;
  // Call callbacks if they exist
  if (session->config.callbacks != NULL)
  {
    if (session->config.callbacks->notify_main_thread != NULL)
      session->config.callbacks->notify_main_thread(session);
    if (session->config.callbacks->logged_out != NULL)
      session->config.callbacks->logged_out(session);
  }
  return SP_ERROR_OK;
}

sp_error
sp_session_flush_caches(sp_session *session)
{
  // no op
  return SP_ERROR_OK;
}

sp_user *
sp_session_user(sp_session *session)
{
  return session->user;
}

int
sp_session_user_country(sp_session *UNUSED(session))
{
  return ('S' << 8 | 'E');
}

sp_error
sp_session_set_cache_size(sp_session *session, size_t size)
{
  session->cache_size = size;
  return SP_ERROR_OK;
}

sp_error
sp_session_preferred_bitrate(sp_session *session, sp_bitrate bitrate)
{
  session->preferred_bitrate = bitrate;
  return SP_ERROR_OK;
}

sp_error
sp_session_set_connection_type(sp_session *session, sp_connection_type connection_type)
{
  session->connection_type = connection_type;
  return SP_ERROR_OK;
}

sp_error
sp_session_set_connection_rules(sp_session *session, sp_connection_rules connection_rules)
{
  session->connection_rules = connection_rules;
  return SP_ERROR_OK;
}

sp_error
sp_session_preferred_offline_bitrate(sp_session *UNUSED(session), sp_bitrate UNUSED(bitrate), bool UNUSED(allow_resync))
{
  return SP_ERROR_OK;
}

bool
sp_offline_sync_get_status(sp_session *session, sp_offline_sync_status *status)
{
  if (session->offline_sync_status)
  {
    MEMCPY(status, session->offline_sync_status, sp_offline_sync_status);
    return true;
  }

  return false;
}

int sp_offline_time_left(sp_session *x) { return x->offline_time_left; }
int sp_offline_num_playlists(sp_session *x) { return x->offline_num_playlists; }
int sp_offline_tracks_to_sync(sp_session *x) { return x->offline_tracks_to_sync; }

sp_playlist *
sp_session_starred_create(sp_session *session)
{
  if (sp_session_connectionstate(session) != SP_CONNECTION_STATE_LOGGED_IN)
  {
    return NULL;
  }

  return sp_session_starred_for_user_create(session, sp_user_canonical_name(session->user));
}

sp_playlist *
sp_session_starred_for_user_create(sp_session *session, const char *name)
{
  char *link;

  if (sp_session_connectionstate(session) != SP_CONNECTION_STATE_LOGGED_IN)
  {
    return NULL;
  }

  link = ALLOC_STR(strlen("spotify:user:") + strlen(name) + strlen(":starred"));
  sprintf(link, "spotify:user:%s:starred", name);
  return (sp_playlist *)registry_find(link);
}

sp_playlist *
sp_session_inbox_create(sp_session *session)
{
  if (sp_session_connectionstate(session) != SP_CONNECTION_STATE_LOGGED_IN)
  {
    return NULL;
  }

  return session->inbox;
}

bool
sp_session_get_volume_normalization(sp_session *session)
{
  return session->volume_normalization;
}

sp_error
sp_session_set_volume_normalization(sp_session *session, bool yepnope)
{
  session->volume_normalization = yepnope;
  return SP_ERROR_OK;
}

void *
sp_session_userdata(sp_session *session)
{
  return session->config.userdata;
}
