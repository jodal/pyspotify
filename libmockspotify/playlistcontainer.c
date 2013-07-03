#include "libmockspotify.h"
#include "util.h"

static sp_error
mocksp_playlistcontainer_insert(sp_playlistcontainer *, int, sp_playlistcontainer_playlist_t);

static sp_error
mocksp_playlistcontainer_remove(sp_playlistcontainer *pc, int index);

static sp_playlistcontainer_playlist_t *
mocksp_playlistcontainer_find_playlist(sp_playlistcontainer *, sp_playlist *);

sp_playlistcontainer *
mocksp_playlistcontainer_create(sp_user *owner, bool loaded,
                                int num_playlists, sp_playlistcontainer_playlist_t *playlists,
                                sp_playlistcontainer_callbacks *callbacks, void *userdata)
{
  sp_playlistcontainer *container = ALLOC(sp_playlistcontainer);

  container->is_loaded = loaded;
  container->owner     = owner;

  container->num_playlists = num_playlists;
  container->playlists = ALLOC_N(sp_playlistcontainer_playlist_t, num_playlists);
  MEMCPY_N(container->playlists, playlists, sp_playlistcontainer_playlist_t, num_playlists);

  container->callbacks = callbacks;
  container->userdata  = userdata;

  return container;
}

DEFINE_REFCOUNTERS_FOR(playlistcontainer);

DEFINE_READER(playlistcontainer, is_loaded, bool);
DEFINE_READER(playlistcontainer, owner, sp_user *);
DEFINE_READER(playlistcontainer, num_playlists, int);
DEFINE_ARRAY_MEMBER_READER(playlistcontainer, playlist, playlist, sp_playlist *);
DEFINE_ARRAY_MEMBER_READER(playlistcontainer, playlist, type, sp_playlist_type);
DEFINE_ARRAY_MEMBER_READER(playlistcontainer, playlist, folder_id, sp_uint64);

sp_playlist *
sp_playlistcontainer_playlist(sp_playlistcontainer *pc, int index)
{
  return sp_playlistcontainer_playlist_playlist(pc, index);
}

sp_error
sp_playlistcontainer_playlist_folder_name(sp_playlistcontainer *pc, int index, char *buffer, int buffer_size)
{
  long null_byte_index = 0;

  if (index >= pc->num_playlists || index < 0)
  {
    return SP_ERROR_INDEX_OUT_OF_RANGE;
  }

  if (pc->playlists[index].folder_name)
  {
    strncpy(buffer, pc->playlists[index].folder_name, buffer_size);

    if ((unsigned int) buffer_size <= strlen(pc->playlists[index].folder_name))
    {
      null_byte_index = buffer_size - 1;
    }
    else
    {
      null_byte_index = strlen(pc->playlists[index].folder_name);
    }
  }

  buffer[null_byte_index] = '\0';

  return SP_ERROR_OK;
}

sp_error
sp_playlistcontainer_add_callbacks(sp_playlistcontainer *pc, sp_playlistcontainer_callbacks *callbacks, void *userdata)
{
  /* TODO: multi-callback support */
  pc->callbacks = callbacks;
  pc->userdata  = userdata;
  return SP_ERROR_OK;
}

sp_error
sp_playlistcontainer_remove_callbacks(sp_playlistcontainer *pc, sp_playlistcontainer_callbacks *UNUSED(callbacks), void *UNUSED(userdata)) 
{
  /* TODO: multi-callback support */
  pc->callbacks = NULL;
  pc->userdata  = NULL;
  return SP_ERROR_OK;
}

sp_playlist *
sp_playlistcontainer_add_new_playlist(sp_playlistcontainer *pc, const char *name)
{
  sp_playlist *playlist = mocksp_playlist_create(name, true, NULL, false, NULL, NULL, false, 0, NULL, true, SP_PLAYLIST_OFFLINE_STATUS_NO, 0, 0, NULL);

  sp_playlistcontainer_playlist_t container_playlist;
  container_playlist.playlist = playlist;
  container_playlist.type     = SP_PLAYLIST_TYPE_PLAYLIST;

  mocksp_playlistcontainer_insert(pc, sp_playlistcontainer_num_playlists(pc), container_playlist);

  return playlist;
}

sp_playlist *
sp_playlistcontainer_add_playlist(sp_playlistcontainer *pc, sp_link *link)
{
  sp_playlist *playlist = NULL;

  switch (sp_link_type(link))
  {
    case SP_LINKTYPE_PLAYLIST:
    case SP_LINKTYPE_STARRED:
      playlist = (sp_playlist *)registry_find(link->data);
      break;

    default: return NULL;
  }

  if (playlist)
  {
    sp_playlistcontainer_playlist_t container_playlist;

    container_playlist.playlist = playlist;
    container_playlist.type     = SP_PLAYLIST_TYPE_PLAYLIST;

    mocksp_playlistcontainer_insert(pc, sp_playlistcontainer_num_playlists(pc), container_playlist);
  }

  return playlist;
}

sp_error
sp_playlistcontainer_add_folder(sp_playlistcontainer *pc, int index, const char *name)
{
  sp_playlistcontainer_playlist_t start_folder;
  sp_playlistcontainer_playlist_t end_folder;
  sp_error error;
  long folder_id = random();

  start_folder.folder_id   = folder_id;
  start_folder.folder_name = strclone(name);
  start_folder.type        = SP_PLAYLIST_TYPE_START_FOLDER;

  end_folder.folder_id   = folder_id;
  end_folder.folder_name = NULL;
  end_folder.type        = SP_PLAYLIST_TYPE_END_FOLDER;

  error = mocksp_playlistcontainer_insert(pc, index, start_folder);

  if (error == SP_ERROR_OK)
  {
    error = mocksp_playlistcontainer_insert(pc, index + 1, end_folder);
  }

  return error;
}

sp_error
sp_playlistcontainer_remove_playlist(sp_playlistcontainer *pc, int index)
{
  sp_playlistcontainer_playlist_t *new_playlists;
  int num_playlists = sp_playlistcontainer_num_playlists(pc);
  int new_num_playlists = num_playlists - 1;
  int i, j;

  if (index >= num_playlists || index < 0)
  {
    return SP_ERROR_INDEX_OUT_OF_RANGE;
  }

  new_playlists = ALLOC_N(sp_playlistcontainer_playlist_t, new_num_playlists);
  for (i = 0, j = 0; i < num_playlists; ++i)
  {
    if (i != index)
    {
      MEMCPY(&new_playlists[j++], &pc->playlists[i], sp_playlistcontainer_playlist_t);
    }
  }

  free(pc->playlists);
  pc->playlists = new_playlists;
  pc->num_playlists = new_num_playlists;

  return SP_ERROR_OK;
}

sp_error
sp_playlistcontainer_move_playlist(sp_playlistcontainer *pc, int from, int to, bool dry_run)
{
  int num_playlists = sp_playlistcontainer_num_playlists(pc);
  sp_error error = SP_ERROR_OK;

  if (from >= num_playlists || from < 0 || to < 0 || to > num_playlists)
  {
    return SP_ERROR_INDEX_OUT_OF_RANGE;
  }

  if (from == to - 1)
  {
    return SP_ERROR_INVALID_INDATA; // don’t look at me, libspotify is strange
  }

  // TODO: error if moving folder into itself

  if ( ! dry_run)
  {
    sp_playlistcontainer_playlist_t playlist;
    MEMCPY(&playlist, &pc->playlists[from], sp_playlistcontainer_playlist_t);

    error |= mocksp_playlistcontainer_insert(pc, to, playlist);

    if (from > to)
    {
      from += 1;
    }

    error |= sp_playlistcontainer_remove_playlist(pc, from);
  }

  return error;
}

int
sp_playlistcontainer_get_unseen_tracks(sp_playlistcontainer *pc, sp_playlist *_playlist, sp_track **tracks, int num_tracks)
{
  sp_playlistcontainer_playlist_t *playlist = mocksp_playlistcontainer_find_playlist(pc, _playlist);
  bool seen = false;
  int unseen_count = 0, i = 0, j = 0;

  if ( ! playlist)
  {
    return -1;
  }

  for (i = 0; i < sp_playlist_num_tracks(_playlist); ++i)
  {
    sp_track *track = sp_playlist_track(_playlist, i);
    seen = false;

    if ( ! track)
    {
      continue;
    }

    for (j = 0; j < playlist->num_seen_tracks; ++j)
    {
      if (playlist->seen_tracks[j] == track)
      {
        seen = true;
      }
    }

    if ( ! seen)
    {
      if (unseen_count < num_tracks)
      {
        tracks[unseen_count] = track;
      }

      unseen_count += 1;
    }
  }

  return unseen_count;
}

int
sp_playlistcontainer_clear_unseen_tracks(sp_playlistcontainer *pc, sp_playlist *_playlist)
{
  sp_playlistcontainer_playlist_t *playlist = mocksp_playlistcontainer_find_playlist(pc, _playlist);
  int i = 0;

  if ( ! playlist)
  {
    return -1;
  }

  playlist->num_seen_tracks = 0;
  xfree(playlist->seen_tracks);

  playlist->num_seen_tracks = sp_playlist_num_tracks(_playlist);
  playlist->seen_tracks = ALLOC_N(sp_track *, playlist->num_seen_tracks);

  for (i = 0; i < playlist->num_seen_tracks; ++i)
  {
    playlist->seen_tracks[i] = sp_playlist_track(_playlist, i);
  }

  return 0;
}

/* UTILITY */
static sp_playlistcontainer_playlist_t *
mocksp_playlistcontainer_find_playlist(sp_playlistcontainer *pc, sp_playlist *_playlist)
{
  sp_playlistcontainer_playlist_t *playlist = NULL;
  sp_playlist *tmp = NULL;
  int i;

  for (i = 0; i < sp_playlistcontainer_num_playlists(pc); ++i)
  {
    tmp = sp_playlistcontainer_playlist(pc, i);
    if (tmp != NULL && _playlist == tmp)
    {
      *playlist = pc->playlists[i];
    }
  }

  return playlist;
}

static sp_error
mocksp_playlistcontainer_insert(sp_playlistcontainer *pc, int index, sp_playlistcontainer_playlist_t playlist)
{
  sp_playlistcontainer_playlist_t *new_playlists;
  int num_playlists = sp_playlistcontainer_num_playlists(pc);
  int new_num_playlists = num_playlists + 1;
  int i, j;

  if (index > num_playlists || index < 0)
  {
    return SP_ERROR_INDEX_OUT_OF_RANGE;
  }

  new_playlists = ALLOC_N(sp_playlistcontainer_playlist_t, new_num_playlists);
  for (i = 0, j = 0; i < new_num_playlists; i++)
  {
    if (i == index)
    {
      MEMCPY(&new_playlists[i], &playlist, sp_playlistcontainer_playlist_t);
    }
    else
    {
      MEMCPY(&new_playlists[i], &pc->playlists[j++], sp_playlistcontainer_playlist_t);
    }
  }

  free(pc->playlists);
  pc->playlists = new_playlists;
  pc->num_playlists = new_num_playlists;

  return SP_ERROR_OK;
}

/*
playlistcontainer_remove_playlist
playlistcontainer_move_playlist
*/
