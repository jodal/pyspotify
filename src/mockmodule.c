/*
 * Provides mocking for the entire libspotify library.  All sp_ calls are
 * mocked here to provide something approximate to what libspotify would
 * provide.
 *
 * Functions for creating mock instances of all spotify objects are also
 * provided.
 *
*/
#include <Python.h>
#include <stdio.h>
#include <string.h>
#include <libspotify/api.h>
#include "pyspotify.h"
#include "album.h"
#include "albumbrowser.h"
#include "artist.h"
#include "artistbrowser.h"
#include "link.h"
#include "playlist.h"
#include "playlistcontainer.h"
#include "search.h"
#include "session.h"
#include "track.h"
#include "user.h"
#include "toplistbrowser.h"

/***************************** FORWARD DEFINES *****************************/
void mock_playlist_event(int event, sp_playlist * p);
void mock_playlistcontainer_event(int event, sp_playlistcontainer * pc);
sp_album *_mock_album(char *name, sp_artist * artist, int year, byte * cover,
                      int type, int loaded, int available);
sp_artist *_mock_artist(char *name, int loaded);
sp_track *_mock_track(char *name, int num_artists, sp_artist ** artists,
                      sp_album * album, int duration, int popularity,
                      int disc, int index, sp_error error, int loaded);
sp_playlistcontainer *_mock_playlistcontainer(void);
sp_playlist *_mock_playlist(char *name);
sp_albumbrowse *_mock_albumbrowse(sp_album * album, bool loaded);
sp_artistbrowse *_mock_artistbrowse(sp_artist * artist, bool loaded);
sp_user *_mock_user(char *canonical_name, char *display_name, char *full_name,
                    char *picture, sp_relation_type relation, bool loaded);

/****************************** GLOBALS ************************************/

PyObject *SpotifyError;
PyObject *SpotifyApiVersion;

/************************** MOCK DATA STRUCTURES **************************/

typedef struct {
    void *userdata;
    char username[1024];
    char password[1024];
    sp_session_config config;
    sp_playlist *starred;
    int bitrate;
} mocking_data;

mocking_data g_data;

struct sp_link {
    char data[1024];
};

struct sp_artist {
    char name[1024];
    int loaded;
};

struct sp_artistbrowse {
    sp_artist *artist;
    int loaded;
};

struct sp_album {
    char name[1024];
    sp_artist *artist;
    int year;
    byte cover[20];
    int type;
    int loaded;
    bool available;
};

struct sp_albumbrowse {
    sp_album *album;
    int loaded;
};

struct sp_playlist {
    char name[1024];
    sp_track *track[32];
    int num_tracks;
    sp_playlist_callbacks *callbacks;
    void *userdata;
};

struct sp_playlistcontainer {
    sp_playlist *playlist[32];
    int num_playlists;
    sp_playlistcontainer_callbacks *callbacks;
    void *userdata;
};

struct sp_track {
    char name[1024];
    int num_artists;
    sp_artist *artists[16];
    sp_album *album;
    int duration;
    int popularity;
    int disc;
    int index;
    sp_error error;
    int loaded;
    int starred;
};

struct sp_search {
    int loaded;
    int total_tracks;
    int num_tracks;
    int num_artists;
    int num_albums;
    sp_track *track[20];
    sp_album *album[20];
    sp_artist *artist[20];
    char *query;
    char *did_you_mean;
    int error;
};

struct sp_image {
    int error;
};

struct sp_user {
    bool loaded;
    char *canonical_name;
    char *display_name;
    char *full_name;
    char *picture;
    sp_relation_type relation;
};

struct sp_toplistbrowse {
    bool                loaded;
    sp_toplisttype      type;
    sp_toplistregion    region;
    sp_album            *albums[3];
    sp_artist           *artists[3];
    sp_track            *tracks[3];
};

/***************************** MOCK EVENT GENERATION ***************************/

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

event_type eventq[16];
int events = 0;

PyObject *
event_trigger(PyObject *self, PyObject *args)
{
    event_type event;
    PyObject *data = NULL;

    if (!PyArg_ParseTuple(args, "i|O", &event, &data))
        return NULL;
    if (20 <= event && event <= 39) {
        /* Playlist event */
        mock_playlist_event(event, ((Playlist *) data)->_playlist);
    }
    else if (40 <= event) {
        /* Container event */
        mock_playlistcontainer_event(event, ((PlaylistContainer *)
                                             data)->_playlistcontainer);
    }
    Py_RETURN_NONE;
}

/***************************** MOCK SESSION FUNCTIONS **************************/

void
sp_session_login(sp_session * session, const char *username,
                 const char *password)
{
    strcpy(g_data.username, username);
    strcpy(g_data.password, password);
    eventq[events++] = MOCK_LOGGED_IN;
}

void
sp_session_logout(sp_session * session)
{
    eventq[events++] = MOCK_LOGGED_OUT;
}

const char *
sp_error_message(sp_error error)
{
    char *buff;

    buff = malloc(128 * sizeof(char));
    sprintf(buff, "Error number %d", error);
    return buff;
}

sp_user *
sp_session_user(sp_session * session)
{
    return _mock_user(g_data.username, "", NULL, "", 0, 1);
}

sp_playlistcontainer *
sp_session_playlistcontainer(sp_session * session)
{
    return _mock_playlistcontainer();
}

sp_error
sp_session_create(const sp_session_config * config, sp_session ** sess)
{
    if (memcmp
        (config->application_key, "appkey_good", config->application_key_size))
        return SP_ERROR_BAD_APPLICATION_KEY;
    g_data.config.cache_location = malloc(strlen(config->cache_location) + 1);
    g_data.config.settings_location =
        malloc(strlen(config->settings_location) + 1);
    g_data.config.application_key = malloc(config->application_key_size);
    g_data.config.user_agent = malloc(strlen(config->user_agent) + 1);
    g_data.config.callbacks =
        (sp_session_callbacks *) malloc(sizeof(sp_session_callbacks));
    g_data.config.userdata = config->userdata;

    g_data.config.api_version = config->api_version;
    strcpy((char *)g_data.config.cache_location, config->cache_location);
    strcpy((char *)g_data.config.settings_location, config->settings_location);
    memcpy((char *)g_data.config.application_key, config->application_key,
           config->application_key_size);
    strcpy((char *)g_data.config.user_agent, config->user_agent);
    memcpy((char *)g_data.config.callbacks, config->callbacks,
           sizeof(sp_session_callbacks));
    g_data.config.userdata = config->userdata;
    return SP_ERROR_OK;
}

void *
sp_session_userdata(sp_session * session)
{
    return g_data.config.userdata;
}

void
sp_session_preferred_bitrate(sp_session * s, sp_bitrate b)
{
    // TODO
}

void
sp_session_process_events(sp_session * session, int *next_timeout)
{
    if (events > 0) {
        events--;
        event_type next = eventq[events];

        if (next == MOCK_LOGGED_IN) {
            g_data.config.callbacks->logged_in(session, SP_ERROR_OK);
        }
    }
    *next_timeout = 1;
}

sp_playlist *
sp_session_starred_create(sp_session * session)
{
    return _mock_playlist("Starred");
}

sp_error
sp_session_player_load(sp_session * session, sp_track * track)
{
    return 0;
}

void
sp_session_player_seek(sp_session * session, int offset)
{
}

void
sp_session_player_play(sp_session * session, bool b)
{
}

void
sp_session_player_unload(sp_session * session)
{
}

bool
sp_track_is_available(sp_session * session, sp_track * t)
{
    return 1;
}

int
sp_session_num_friends(sp_session *session)
{
    return 3;
}

sp_user *
sp_session_friend(sp_session *session, int index)
{
    char *names[3] = {"foo", "bar", "baz"};

    if (index > 3) return NULL;
    return _mock_user(names[index], names[index], names[index],
                      "1245678901234567890", 0, 1);
}

/********************************* MOCK SEARCH FUNCTIONS *********************************/

void
sp_search_add_ref(sp_search * search)
{
}

void
sp_search_release(sp_search * search)
{
}

sp_search *
sp_search_create(sp_session * session, const char *query, int track_offset,
                 int track_count, int album_offset, int album_count,
                 int artist_offset, int artist_count,
                 search_complete_cb * callback, void *userdata)
{
    sp_search *search = malloc(sizeof(sp_search));

    if (!strncmp(query, "!loaded", 7))
        search->loaded = 0;
    if (!strncmp(query, "loaded", 6))
        search->loaded = 1;
    search->num_tracks = 4;
    search->num_albums = 3;
    search->num_artists = 2;
    search->total_tracks = 24;
    search->query = malloc(strlen(query) + 1);
    strcpy(search->query, query);
    search->error = 3;
    search->did_you_mean = "did_you_mean";
    search->artist[0] = _mock_artist("foo", 1);
    search->artist[1] = _mock_artist("bar", 1);
    search->album[0] = _mock_album("baz", search->artist[0], 2001,
                                   (byte *) "01234567890123456789", 1, 1, 1);
    search->album[1] = _mock_album("qux", search->artist[1], 2002,
                                   (byte *) "01234567890123456789", 1, 1, 1);
    search->album[2] = _mock_album("quux", search->artist[0], 2003,
                                   (byte *) "01234567890123456789", 1, 1, 1);
    search->track[0] =
        _mock_track("corge", 1, search->artist, search->album[0], 99, 72, 1, 1,
                    0, 1);
    search->track[1] =
        _mock_track("grault", 1, search->artist, search->album[1], 98, 72, 1,
                    1, 0, 1);
    search->track[2] =
        _mock_track("garply", 1, search->artist, search->album[2], 97, 72, 1,
                    1, 0, 1);
    search->track[3] =
        _mock_track("waldo", 1, search->artist, search->album[0], 96, 72, 1, 1,
                    0, 1);
    callback(search, userdata);
    return search;
}

bool
sp_search_is_loaded(sp_search * s)
{
    return s->loaded;
}

int
sp_search_num_artists(sp_search * s)
{
    return s->num_artists;
}

int
sp_search_num_albums(sp_search * s)
{
    return s->num_albums;
}

int
sp_search_num_tracks(sp_search * s)
{
    return s->num_tracks;
}

int
sp_search_total_tracks(sp_search * s)
{
    return s->total_tracks;
}

sp_artist *
sp_search_artist(sp_search * s, int i)
{
    return s->artist[i];
}

sp_album *
sp_search_album(sp_search * s, int i)
{
    return s->album[i];
}

sp_track *
sp_search_track(sp_search * s, int i)
{
    return s->track[i];
}

const char *
sp_search_query(sp_search * s)
{
    return s->query;
}

sp_error
sp_search_error(sp_search * s)
{
    return s->error;
}

const char *
sp_search_did_you_mean(sp_search * s)
{
    return s->did_you_mean;
}

/********************************* MOCK USER FUNCTIONS ***********************************/

void
sp_user_add_ref(sp_user *user)
{
}

void
sp_user_release(sp_user *user)
{
}

bool
sp_user_is_loaded(sp_user *user)
{
    return user->loaded;
}

const char *
sp_user_canonical_name(sp_user *user)
{
    return user->canonical_name;
}

const char *
sp_user_display_name(sp_user *user)
{
    return user->display_name;
}

const char *
sp_user_full_name(sp_user *user)
{
    return user->loaded ? user->full_name : NULL;
}

const char *
sp_user_picture(sp_user *user)
{
    return user->loaded ? user->picture : NULL;
}

sp_relation_type
sp_user_relation_type(sp_session *session, sp_user *user)
{
    return user->relation;
}

/********************************* MOCK LINK FUNCTIONS ***********************************/

void
sp_link_add_ref(sp_link * link)
{
}

void
sp_link_release(sp_link * link)
{
}

sp_track *
sp_link_as_track(sp_link * link)
{
    if (strncmp(link->data, "link:track:", strlen("link:track:")))
        return NULL;
    sp_track *t = malloc(sizeof(sp_track));

    memset(t, 0, sizeof(sp_track));
    return _mock_track(link->data + strlen("link:track:"), 0, NULL, NULL, 0,
                       0, 0, 0, 0, 1);
    return t;
}

sp_artist *
sp_link_as_artist(sp_link * link)
{
    if (strncmp(link->data, "link:artist:", strlen("link:artist:")))
        return NULL;
    return _mock_artist(link->data + strlen("link:artist:"), 1);
}

sp_album *
sp_link_as_album(sp_link * link)
{
    if (strncmp(link->data, "link:album:", strlen("link:album:")))
        return NULL;
    return _mock_album(link->data + strlen("link:album:"),
                       _mock_artist("mock", 1), 1901, (byte *) "",
                       SP_ALBUMTYPE_ALBUM, 1, 1);
}

sp_link *
sp_link_create_from_track(sp_track * track, int offset)
{
    sp_link *l = malloc(sizeof(sp_link));

    memset(l, 0, sizeof(sp_link));
    sprintf(l->data, "link:track:%s/%d", track->name, offset);
    return l;
}

sp_link *
sp_link_create_from_album(sp_album * album)
{
    sp_link *l = malloc(sizeof(sp_link));

    memset(l, 0, sizeof(sp_link));
    sprintf(l->data, "link:album:%s", album->name);
    return l;
}

sp_link *
sp_link_create_from_playlist(sp_playlist * playlist)
{
    sp_link *l = malloc(sizeof(sp_link));

    memset(l, 0, sizeof(sp_link));
    sprintf(l->data, "link:playlist:%s", playlist->name);
    return l;
}

sp_link *
sp_link_create_from_artist(sp_artist * artist)
{
    sp_link *l = malloc(sizeof(sp_link));

    memset(l, 0, sizeof(sp_link));
    sprintf(l->data, "link:artist:%s", artist->name);
    return l;
}

sp_link *
sp_link_create_from_search(sp_search * s)
{
    sp_link *l = malloc(sizeof(sp_link));

    memset(l, 0, sizeof(sp_link));
    sprintf(l->data, "link:search:%s", s->query);
    return l;
}

sp_link *
sp_link_create_from_string(const char *link)
{
    sp_link *l = malloc(sizeof(sp_link));

    memset(l, 0, sizeof(sp_link));
    sprintf(l->data, "link:%s", link);
    return l;
}

int
sp_link_as_string(sp_link * link, char *buffer, int buffer_size)
{
    strncpy(buffer, link->data, buffer_size);
    return strlen(link->data);
}

sp_linktype
sp_link_type(sp_link * link)
{
    return 1;
}

/*************** MOCK TRACK METHODS ************************/

bool
sp_track_is_loaded(sp_track * t)
{
    return t->loaded;
}

const char *
sp_track_name(sp_track * track)
{
    return track->name;
}

int
sp_track_num_artists(sp_track * t)
{
    return 3;
}

sp_artist *
sp_track_artist(sp_track * t, int index)
{
    static sp_artist *a[3];

    a[0] = _mock_artist("a1", 1);
    a[1] = _mock_artist("a2", 1);
    a[2] = _mock_artist("a3", 1);
    return a[index];
}

int
sp_track_disc(sp_track * t)
{
    return t->disc;
}

int
sp_track_index(sp_track * t)
{
    return t->index;
}

int
sp_track_popularity(sp_track * t)
{
    return t->popularity;
}

int
sp_track_duration(sp_track * t)
{
    return t->duration;
}

sp_error
sp_track_error(sp_track * t)
{
    return t->error;
}

sp_album *
sp_track_album(sp_track * t)
{
    return t->album;
}

bool
sp_track_is_local(sp_session * s, sp_track * t)
{
    return 0;
}

bool
sp_track_is_starred(sp_session * s, sp_track * t)
{
    return t->starred;
}

void
sp_track_set_starred(sp_session * s, const sp_track ** ts, int n, bool starred)
{
    int i;

    for (i = 0; i < n; i++)
        ((sp_track *) ts[i])->starred = starred;
}

void
sp_track_add_ref(sp_track * track)
{
}

void
sp_track_release(sp_track * track)
{
}

/*************** MOCK ARTIST METHODS **********************/

void
sp_artist_add_ref(sp_artist * a)
{
}

const char *
sp_artist_name(sp_artist * a)
{
    return a->name;
}

bool
sp_artist_is_loaded(sp_artist * a)
{
    return a->loaded;
}

void
sp_artist_release(sp_artist * a)
{
}

/**************** MOCK PLAYLIST METHODS *****************/

void
sp_playlist_add_ref(sp_playlist * p)
{
}

void
sp_playlist_release(sp_playlist * p)
{
}

void
sp_playlist_set_autolink_tracks(sp_playlist *p, bool set)
{
}

bool
sp_playlist_is_loaded(sp_playlist * p)
{
    return 1;
}

const char *
sp_playlist_name(sp_playlist * p)
{
    return p->name;
}

sp_error
sp_playlist_rename(sp_playlist *p, const char *new_name)
{
    strcpy(p->name, new_name);
    return SP_ERROR_OK;
}

sp_track *
sp_playlist_track(sp_playlist * p, int index)
{
    return p->track[index];
}

int
sp_playlist_num_tracks(sp_playlist * p)
{
    return p->num_tracks;
}

void
sp_playlist_add_callbacks(sp_playlist * p, sp_playlist_callbacks * cb,
                          void *userdata)
{
    p->callbacks = cb;
    p->userdata = userdata;
}

void
sp_playlist_remove_callbacks(sp_playlist * p, sp_playlist_callbacks * cb,
                             void *userdata)
{
    p->callbacks = NULL;
}

bool
sp_playlist_is_collaborative(sp_playlist * p)
{
    return 0;
}

sp_error
sp_playlist_add_tracks(sp_playlist *p, const sp_track **tracks, int num_tracks,
                       int position, sp_session *session) {
    if (position > p->num_tracks - 1)
        return SP_ERROR_INVALID_INDATA;
    return SP_ERROR_OK;
};

sp_error
sp_playlist_remove_tracks(sp_playlist * p, const int *tracks, int num_tracks)
{
    // TODO
    return SP_ERROR_OK;
}

void
mock_playlist_event(int event, sp_playlist * p)
{
    sp_artist *artist = _mock_artist("foo_", 1);
    sp_album *album = _mock_album("bar_", artist, 2011,
                                  (byte *) "01234567890123456789", 0, 1, 1);
    sp_user *user = _mock_user("foo", "", "", "", 0, 0);
    sp_track *tracks[3] = {
        _mock_track("foo", 1, &artist, album, 0, 0, 0, 0, 0, 1),
        _mock_track("bar", 1, &artist, album, 0, 0, 0, 0, 0, 1),
        _mock_track("baz", 1, &artist, album, 0, 0, 0, 0, 0, 1)
    };
    int nums[3] = { 0, 1, 2 };

    switch (event) {
    case MOCK_PLAYLIST_TRACKS_ADDED:
        if (p->callbacks->tracks_added)
            p->callbacks->tracks_added(p, tracks, 3, 0, p->userdata);
        break;
    case MOCK_PLAYLIST_TRACKS_MOVED:
        if (p->callbacks->tracks_moved)
            p->callbacks->tracks_moved(p, nums, 3, 0, p->userdata);
        break;
    case MOCK_PLAYLIST_TRACKS_REMOVED:
        if (p->callbacks->tracks_removed)
            p->callbacks->tracks_removed(p, nums, 3, p->userdata);
        break;

    case MOCK_PLAYLIST_RENAMED:
        if (p->callbacks->playlist_renamed)
            p->callbacks->playlist_renamed(p, p->userdata);
        break;

    case MOCK_PLAYLIST_STATE_CHANGED:
        if (p->callbacks->playlist_state_changed)
            p->callbacks->playlist_state_changed(p, p->userdata);
        break;

    case MOCK_PLAYLIST_UPDATE_IN_PROGRESS:
        if (p->callbacks->playlist_update_in_progress)
            p->callbacks->playlist_update_in_progress(p, 1, p->userdata);
        break;

    case MOCK_PLAYLIST_METADATA_UPDATED:
        if (p->callbacks->playlist_metadata_updated)
            p->callbacks->playlist_metadata_updated(p, p->userdata);
        break;

    case MOCK_PLAYLIST_TRACK_CREATED_CHANGED:
        if (p->callbacks->track_created_changed)
            p->callbacks->track_created_changed(p, 1, user, 123, p->userdata);
        break;

    case MOCK_PLAYLIST_TRACK_MESSAGE_CHANGED:
        if (p->callbacks->track_message_changed)
            p->callbacks->track_message_changed(p, 1, "foo", p->userdata);
        break;

    case MOCK_PLAYLIST_TRACK_SEEN_CHANGED:
        if (p->callbacks->track_seen_changed)
            p->callbacks->track_seen_changed(p, 1, 0, p->userdata);
        break;

    case MOCK_PLAYLIST_DESCRIPTION_CHANGED:
        if (p->callbacks->description_changed)
            p->callbacks->description_changed(p, "foo", p->userdata);
        break;

    case MOCK_PLAYLIST_SUBSCRIBERS_CHANGED:
        if (p->callbacks->subscribers_changed)
            p->callbacks->subscribers_changed(p, p->userdata);
        break;

    case MOCK_PLAYLIST_IMAGE_CHANGED:
        if (p->callbacks->image_changed)
            p->callbacks->image_changed(p, (byte *) "01234567890123456789",
                                        p->userdata);
        break;

    default:
        break;
    }
}

/********************* MOCK PLAYLIST CONTAINER METHODS ************/

void
sp_playlistcontainer_add_ref(sp_playlistcontainer * p)
{
}

void
sp_playlistcontainer_release(sp_playlistcontainer * p)
{
}

bool
sp_playlistcontainer_is_loaded(sp_playlistcontainer *p)
{
    return 1;
}

sp_playlist *
sp_playlistcontainer_playlist(sp_playlistcontainer * pc, int index)
{
    return pc->playlist[index];
}

int
sp_playlistcontainer_num_playlists(sp_playlistcontainer * pc)
{
    return pc->num_playlists;
}

sp_playlist *
sp_playlistcontainer_add_playlist(sp_playlistcontainer *pc, sp_link *link)
{
    // TODO
    return NULL;
}

sp_playlist *
sp_playlistcontainer_add_new_playlist(sp_playlistcontainer *pc,
                                      const char *name)
{
    return _mock_playlist((char *)name);
}

void
sp_playlistcontainer_add_callbacks(sp_playlistcontainer * pc,
                                   sp_playlistcontainer_callbacks * cb,
                                   void *userdata)
{
    pc->callbacks = cb;
    pc->userdata = userdata;
}

void
mock_playlistcontainer_event(int event, sp_playlistcontainer * c)
{
    sp_playlist *playlist = _mock_playlist("foo");

    switch (event) {
    case MOCK_CONTAINER_LOADED:
        if (c->callbacks->container_loaded)
            c->callbacks->container_loaded(c, c->userdata);
        break;
    case MOCK_CONTAINER_PLAYLIST_ADDED:
        if (c->callbacks->playlist_added)
            c->callbacks->playlist_added(c, playlist, 0, c->userdata);
        break;
    case MOCK_CONTAINER_PLAYLIST_MOVED:
        if (c->callbacks->playlist_moved)
            c->callbacks->playlist_moved(c, playlist, 0, 1, c->userdata);
        break;
    case MOCK_CONTAINER_PLAYLIST_REMOVED:
        if (c->callbacks->playlist_removed)
            c->callbacks->playlist_removed(c, playlist, 0, c->userdata);
        break;
    default:
        break;
    }
}

/*********************** MOCK IMAGE METHODS ************************/

void
sp_image_add_ref(sp_image * image)
{
}

void
sp_image_release(sp_image * image)
{
}

bool
sp_image_is_loaded(sp_image * i)
{
    return 1;
}

sp_imageformat
sp_image_format(sp_image * i)
{
    return 1;
}

sp_error
sp_image_error(sp_image * i)
{
    return 0;
}

const void *
sp_image_data(sp_image * i, size_t * t)
{
    return NULL;
}

sp_image *
sp_image_create(sp_session * session, const byte image_id[20])
{
    return NULL;
}

void
sp_image_add_load_callback(sp_image * i, image_loaded_cb * callback,
                           void *userdata)
{
}

void
sp_image_remove_load_callback(sp_image * i, image_loaded_cb * callback,
                              void *userdata)
{
}

/*********************** MOCK ALBUM METHODS ************************/

void
sp_album_add_ref(sp_album * a)
{
}

void
sp_album_release(sp_album * a)
{
}

bool
sp_album_is_loaded(sp_album * a)
{
    return a->loaded;
}

bool
sp_album_is_available(sp_album * a)
{
    return a->available;
}

sp_artist *
sp_album_artist(sp_album * a)
{
    return a->artist;
}

const byte *
sp_album_cover(sp_album * a)
{
    return a->cover;
}

const char *
sp_album_name(sp_album * a)
{
    return a->name;
}

int
sp_album_year(sp_album * a)
{
    return a->year;
}

sp_albumtype
sp_album_type(sp_album * a)
{
    return a->type;
}

/**************** MOCK ALBUM BROWSING ******************/

void
sp_albumbrowse_add_ref(sp_albumbrowse * ab)
{
}

void
sp_albumbrowse_release(sp_albumbrowse * ab)
{
}

sp_track *
sp_albumbrowse_track(sp_albumbrowse * ab, int index)
{
    sp_track *track;

    switch (index) {
    case 0:
        track = _mock_track("foo", 1, &(ab->album->artist), ab->album,
                            123, 0, 1, 1, SP_ERROR_OK, 1);
        break;
    case 1:
        track = _mock_track("bar", 1, &(ab->album->artist), ab->album,
                            123, 0, 1, 2, SP_ERROR_OK, 1);
        break;
    case 2:
        track = _mock_track("baz", 1, &(ab->album->artist), ab->album,
                            123, 0, 1, 3, SP_ERROR_OK, 1);
        break;
    default:
        track = NULL;
        break;
    }
    return track;
}

int
sp_albumbrowse_num_tracks(sp_albumbrowse * ab)
{
    return 3;
}

bool
sp_albumbrowse_is_loaded(sp_albumbrowse * ab)
{
    return ab->loaded;
}

sp_albumbrowse *
sp_albumbrowse_create(sp_session * s, sp_album * a,
                      albumbrowse_complete_cb cb, void *userdata)
{
    sp_albumbrowse *ab;

    ab = _mock_albumbrowse(a, 1);
    if (cb)
        cb(ab, userdata);
    return ab;
}

/**************** MOCK ARTIST BROWSING *****************/

void
sp_artistbrowse_add_ref(sp_artistbrowse * ab)
{
}

void
sp_artistbrowse_release(sp_artistbrowse * ab)
{
}

sp_artistbrowse *
sp_artistbrowse_create(sp_session * s, sp_artist * a,
                       artistbrowse_complete_cb cb, void *userdata)
{
    sp_artistbrowse *ab;

    ab = _mock_artistbrowse(a, 1);
    if (cb)
        cb(ab, userdata);
    return ab;
}

sp_track *
sp_artistbrowse_track(sp_artistbrowse * ab, int index)
{
    sp_album *album;
    sp_track *track;

    album = _mock_album("fool-album", ab->artist, 2001,
                        (byte *) "01234567890123456789", 1, 1, 1);
    switch (index) {
    case 0:
        track = _mock_track("foo", 1, &(album->artist), album,
                            123, 0, 1, 1, SP_ERROR_OK, 1);
        break;
    case 1:
        track = _mock_track("bar", 1, &(album->artist), album,
                            123, 0, 1, 2, SP_ERROR_OK, 1);
        break;
    case 2:
        track = _mock_track("baz", 1, &(album->artist), album,
                            123, 0, 1, 3, SP_ERROR_OK, 1);
        break;
    default:
        track = NULL;
        break;
    }
    return track;
}

sp_album *
sp_artistbrowse_album(sp_artistbrowse * ab, int index)
{
    sp_album *album;

    switch (index) {
    case 0:
        album = _mock_album("foo", ab->artist, 2001,
                            (byte *) "01234567890123456789", 1, 1, 1);
        break;
    case 1:
        album = _mock_album("bar", ab->artist, 2002,
                            (byte *) "01234567890123456789", 1, 1, 1);
        break;
    case 2:
        album = _mock_album("baz", ab->artist, 2003,
                            (byte *) "01234567890123456789", 1, 1, 1);
        break;
    default:
        album = NULL;
        break;
    }
    return album;
}

int
sp_artistbrowse_num_albums(sp_artistbrowse * ab)
{
    return 3;
}

int
sp_artistbrowse_num_tracks(sp_artistbrowse * ab)
{
    return 3;
}

bool
sp_artistbrowse_is_loaded(sp_artistbrowse * ab)
{
    return ab->loaded;
}


/**************** MOCK TOPLIST BROWSING ****************/
void
sp_toplistbrowse_add_ref(sp_toplistbrowse *tb)
{
}

void
sp_toplistbrowse_release(sp_toplistbrowse *tb)
{
}

bool
sp_toplistbrowse_is_loaded(sp_toplistbrowse *tb)
{
    return tb->loaded;
}

sp_error
sp_toplistbrowse_error(sp_toplistbrowse *tb)
{
    return SP_ERROR_OK;
}

int
sp_toplistbrowse_num_albums(sp_toplistbrowse *tb)
{
    return tb->type == SP_TOPLIST_TYPE_ALBUMS ? 3 : 0;
}

int
sp_toplistbrowse_num_artists(sp_toplistbrowse *tb)
{
    return tb->type == SP_TOPLIST_TYPE_ARTISTS ? 3 : 0;
}

int
sp_toplistbrowse_num_tracks(sp_toplistbrowse *tb)
{
    return tb->type == SP_TOPLIST_TYPE_TRACKS ? 3 : 0;
}

sp_album *
sp_toplistbrowse_album(sp_toplistbrowse *tb, int index)
{
    return tb->albums[index];
}

sp_artist *
sp_toplistbrowse_artist(sp_toplistbrowse *tb, int index)
{
    return tb->artists[index];
}

sp_track *
sp_toplistbrowse_track(sp_toplistbrowse *tb, int index)
{
    return tb->tracks[index];
}

sp_toplistbrowse *
sp_toplistbrowse_create(sp_session *session,
                        sp_toplisttype type, sp_toplistregion region,
                        const char* username,
                        toplistbrowse_complete_cb *cb, void *userdata)
{
    sp_toplistbrowse *tb;

    tb = (sp_toplistbrowse *)PyMem_Malloc(sizeof(struct sp_toplistbrowse));
    tb->albums[0] = _mock_album("foo", NULL, 2001,
                                    (byte *) "01234567890123456789", 1, 1, 1);
    tb->albums[1] = _mock_album("bar", NULL, 2001,
                                    (byte *) "01234567890123456789", 1, 1, 1);
    tb->albums[2] = _mock_album("baz", NULL, 2001,
                                    (byte *) "01234567890123456789", 1, 1, 1);
    tb->artists[0] = _mock_artist("foo", 1);
    tb->artists[1] = _mock_artist("bar", 1);
    tb->artists[2] = _mock_artist("baz", 1);
    tb->tracks[0] = _mock_track("foo", 1, NULL, NULL, 5, 0, 1, 1,
                                                                SP_ERROR_OK, 1);
    tb->tracks[1] = _mock_track("bar", 1, NULL, NULL, 5, 0, 1, 1,
                                                                SP_ERROR_OK, 1);
    tb->tracks[2] = _mock_track("baz", 1, NULL, NULL, 5, 0, 1, 1,
                                                                SP_ERROR_OK, 1);
    tb->type = type;
    tb->region = region;
    tb->loaded = 1;
    cb(tb, userdata);
    return tb;
}


/**************** MOCKING NEW OBJECTS *******************/

/// Generate a mock sp_user structure
sp_user *_mock_user(char *canonical_name, char *display_name, char *full_name,
                    char *picture, sp_relation_type relation, bool loaded)
{
    sp_user *user;

    user = malloc(sizeof(sp_user));
    user->canonical_name = canonical_name;
    user->display_name = display_name;
    user->full_name = full_name;
    user->picture = picture;
    user->relation = relation;
    user->loaded = loaded;

    return user;
}

/// Generate a mock spotify.User object
PyObject *
mock_user(PyObject *self, PyObject *args)
{
    char *canonical_name, *display_name, *full_name, *picture;
    int relation;
    int loaded;
    sp_user *user;

    if (!PyArg_ParseTuple(args, "esesesesii", ENCODING, &canonical_name,
                          ENCODING, &display_name, ENCODING, &full_name,
                          ENCODING, &picture, &relation, &loaded))
        return NULL;

    user = _mock_user(canonical_name, display_name, full_name, picture,
                      relation, loaded);
    return User_FromSpotify(user);
}

/// Generate a mock sp_albumbrowse structure
sp_albumbrowse *
_mock_albumbrowse(sp_album * album, bool loaded)
{
    sp_albumbrowse *ab;

    ab = malloc(sizeof(sp_albumbrowse));
    ab->loaded = loaded;
    ab->album = album;
    return ab;
}

/// Generate a mock spotify.Albumbrowse object
PyObject *
mock_albumbrowse(PyObject *self, PyObject *args, PyObject *kwds)
{
    AlbumBrowser *ab;
    int loaded;
    PyObject *session, *album, *callback, *userdata = NULL;
    PyObject *new_args;
    static char *kwlist[] =
        { "session", "album", "loaded", "callback", "userdata", NULL };

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!O!iO|O", kwlist,
                                     &SessionType, &session,
                                     &AlbumType, &album, &loaded,
                                     &callback, &userdata))
        return NULL;
    if (!userdata) {
        userdata = Py_None;
        Py_INCREF(Py_None);
    }
    new_args = PyTuple_New(4);
    PyTuple_SetItem(new_args, 0, session);
    PyTuple_SetItem(new_args, 1, album);
    PyTuple_SetItem(new_args, 2, callback);
    PyTuple_SetItem(new_args, 3, userdata);
    ab = (AlbumBrowser *) PyObject_Call((PyObject *)&AlbumBrowserType,
                                        new_args, NULL);
    ab->_browser->loaded = loaded;
    return (PyObject *)ab;
}

/// Generate a mock sp_artistbrowse structure
sp_artistbrowse *
_mock_artistbrowse(sp_artist * artist, bool loaded)
{
    sp_artistbrowse *ab;

    ab = malloc(sizeof(sp_artistbrowse));
    ab->loaded = loaded;
    ab->artist = artist;
    return ab;
}

/// Generate a mock spotify.Artistbrowse object
PyObject *
mock_artistbrowse(PyObject *self, PyObject *args, PyObject *kwds)
{
    ArtistBrowser *ab;
    int loaded;
    PyObject *session, *artist, *callback, *userdata = NULL;
    PyObject *new_args;
    static char *kwlist[] =
        { "session", "artist", "loaded", "callback", "userdata", NULL };

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!O!iO|O", kwlist,
                                     &SessionType, &session,
                                     &ArtistType, &artist, &loaded,
                                     &callback, &userdata))
        return NULL;
    if (!userdata) {
        userdata = Py_None;
        Py_INCREF(Py_None);
    }
    new_args = PyTuple_New(4);
    PyTuple_SetItem(new_args, 0, session);
    PyTuple_SetItem(new_args, 1, artist);
    PyTuple_SetItem(new_args, 2, callback);
    PyTuple_SetItem(new_args, 3, userdata);
    ab = (ArtistBrowser *) PyObject_Call((PyObject *)&ArtistBrowserType,
                                         new_args, NULL);
    ab->_browser->loaded = loaded;
    return (PyObject *)ab;
}

/// Generate a mock sp_artist structure
sp_artist *
_mock_artist(char *name, int loaded)
{
    sp_artist *a;

    a = malloc(sizeof(sp_artist));
    memset(a, 0, sizeof(sp_artist));
    strcpy(a->name, name);
    a->loaded = loaded;
    return a;
}

/// Generate a mock spotify.Artist python object
PyObject *
mock_artist(PyObject *self, PyObject *args)
{
    char *s;
    int loaded;

    if (!PyArg_ParseTuple(args, "esi", ENCODING, &s, &loaded))
        return NULL;
    Artist *artist =
        (Artist *) PyObject_CallObject((PyObject *)&ArtistType, NULL);
    if (!artist)
        return NULL;
    Py_INCREF(artist);
    artist->_artist = _mock_artist(s, loaded);
    return (PyObject *)artist;
}

/// Generate a mock sp_track structure
sp_track *
_mock_track(char *name, int num_artists, sp_artist ** artists,
            sp_album * album, int duration, int popularity,
            int disc, int index, sp_error error, int loaded)
{
    sp_track *t;

    t = malloc(sizeof(sp_track));
    memset(t, 0, sizeof(sp_track));
    strcpy(t->name, name);
    t->loaded = loaded;
    t->disc = disc;
    t->index = index;
    t->error = error;
    t->duration = duration;
    t->popularity = popularity;
    t->album = album;
    t->starred = 0;
    return t;
}

PyObject *
mock_track(PyObject *self, PyObject *args)
{
    char *name;
    int num_artists;

    //sp_artist **artists;
    Album *album;
    int duration;
    int popularity;
    int disc;
    int index;
    sp_error error;
    int loaded;

    if (!PyArg_ParseTuple
        (args, "esiO!iiiiii", ENCODING, &name, &num_artists, &AlbumType,
         &album, &duration, &popularity, &disc, &index, &error, &loaded))
        return NULL;
    sp_track *t = _mock_track(name, num_artists, NULL, album->_album, duration,
                              popularity,
                              disc, index, error, loaded);
    Track *track = (Track *) PyObject_CallObject((PyObject *)&TrackType, NULL);

    track->_track = t;
    Py_INCREF(track);
    return (PyObject *)track;
}

sp_album *
_mock_album(char *name, sp_artist * artist, int year, byte * cover,
            int type, int loaded, int available)
{
    sp_album *a;

    a = malloc(sizeof(sp_album));
    memset(a, 0, sizeof(sp_album));
    strcpy(a->name, name);
    a->artist = artist;
    a->year = year;
    memcpy(a->cover, cover, 20);
    a->type = type;
    a->loaded = loaded;
    a->available = available;
    return a;
}

PyObject *
mock_album(PyObject *self, PyObject *args)
{
    Artist *artist;
    byte *cover;
    char *name;
    int year, type, loaded, available;

    if (!PyArg_ParseTuple(args, "esO!isiii", ENCODING, &name, &ArtistType,
                          &artist, &year, &cover, &type, &loaded, &available))
        return NULL;
    Album *album = (Album *) PyObject_CallObject((PyObject *)&AlbumType, NULL);

    album->_album =
        _mock_album(name, artist->_artist, year, cover, type, loaded,
                    available);
    return (PyObject *)album;
}

sp_playlist *
_mock_playlist(char *name)
{
    sp_playlist *p;

    p = malloc(sizeof(sp_playlist));
    memset(p, 0, sizeof(sp_playlist));
    strcpy(p->name, name);
    return p;
}

PyObject *
mock_playlist(PyObject *self, PyObject *args)
{
    char *s;
    int i;
    PyObject *tracks;

    if (!PyArg_ParseTuple(args, "esO", ENCODING, &s, &tracks))
        return NULL;
    Playlist *playlist =
        (Playlist *) PyObject_CallObject((PyObject *)&PlaylistType, NULL);
    if (!playlist)
        return NULL;
    Py_INCREF(playlist);
    playlist->_playlist = _mock_playlist(s);
    for (i = 0; i < PySequence_Length(tracks); i++) {
        Track *t = (Track *) PySequence_GetItem(tracks, i);

        Py_INCREF(t);
        playlist->_playlist->track[playlist->_playlist->num_tracks++] =
            t->_track;
    }
    return (PyObject *)playlist;
}

sp_playlistcontainer *
_mock_playlistcontainer(void)
{
    sp_playlistcontainer *pc;

    pc = malloc(sizeof(sp_playlistcontainer));
    memset(pc, 0, sizeof(sp_playlistcontainer));
    return pc;
}

PyObject *
mock_playlistcontainer(PyObject *self, PyObject *args)
{
    PyObject *seq;

    if (!PyArg_ParseTuple(args, "O", &seq))
        return NULL;
    PlaylistContainer *pc =
        (PlaylistContainer *) PyObject_CallObject((PyObject *)
                                                  &PlaylistContainerType,
                                                  NULL);

    pc->_playlistcontainer = _mock_playlistcontainer();
    int len = PySequence_Length(seq);
    int i;

    for (i = 0; i < len; ++i) {
        Playlist *item = (Playlist *) PySequence_GetItem(seq, i);

        Py_INCREF(item);
        pc->_playlistcontainer->playlist[pc->
                                         _playlistcontainer->num_playlists++] =
            item->_playlist;
    }
    return (PyObject *)pc;
}

PyObject *
mock_search(PyObject *self, PyObject *args)
{
    sp_search *s;

    s = malloc(sizeof(sp_search));
    s->query = "query";
    Results *results =
        (Results *) PyObject_CallObject((PyObject *)&ResultsType, NULL);
    results->_search = s;
    Py_INCREF(results);
    return (PyObject *)results;
}

PyObject *
mock_session(PyObject *self, PyObject *args)
{
    Session *session =
        (Session *) PyObject_CallObject((PyObject *)&SessionType, NULL);
    Py_INCREF(session);
    return (PyObject *)session;
}

/**************************** MODULE INITIALISATION ********************************/

static PyMethodDef module_methods[] = {
    {"connect", session_connect, METH_VARARGS,
     "Run the spotify subsystem.  this will return on error, or after spotify is logged out."},
    {"mock_track", mock_track, METH_VARARGS, "Create a mock track"},
    {"mock_album", mock_album, METH_VARARGS, "Create a mock album"},
    {"mock_albumbrowse", (PyCFunction)mock_albumbrowse,
     METH_VARARGS | METH_KEYWORDS, "Create a mock album browser"},
    {"mock_artist", mock_artist, METH_VARARGS, "Create a mock artist"},
    {"mock_artistbrowse", (PyCFunction)mock_artistbrowse,
     METH_VARARGS | METH_KEYWORDS, "Create a mock artist browser"},
    {"mock_playlist", mock_playlist, METH_VARARGS, "Create a mock playlist"},
    {"mock_playlistcontainer", mock_playlistcontainer, METH_VARARGS,
     "Create a mock playlist container"},
    {"mock_search", mock_search, METH_VARARGS, "Create mock search results"},
    {"mock_session", mock_session, METH_VARARGS, "Create a mock session"},
    {"mock_event_trigger", event_trigger, METH_VARARGS, "Triggers an event"},
    {"mock_user", mock_user, METH_VARARGS, "Create a mock user."},
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC
init_mockspotify(void)
{
    PyObject *m;

    if (PyType_Ready(&SessionType) < 0)
        return;
    if (PyType_Ready(&AlbumType) < 0)
        return;
    if (PyType_Ready(&AlbumBrowserType) < 0)
        return;
    if (PyType_Ready(&ArtistType) < 0)
        return;
    if (PyType_Ready(&ArtistBrowserType) < 0)
        return;
    if (PyType_Ready(&LinkType) < 0)
        return;
    if (PyType_Ready(&PlaylistType) < 0)
        return;
    if (PyType_Ready(&PlaylistContainerType) < 0)
        return;
    if (PyType_Ready(&ResultsType) < 0)
        return;
    if (PyType_Ready(&TrackType) < 0)
        return;
    if (PyType_Ready(&UserType) < 0)
        return;
    if (PyType_Ready(&ToplistBrowserType) < 0)
        return;

    m = Py_InitModule("_mockspotify", module_methods);
    if (m == NULL)
        return;

    PyObject *spotify = PyImport_ImportModule("spotify");
    PyObject *d = PyModule_GetDict(spotify);
    PyObject *s = PyUnicode_FromString("SpotifyError");

    SpotifyError = PyDict_GetItem(d, s);
    Py_DECREF(s);

    SpotifyApiVersion = Py_BuildValue("i", SPOTIFY_API_VERSION);
    Py_INCREF(SpotifyApiVersion);
    PyModule_AddObject(m, "api_version", SpotifyApiVersion);
    album_init(m);
    albumbrowser_init(m);
    artist_init(m);
    artistbrowser_init(m);
    link_init(m);
    playlist_init(m);
    playlistcontainer_init(m);
    session_init(m);
    search_init(m);
    track_init(m);
    user_init(m);
    toplistbrowser_init(m);
}
