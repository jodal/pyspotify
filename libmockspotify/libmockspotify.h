/*
 * API for libmockspotify
 *
 */

#ifndef LIBMOCKSPOTIFY_API_H
#define LIBMOCKSPOTIFY_API_H

#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include "libspotify/api.h"

/* custom type */
struct sp_player
{
  sp_track *track;
  int position;
  bool playing;
};
typedef struct sp_player sp_player;

struct sp_session
{
  char *username;
  sp_session_config config;
  void *userdata;
  sp_connectionstate connectionstate;
  size_t cache_size;

  sp_user *user;

  sp_player player;
  sp_bitrate preferred_bitrate;
  sp_connection_type connection_type;
  sp_connection_rules connection_rules;

  int offline_time_left;
  sp_offline_sync_status *offline_sync_status;
  int offline_num_playlists;
  int offline_tracks_to_sync;

  sp_playlist *inbox;

  bool volume_normalization;
};

struct sp_album
{
  char *name;
  sp_artist *artist;
  int year;
  byte *cover;
  int type;
  bool is_loaded;
  bool is_available;
};

struct sp_albumbrowse
{
  sp_error error;
  int backend_request_duration;

  sp_album *album;
  sp_artist *artist;

  int num_copyrights;
  char **copyrights;

  int num_tracks;
  sp_track **tracks;

  char *review;

  albumbrowse_complete_cb *callback;
  void *userdata;
};

struct sp_artist
{
  char *name;
  int is_loaded;
  byte *portrait;
};

struct sp_artistbrowse
{
  sp_error error;
  int backend_request_duration;
  sp_artist *artist;
  int num_portraits;
  byte **portraits;
  int num_tracks;
  sp_track **tracks;
  int num_albums;
  sp_album **albums;
  int num_similar_artists;
  sp_artist **similar_artists;
  int num_tophit_tracks;
  sp_track **tophit_tracks;
  char *biography;
  sp_artistbrowse_type type;

  artistbrowse_complete_cb *callback;
  void *userdata;
};

struct sp_image
{
  byte image_id[20];
  sp_imageformat format;
  size_t data_size;
  byte *data;
  sp_error error;

  image_loaded_cb *callback;
  void *userdata;
};

/* custom struct */
struct sp_playlist_track
{
  sp_track *track;
  int create_time;
  sp_user *creator;
  char *message;
  bool seen;
};
typedef struct sp_playlist_track sp_playlist_track_t;

struct sp_playlist
{
  char *name;
  bool is_loaded;
  sp_user *owner;
  bool is_collaborative;
  char *get_description;
  byte *image;
  bool has_pending_changes;
  int num_subscribers;
  sp_subscribers *subscribers;
  bool is_in_ram;
  sp_playlist_offline_status get_offline_status;
  int get_offline_download_completed;
  int num_tracks;

  sp_playlist_track_t *tracks;
  bool autolink_tracks;

  sp_playlist_callbacks *callbacks;
  void *userdata;
};

/* custom struct */
struct sp_playlistcontainer_playlist
{
  sp_playlist *playlist;
  sp_playlist_type type;
  char * folder_name;
  sp_uint64 folder_id;

  int num_seen_tracks;
  sp_track **seen_tracks;
};
typedef struct sp_playlistcontainer_playlist sp_playlistcontainer_playlist_t;

struct sp_playlistcontainer
{
  bool is_loaded;
  sp_user *owner;

  int num_playlists;
  sp_playlistcontainer_playlist_t *playlists;

  sp_playlistcontainer_callbacks *callbacks;
  void *userdata;
};

struct sp_search
{
  int total_tracks;
  int num_tracks;
  sp_track **tracks;

  int total_artists;
  int num_artists;
  sp_artist **artists;

  int total_albums;
  int num_albums;
  sp_album **albums;

  int total_playlists;
  int num_playlists;
  sp_playlist **playlists;

  char *query;
  char *did_you_mean;
  sp_search_type type;

  int error;

  search_complete_cb *callback;
  void *userdata;
};

struct sp_track
{
  char *name;
  int num_artists;
  sp_artist **artists;
  sp_album *album;
  int duration;
  int popularity;
  int disc;
  int index;
  sp_error error;

  bool is_loaded;
  bool is_placeholder;
  bool is_starred;
  bool is_local;
  bool is_autolinked;

  sp_track *get_playable;

  sp_track_availability availability;
  sp_track_offline_status offline_status;
};

struct sp_user
{
  char *canonical_name;
  char *display_name;
  bool is_loaded;
};

struct sp_link
{
  char *data;
};

struct sp_toplistbrowse
{
  sp_error error;
  int backend_request_duration;

  int num_artists;
  sp_artist **artists;

  int num_albums;
  sp_album **albums;

  int num_tracks;
  sp_track **tracks;

  toplistbrowse_complete_cb *callback;
  void *userdata;
};

struct sp_inbox
{
  char *user;
  char *message;
  sp_track *tracks;
  int num_tracks;

  inboxpost_complete_cb *callback;
  void *userdata;
};

/* Event types */
typedef enum event_type {
    // SESSION EVENTS
    MOCK_LOGGED_IN = 0,
    MOCK_LOGGED_OUT = 1,
    MOCK_METADATA_UPDATED = 2,
    MOCK_CONNECTION_ERROR = 3,

    // PLAYLIST EVENTS
    MOCK_PLAYLIST_TRACKS_ADDED = 20,
    MOCK_PLAYLIST_TRACKS_MOVED = 21,
    MOCK_PLAYLIST_TRACKS_REMOVED = 22,
    MOCK_PLAYLIST_RENAMED = 23,
    MOCK_PLAYLIST_STATE_CHANGED = 24,
    MOCK_PLAYLIST_UPDATE_IN_PROGRESS = 25,
    MOCK_PLAYLIST_METADATA_UPDATED = 26,
    MOCK_PLAYLIST_TRACK_CREATED_CHANGED = 27,
    MOCK_PLAYLIST_TRACK_MESSAGE_CHANGED = 28,
    MOCK_PLAYLIST_TRACK_SEEN_CHANGED = 29,
    MOCK_PLAYLIST_DESCRIPTION_CHANGED = 30,
    MOCK_PLAYLIST_SUBSCRIBERS_CHANGED = 31,
    MOCK_PLAYLIST_IMAGE_CHANGED = 32,

    // CONTAINER EVENTS
    MOCK_CONTAINER_LOADED = 40,
    MOCK_CONTAINER_PLAYLIST_ADDED = 41,
    MOCK_CONTAINER_PLAYLIST_MOVED = 42,
    MOCK_CONTAINER_PLAYLIST_REMOVED = 43
} event_type;

/* Event triggers */
void mocksp_event_playlist(event_type event, sp_playlist *p);
void mocksp_event_playlistcontainer(event_type event, sp_playlistcontainer *pc);

/* Registry utils */
void *
registry_find(const char *url);

void
registry_add(const char *url, void *ptr);

const char *
registry_reverse_find(void *);

void
registry_clean(void);

/* MockSpotify API */
sp_session *
mocksp_session_create(const sp_session_config *, sp_connectionstate, int, sp_offline_sync_status *, int, int, sp_playlist *);

sp_album *
mocksp_album_create(const char *, sp_artist *, int, const byte *, sp_albumtype, bool, bool);

sp_albumbrowse *
mocksp_albumbrowse_create(sp_error, int, sp_album *, sp_artist *, int, const char **, int, sp_track **, const char *, albumbrowse_complete_cb *cb, void *userdata);

sp_artist *
mocksp_artist_create(const char *, const byte *, bool);

sp_artistbrowse *
mocksp_artistbrowse_create(sp_error, int, sp_artist *, int, const byte **, int, sp_track **, int, sp_album **, int, sp_artist **, int, sp_track **, const char *, sp_artistbrowse_type, artistbrowse_complete_cb *, void *);

sp_playlist *
mocksp_playlist_create(const char *, bool, sp_user *, bool, const char *, const byte *, bool, unsigned int, sp_subscribers *, bool, sp_playlist_offline_status, int, int, sp_playlist_track_t *);

sp_subscribers *
mocksp_subscribers(int, char **);

sp_playlistcontainer *
mocksp_playlistcontainer_create(sp_user *, bool, int, sp_playlistcontainer_playlist_t *, sp_playlistcontainer_callbacks *, void *);

sp_track *
mocksp_track_create(const char *, int, sp_artist **, sp_album *, int, int, int, int, sp_error, bool, sp_track_availability, sp_track_offline_status, bool, bool, sp_track *, bool, bool);

sp_user *
mocksp_user_create(const char *, const char *, bool);

sp_image*
mocksp_image_create(const byte[20], sp_imageformat, size_t, const byte *, sp_error);

sp_toplistbrowse *
mocksp_toplistbrowse_create(sp_error, int, int, sp_artist **, int, sp_album **, int, sp_track **, toplistbrowse_complete_cb *, void *);

sp_search *
mocksp_search_create(sp_error, const char *, const char *, int, int, const sp_track **, int, int, const sp_album **, int, int, const sp_artist **, int, int, const sp_playlist **, search_complete_cb *, void *);

/* custom accessors for testing libmockspotify state */
bool
mocksp_playlist_get_autolink_tracks(sp_playlist *);

#endif /* LIBMOCKSPOTIFY_API_H */
