#include "libmockspotify.h"
#include "util.h"
#include "time.h"

sp_playlist *
mocksp_playlist_create(const char *name, bool is_loaded, sp_user *owner, bool is_collaborative,
                       const char *description, const byte *image, bool has_pending_changes,
                       unsigned int num_subscribers, sp_subscribers *subscribers, bool is_in_ram,
                       sp_playlist_offline_status offline_status, int offline_download_completed,
                       int num_tracks, sp_playlist_track_t *tracks)
{
  sp_playlist *playlist = ALLOC(sp_playlist);

  playlist->name = strclone(name);
  playlist->is_loaded = is_loaded;
  playlist->owner = owner;
  playlist->is_collaborative = is_collaborative;
  playlist->get_description = strclone(description);

  if (image)
  {
    playlist->image = ALLOC_N(byte, 20);
    MEMCPY_N(playlist->image, image, byte, 20);
  }

  playlist->has_pending_changes = has_pending_changes;

  playlist->num_subscribers = num_subscribers;
  playlist->subscribers     = subscribers;

  playlist->is_in_ram = is_in_ram;
  playlist->get_offline_status = offline_status;
  playlist->get_offline_download_completed = offline_download_completed;

  playlist->num_tracks = num_tracks;
  playlist->tracks     = ALLOC_N(sp_playlist_track_t, num_tracks);
  MEMCPY_N(playlist->tracks, tracks, sp_playlist_track_t, num_tracks);

  /* private mock accessors */
  playlist->autolink_tracks = false;

  return playlist;
}

sp_subscribers *
mocksp_subscribers(int count, char **names)
{
  int i = 0;

  sp_subscribers *subscribers = (sp_subscribers *) malloc(sizeof(sp_subscribers) + sizeof(char*) * (count - 1));
  subscribers->count = count;

  for (i = 0; i < count; ++i)
  {
    subscribers->subscribers[i] = strclone(names[i]);
  }

  return subscribers;
}

sp_error
sp_playlist_subscribers_free(sp_subscribers *subscribers)
{
  unsigned int i;

  for (i = 0; i < subscribers->count; ++i)
  {
    free(subscribers->subscribers[i]);
  }

  free(subscribers);
  return SP_ERROR_OK;
}

DEFINE_REFCOUNTERS_FOR(playlist);

DEFINE_READER(playlist, name, const char *);
DEFINE_READER(playlist, is_loaded, bool);
DEFINE_READER(playlist, num_tracks, int);
DEFINE_READER(playlist, is_collaborative, bool);
DEFINE_READER(playlist, has_pending_changes, bool);
DEFINE_READER(playlist, owner, sp_user *);
DEFINE_READER(playlist, get_description, const char *);
DEFINE_READER(playlist, subscribers, sp_subscribers *);
DEFINE_READER(playlist, num_subscribers, unsigned int);
DEFINE_SESSION_READER(playlist, get_offline_status, sp_playlist_offline_status);
DEFINE_SESSION_READER(playlist, get_offline_download_completed, int);
DEFINE_SESSION_READER(playlist, is_in_ram, bool);

DEFINE_ARRAY_MEMBER_READER(playlist, track, track, sp_track *);
DEFINE_ARRAY_MEMBER_READER(playlist, track, create_time, int);
DEFINE_ARRAY_MEMBER_READER(playlist, track, creator, sp_user *);
DEFINE_ARRAY_MEMBER_READER(playlist, track, message, const char *);
DEFINE_ARRAY_MEMBER_READER(playlist, track, seen, bool);

DEFINE_MOCK_READER(playlist, autolink_tracks, bool);

sp_playlist *
sp_playlist_create(sp_session *UNUSED(session), sp_link *link)
{
  sp_linktype type = sp_link_type(link);

  if (type != SP_LINKTYPE_PLAYLIST && type != SP_LINKTYPE_STARRED)
  {
    return NULL;
  }

  return registry_find(link->data);
}

sp_track *
sp_playlist_track(sp_playlist *playlist, int index)
{
  return sp_playlist_track_track(playlist, index);
}

sp_error
sp_playlist_track_set_seen(sp_playlist *playlist, int index, bool seen)
{
  if (index >= playlist->num_tracks)
  {
    return SP_ERROR_INDEX_OUT_OF_RANGE;
  }

  playlist->tracks[index].seen = seen;
  return SP_ERROR_OK;
}

bool
sp_playlist_get_image(sp_playlist *playlist, byte *buffout)
{
  if (playlist->image)
  {
    MEMCPY_N(buffout, playlist->image, byte, 20);
    return true;
  }

  return false;
}

sp_error
sp_playlist_rename(sp_playlist *playlist, const char *new_name)
{
  size_t length = strlen(new_name);

  if (length == 0 || length > 255)
  {
    return SP_ERROR_INVALID_INDATA;
  }

  playlist->name = strclone(new_name);
  return SP_ERROR_OK;
}

sp_error
sp_playlist_set_collaborative(sp_playlist *playlist, bool collaborative)
{
  playlist->is_collaborative = collaborative;
  return SP_ERROR_OK;
}

sp_error
sp_playlist_set_autolink_tracks(sp_playlist *playlist, bool autolink_tracks)
{
  playlist->autolink_tracks = autolink_tracks;
  return SP_ERROR_OK;
}

sp_error
sp_playlist_set_in_ram(sp_session *UNUSED(session), sp_playlist *playlist, bool in_ram)
{
  playlist->is_in_ram = in_ram;
  return SP_ERROR_OK;
}

sp_error
sp_playlist_set_offline_mode(sp_session *UNUSED(session), sp_playlist *playlist, bool offline_mode)
{
  playlist->get_offline_status = offline_mode ? SP_PLAYLIST_OFFLINE_STATUS_YES : SP_PLAYLIST_OFFLINE_STATUS_NO;
  return SP_ERROR_OK;
}

sp_error
sp_playlist_add_callbacks(sp_playlist *playlist, sp_playlist_callbacks *callbacks, void *userdata)
{
  playlist->callbacks = callbacks;
  playlist->userdata  = userdata;
  return SP_ERROR_OK;
}

sp_error
sp_playlist_remove_callbacks(sp_playlist *playlist, sp_playlist_callbacks *UNUSED(callbacks), void *UNUSED(userdata))
{
  playlist->callbacks = NULL;
  playlist->userdata  = NULL;
  return SP_ERROR_OK;
}

sp_error
sp_playlist_update_subscribers(sp_session *UNUSED(session), sp_playlist *playlist)
{
  if (playlist->callbacks && playlist->callbacks->subscribers_changed)
  {
    playlist->callbacks->subscribers_changed(playlist, playlist->userdata);
  }
  return SP_ERROR_OK;
}

sp_error
sp_playlist_add_tracks(sp_playlist *playlist, sp_track *const *tracks, int num_tracks, int position, sp_session *session)
{
  int size = sp_playlist_num_tracks(playlist);
  int new_size = size + num_tracks;
  int i, j, k;
  sp_playlist_track_t *new_tracks = NULL;

  if (position < 0 || position > size)
  {
    return SP_ERROR_INVALID_INDATA;
  }

  new_tracks = ALLOC_N(sp_playlist_track_t, new_size);

  for (i = 0, j = 0, k = 0; i < new_size; ++i)
  {
    if (i >= position && j < num_tracks)
    {
      new_tracks[i].track = tracks[j++];
      new_tracks[i].create_time = (int) time(NULL); // let’s hope before year 2038 we fix this :)
      new_tracks[i].creator = sp_session_user(session);
      new_tracks[i].message = NULL;
      new_tracks[i].seen = true;
    }
    else
    {
      MEMCPY(&new_tracks[i], &playlist->tracks[k++], sp_playlist_track_t);
    }
  }

  free(playlist->tracks);
  playlist->tracks = new_tracks;
  playlist->num_tracks = new_size;

  return SP_ERROR_OK;
}

sp_error
sp_playlist_remove_tracks(sp_playlist *playlist, const int *tracks, int num_tracks)
{
  int size     = sp_playlist_num_tracks(playlist);
  int new_size = size - num_tracks;
  int i = 0, j = 0, k = 0;
  sp_playlist_track_t *new_tracks = NULL;
  int *sorted_tracks = NULL;

  // Make sure all indices are unique and not too small/large
  for (i = 0; i < num_tracks; ++i)
  {
    if (tracks[i] < 0 || tracks[i] >= size)
      return SP_ERROR_INVALID_INDATA;

    for (j = i + 1; j < num_tracks; ++j)
    {
      if (tracks[i] == tracks[j])
        return SP_ERROR_INVALID_INDATA;
    }
  }

  new_tracks = ALLOC_N(sp_playlist_track_t, new_size);

  // this simplifies the remove operation quite a bit!
  sorted_tracks = ALLOC_N(int, num_tracks);
  MEMCPY_N(sorted_tracks, tracks, int, num_tracks);
  qsort(sorted_tracks, num_tracks, sizeof(int), compare_ints);

  for (i = 0, j = 0, k = 0; i < size; ++i)
  {
    if (sorted_tracks[j] == i)
    {
      j += 1;
      continue;
    }

    MEMCPY(&new_tracks[k++], &playlist->tracks[i], sp_playlist_track_t);
  }


  // we usually don’t do memory management, but in this case why not?
  free(sorted_tracks);
  free(playlist->tracks);
  playlist->tracks = new_tracks;
  playlist->num_tracks = new_size;

  return SP_ERROR_OK;
}

sp_error sp_playlist_reorder_tracks	(sp_playlist *playlist, const int *tracks, int num_tracks, int new_position)
{
  int i, j, k;
  int continues_from = new_position;
  int size = sp_playlist_num_tracks(playlist);
  int *sorted_tracks;
  sp_playlist_track_t *new_tracks;
  sp_playlist_track_t *from;
  sp_playlist_track_t *to;

  if (new_position > 0)
    new_position = new_position - 1;

  // Make sure all indices are unique and not too small/large
  for (i = 0; i < num_tracks; ++i)
  {
    if (tracks[i] < 0 || tracks[i] >= size)
      return SP_ERROR_INVALID_INDATA;

    for (j = i + 1; j < num_tracks; ++j)
    {
      if (tracks[i] == tracks[j])
        return SP_ERROR_INVALID_INDATA;
    }
  }

  new_tracks = ALLOC_N(sp_playlist_track_t, size);

  // this simplifies the move operation quite a bit!
  sorted_tracks = ALLOC_N(int, num_tracks);
  MEMCPY_N(sorted_tracks, tracks, int, num_tracks);
  qsort(sorted_tracks, num_tracks, sizeof(int), compare_ints);

  // Now, this is confusing! :D
  //
  // We keep three counters;
  //   i: item we are currently placing
  //   j: if we are moving, this is the index we are moving from
  //   k: if we are not moving, this is the index we should now place to
  for (i = 0, j = 0, k = 0; i < size; ++i)
  {
    if (i == tracks[j])
    {
      to   = &new_tracks[new_position + j];
      from = &playlist->tracks[i];
      j += 1;
    }
    else
    {
      to   = &new_tracks[k++];
      from = &playlist->tracks[i];

      if (k >= new_position && k < continues_from)
      {
        k = continues_from + 1;
      }
    }

    MEMCPY(to, from, sp_playlist_track_t);
  }

  free(sorted_tracks);
  free(playlist->tracks);
  playlist->tracks = new_tracks;

  return SP_ERROR_OK;
}
