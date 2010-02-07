/* $Id$
 *
 * Copyright 2009 Doug Winter
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *  http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
*/

/*
 * Provides mocking for the entire libspotify library.  All sp_ calls are mocked here to provide
 * something approximate to what libspotify would provide.
 *
 * Functions for creating mock instances of all spotify objects are also provided.
 *
*/

#include <stdio.h>
#include <string.h>
#include <Python.h>
#include "spotify/api.h"
#include "pyspotify.h"
#include "artist.h"
#include "album.h"
#include "link.h"
#include "playlist.h"
#include "search.h"
#include "session.h"
#include "track.h"

/***************************** FORWARD DEFINES *****************************/

sp_album *_mock_album(char *name, sp_artist *artist, int year, byte *cover, int type, int loaded);
sp_artist *_mock_artist(char *name, int loaded);
sp_track *_mock_track(char *name, int num_artists, sp_artist **artists,
		      sp_album *album, int duration, int popularity,
		      int disc, int index, sp_error error, int loaded);
sp_playlistcontainer *_mock_playlistcontainer();

/****************************** GLOBALS ************************************/

PyObject *SpotifyError;
PyObject *SpotifyApiVersion;

/************************** MOCK DATA STRUCTURES **************************/

typedef struct {
    void *userdata;
    char username[1024];
    char password[1024];
    sp_session_config config;
} mocking_data;

mocking_data g_data;

struct sp_link {
    char data[1024];
};

struct sp_artist {
    char name[1024];
    int loaded;
};

struct sp_album {
    char name[1024];
    sp_artist *artist;
    int year;
    byte cover[20];
    int type;
    int loaded;
};

struct sp_playlist {
    char name[1024];
    sp_track *track[32];
    int num_tracks;
};

struct sp_playlistcontainer {
    sp_playlist *playlist[32];
    int num_playlists;
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

/***************************** MOCK EVENT GENERATION ***************************/


typedef enum event_type {
    MOCK_LOGGED_IN                   = 0,
    MOCK_LOGGED_OUT                  = 1,
    MOCK_METADATA_UPDATED            = 2,
    MOCK_CONNECTION_ERROR            = 3,
//    message_to_user             = 4,
//    notify_main_thread          = 5,
//    music_delivery              = 6,
//    play_token_lost             = 7,
//    log_message                 = 8
} event_type;


event_type eventq[16];
int events = 0;

/***************************** MOCK SESSION FUNCTIONS **************************/

sp_error sp_session_login(sp_session *session, const char *username, const char *password) {
    strcpy(g_data.username, username);
    strcpy(g_data.password, password);
    eventq[events++] = MOCK_LOGGED_IN;
    return SP_ERROR_OK;
}

sp_error sp_session_logout(sp_session *session) {
    eventq[events++] = MOCK_LOGGED_OUT;
    return SP_ERROR_OK;
}

const char* sp_error_message(sp_error error) {
    static const char buff[1024];
    sprintf((char *)buff, "Error number %d", error);
    return buff;
}

sp_user * sp_session_user(sp_session *session) {
    return (sp_user *)-1;
}

sp_playlistcontainer *sp_session_playlistcontainer(sp_session *session) {
    return _mock_playlistcontainer();
}

sp_error sp_session_init(const sp_session_config *config, sp_session **sess) {
    if(strcmp(config->application_key, "appkey_good"))
        return SP_ERROR_BAD_APPLICATION_KEY;
    g_data.config.cache_location = malloc(strlen(config->cache_location) + 1);
    g_data.config.settings_location = malloc(strlen(config->settings_location) + 1);
    g_data.config.application_key = malloc(config->application_key_size);
    g_data.config.user_agent = malloc(strlen(config->user_agent) + 1);
    g_data.config.callbacks = (sp_session_callbacks *)malloc(sizeof(sp_session_callbacks));
    g_data.config.userdata = config->userdata;

    g_data.config.api_version = config->api_version;
    strcpy((char *)g_data.config.cache_location, config->cache_location);
    strcpy((char *)g_data.config.settings_location, config->settings_location);
    memcpy((char *)g_data.config.application_key, config->application_key, config->application_key_size);
    strcpy((char *)g_data.config.user_agent, config->user_agent);
    memcpy((char *)g_data.config.callbacks, config->callbacks, sizeof(sp_session_callbacks));
    g_data.config.userdata = config->userdata;
    return SP_ERROR_OK;
}

void * sp_session_userdata(sp_session *session) {
    return g_data.config.userdata;
}

void sp_session_process_events(sp_session *session, int *next_timeout) {
    if(events > 0) {
        events--;
        event_type next = eventq[events];
        if(next == MOCK_LOGGED_IN) {
            g_data.config.callbacks->logged_in(session, SP_ERROR_OK);
        }
    }
    *next_timeout = 1;
}

bool sp_user_is_loaded(sp_user *user) {
    return 0;
}

sp_error sp_session_player_load(sp_session *session, sp_track *track) {
    return 0;
}

sp_error sp_session_player_play(sp_session *session, bool b) {
    return 0;
}

/********************************* MOCK SEARCH FUNCTIONS *********************************/

sp_search *sp_search_create(sp_session *session, const char *query, int track_offset, int track_count, int album_offset, int album_count, int artist_offset, int artist_count, search_complete_cb *callback, void *userdata) {
    sp_search *search = malloc(sizeof(sp_search));
    if(!strncmp(query, "!loaded", 7))
	search->loaded = 0;
    if(!strncmp(query, "loaded", 6))
	search->loaded = 1;
    search->num_tracks = 4;
    search->num_albums = 3;
    search->num_artists = 2;
    search->total_tracks = 24;
    search->query = malloc(strlen(query) +1);
    strcpy(search->query, query);
    search->error = 3;
    search->did_you_mean = "did_you_mean";
    search->artist[0] = _mock_artist("foo", 1);
    search->artist[1] = _mock_artist("bar", 1);
    search->album[0] = _mock_album("baz", search->artist[0], 2001, "01234567890123456789", 1, 1);
    search->album[1] = _mock_album("qux", search->artist[1], 2002, "01234567890123456789", 1, 1);
    search->album[2] = _mock_album("quux", search->artist[0], 2003, "01234567890123456789", 1, 1);
    search->track[0] = _mock_track("corge", 1, search->artist, search->album[0], 99, 72, 1, 1, 0, 1);
    search->track[1] = _mock_track("grault", 1, search->artist, search->album[1], 98, 72, 1, 1, 0, 1);
    search->track[2] = _mock_track("garply", 1, search->artist, search->album[2], 97, 72, 1, 1, 0, 1);
    search->track[3] = _mock_track("waldo", 1, search->artist, search->album[0], 96, 72, 1, 1, 0, 1);
    callback(search, userdata);
    return search;
}

bool sp_search_is_loaded(sp_search *s) {
    return s->loaded;
}

int sp_search_num_artists(sp_search *s) {
    return s->num_artists;
}

int sp_search_num_albums(sp_search *s) {
    return s->num_albums;
}

int sp_search_num_tracks(sp_search *s) {
    return s->num_tracks;
}

int sp_search_total_tracks(sp_search *s) {
    return s->total_tracks;
}

sp_artist *sp_search_artist(sp_search *s, int i) {
    return s->artist[i];
}

sp_album *sp_search_album(sp_search *s, int i) {
    return s->album[i];
}

sp_track *sp_search_track(sp_search *s, int i) {
    return s->track[i];
}

const char *sp_search_query(sp_search *s) {
    return s->query;
}

sp_error sp_search_error(sp_search *s) {
    return s->error;
}

const char *sp_search_did_you_mean(sp_search *s) {
    return s->did_you_mean;
}


/********************************* MOCK USER FUNCTIONS ***********************************/

const char * sp_user_canonical_name(sp_user *user) {
    return g_data.username;
}

const char * sp_user_display_name(sp_user *user) {
    return "Mock display name";
}

/********************************* MOCK LINK FUNCTIONS ***********************************/


sp_track* sp_link_as_track(sp_link *link) {
    if(strncmp(link->data, "link:track:", strlen("link:track:")))
	return NULL;
    sp_track *t = malloc(sizeof(sp_track));
    memset(t,0,sizeof(sp_track));
    return _mock_track(link->data + strlen("link:track:"), 0, NULL, NULL, 0, 0, 0, 0, 0, 1);
    return t;
}

sp_artist *sp_link_as_artist(sp_link *link) {
    if(strncmp(link->data, "link:artist:", strlen("link:artist:")))
	return NULL;
    return _mock_artist(link->data + strlen("link:artist:"), 1);
}

sp_album *sp_link_as_album(sp_link *link) {
    if(strncmp(link->data, "link:album:", strlen("link:album:")))
	return NULL;
    return _mock_album(link->data + strlen("link:album:"), _mock_artist("mock", 1), 1901, (byte *)"", SP_ALBUMTYPE_ALBUM, 1);
}

sp_link* sp_link_create_from_track(sp_track *track,int offset) {
    sp_link *l = malloc(sizeof(sp_link));
    memset(l,0,sizeof(sp_link));
    sprintf(l->data, "link:track:%s/%d", track->name, offset);
    return l;
}

sp_link *sp_link_create_from_album(sp_album *album) {
    sp_link *l = malloc(sizeof(sp_link));
    memset(l, 0, sizeof(sp_link));
    sprintf(l->data, "link:album:%s", album->name);
    return l;
}

sp_link *sp_link_create_from_playlist(sp_playlist *playlist) {
    sp_link *l = malloc(sizeof(sp_link));
    memset(l, 0, sizeof(sp_link));
    sprintf(l->data, "link:playlist:%s", playlist->name);
    return l;
}

sp_link *sp_link_create_from_artist(sp_artist *artist) {
    sp_link *l = malloc(sizeof(sp_link));
    memset(l, 0, sizeof(sp_link));
    sprintf(l->data, "link:artist:%s", artist->name);
    return l;
}

sp_link *sp_link_create_from_search(sp_search *s) {
    sp_link *l = malloc(sizeof(sp_link));
    memset(l, 0, sizeof(sp_link));
    sprintf(l->data, "link:search:%s", s->query);
    return l;
}

sp_link* sp_link_create_from_string(const char * link) {
    sp_link *l = malloc(sizeof(sp_link));
    memset(l,0,sizeof(sp_link));
    sprintf(l->data, "link:%s", link);
    return l;
}

int sp_link_as_string (sp_link *link, char *buffer, int buffer_size) {
    strncpy(buffer, link->data, buffer_size);
    return strlen(link->data);
}

sp_linktype sp_link_type(sp_link *link) {
    return 1;
}


/*************** MOCK TRACK METHODS ************************/

bool sp_track_is_loaded(sp_track *t) {
    return t->loaded;
}

const char *sp_track_name (sp_track *track) {
    return track->name;
}

bool sp_track_is_available(sp_track *t) {
    return 1;
}

int sp_track_num_artists(sp_track *t) {
    return 3;
}

sp_artist *sp_track_artist(sp_track *t, int index) {
    const static sp_artist *a[3];
    a[0] = _mock_artist("a1", 1);
    a[1] = _mock_artist("a2", 1);
    a[2] = _mock_artist("a3", 1);
    return a[index];
}

int sp_track_disc(sp_track *t) {
    return t->disc;
}

int sp_track_index(sp_track *t) {
    return t->index;
}

int sp_track_popularity(sp_track *t) {
    return t->popularity;
}

int sp_track_duration(sp_track *t) {
    return t->duration;
}

sp_error sp_track_error(sp_track *t) {
    return t->error;
}

sp_album *sp_track_album(sp_track *t) {
    return t->album;
}

/*************** MOCK ARTIST METHODS **********************/

const char *sp_artist_name(sp_artist *a) {
    return a->name;
}

bool sp_artist_is_loaded(sp_artist *a) {
    return a->loaded;
}

/**************** MOCK PLAYLIST METHODS *****************/

bool sp_playlist_is_loaded(sp_playlist *p) {
    return 1;
}

const char *sp_playlist_name(sp_playlist *p) {
    return p->name;
}

sp_track *sp_playlist_track(sp_playlist *p, int index) {
    return p->track[index];
}

int sp_playlist_num_tracks(sp_playlist *p) {
    return p->num_tracks;
}

sp_playlist *sp_playlistcontainer_playlist(sp_playlistcontainer *pc, int index) {
    return pc->playlist[index];
}

int sp_playlistcontainer_num_playlists(sp_playlistcontainer *pc) {
    return pc->num_playlists;
}

/*********************** MOCK IMAGE METHODS ************************/

bool sp_image_is_loaded(sp_image *i) {
    return 1;
}

sp_imageformat sp_image_format(sp_image *i) {
    return 1;
}

sp_error sp_image_error(sp_image *i) {
    return 0;
}

const void *sp_image_data(sp_image *i, size_t *t) {
    return NULL;
}

sp_image *sp_image_create(sp_session *session, const byte image_id[20]) {
    return NULL;
}

void sp_image_add_load_callback(sp_image *i, image_loaded_cb *callback, void *userdata) {
}

void sp_image_remove_load_callback(sp_image *i, image_loaded_cb *callback, void *userdata) {
}

/*********************** MOCK ALBUM METHODS ************************/

bool sp_album_is_loaded(sp_album *a) {
    return a->loaded;
}

sp_artist *sp_album_artist(sp_album *a) {
    return a->artist;
}

const byte *sp_album_cover(sp_album *a) {
    return a->cover;
}

const char *sp_album_name(sp_album *a) {
    return a->name;
}

int sp_album_year(sp_album *a) {
    return a->year;
}

sp_albumtype sp_album_type(sp_album *a) {
    return a->type;
}

/**************** MOCKING NEW OBJECTS *******************/

/// Generate a mock sp_artist structure
sp_artist *_mock_artist(char *name, int loaded) {
    sp_artist *a;
    a = malloc(sizeof(sp_artist));
    memset(a, 0, sizeof(sp_artist));
    strcpy(a->name, name);
    a->loaded = loaded;
    return a;
}

/// Generate a mock spotify.Artist python object
PyObject *mock_artist(PyObject *self, PyObject *args) {
    char *s;
    int loaded;
    if(!PyArg_ParseTuple(args, "si", &s, &loaded))
	return NULL;
    Artist *artist = (Artist *)PyObject_CallObject((PyObject *)&ArtistType, NULL);
    if(!artist)
	return NULL;
    Py_INCREF(artist);
    artist -> _artist = _mock_artist(s, loaded);
    return (PyObject *)artist;
}

/// Generate a mock sp_track structure
sp_track *_mock_track(char *name, int num_artists, sp_artist **artists,
		      sp_album *album, int duration, int popularity,
		      int disc, int index, sp_error error, int loaded) {
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
    return t;
}

PyObject *mock_track(PyObject *self, PyObject *args) {
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
    if(!PyArg_ParseTuple(args, "siO!iiiiii", &name, &num_artists, &AlbumType, &album,
	&duration, &popularity, &disc, &index, &error, &loaded))
	return NULL;
    sp_track *t = _mock_track(name, num_artists, NULL, album->_album, duration, popularity, disc, index, error, loaded);
    Track *track = (Track *)PyObject_CallObject((PyObject *)&TrackType, NULL);
    track->_track = t;
    Py_INCREF(track);
    return (PyObject *)track;
}

sp_album *_mock_album(char *name, sp_artist *artist, int year, byte *cover, int type, int loaded) {
    sp_album *a;
    a = malloc(sizeof(sp_album));
    memset(a, 0, sizeof(sp_album));
    strcpy(a->name, name);
    a->artist = artist;
    a->year = year;
    memcpy(a->cover, cover, 20);
    a->type = type;
    a->loaded = loaded;
    return a;
}

PyObject *mock_album(PyObject *self, PyObject *args) {
    Artist *artist;
    byte *cover;
    char *name;
    int year, type, loaded;
    if(!PyArg_ParseTuple(args, "sO!isii", &name, &ArtistType, &artist, &year, &cover, &type, &loaded))
	return NULL;
    Album *album = (Album *)PyObject_CallObject((PyObject *)&AlbumType, NULL);
    album->_album = _mock_album(name, artist->_artist, year, cover, type, loaded);
    return (PyObject *)album;
}

sp_playlist *_mock_playlist(char *name) {
    sp_playlist *p;
    p = malloc(sizeof(sp_playlist));
    memset(p, 0, sizeof(sp_playlist));
    strcpy(p->name, name);
    return p;
}

PyObject *mock_playlist(PyObject *self, PyObject *args) {
    char *s;
    int i;
    PyObject *tracks;
    if(!PyArg_ParseTuple(args, "sO", &s, &tracks))
	return NULL;
    Playlist *playlist = (Playlist *)PyObject_CallObject((PyObject *)&PlaylistType, NULL);
    if(!playlist)
	return NULL;
    Py_INCREF(playlist);
    playlist -> _playlist = _mock_playlist(s);
    for(i=0; i< PySequence_Length(tracks); i++) {
	Track *t = (Track *)PySequence_GetItem(tracks, i);
	Py_INCREF(t);
	playlist->_playlist->track[playlist->_playlist->num_tracks++] = t->_track;
    }
    return (PyObject *)playlist;
}

sp_playlistcontainer *_mock_playlistcontainer() {
    sp_playlistcontainer *pc;
    pc = malloc(sizeof(sp_playlistcontainer));
    memset(pc, 0, sizeof(sp_playlistcontainer));
    return pc;
}

PyObject *mock_playlistcontainer(PyObject *self, PyObject *args) {
    PyObject *seq;
    if(!PyArg_ParseTuple(args, "O", &seq))
	return NULL;
    PlaylistContainer *pc = (PlaylistContainer *)PyObject_CallObject((PyObject *)&PlaylistContainerType, NULL);
    pc -> _playlistcontainer = _mock_playlistcontainer();
    int len = PySequence_Length(seq);
    int i;
    for(i=0; i<len; ++i) {
	Playlist *item = (Playlist *)PySequence_GetItem(seq, i);
	Py_INCREF(item);
	pc->_playlistcontainer->playlist[pc->_playlistcontainer->num_playlists++] = item->_playlist;
    }
    return (PyObject *)pc;
}

PyObject *mock_search(PyObject *self, PyObject *args) {
    sp_search *s;
    s = malloc(sizeof(sp_search));
    s->query = "query";
    Results *results = (Results *)PyObject_CallObject((PyObject *)&ResultsType, NULL);
    results->_search = s;
    Py_INCREF(results);
    return (PyObject *)results;
}

PyObject *mock_session(PyObject *self, PyObject *args) {
    Session *session = (Session *)PyObject_CallObject((PyObject *)&SessionType, NULL);
    Py_INCREF(session);
    return (PyObject *)session;
}

/**************************** MODULE INITIALISATION ********************************/

static PyMethodDef module_methods[] = {
    {"connect", session_connect, METH_VARARGS, "Run the spotify subsystem.  this will return on error, or after spotify is logged out."},
    {"mock_track", mock_track, METH_VARARGS, "Create a mock track"},
    {"mock_album", mock_album, METH_VARARGS, "Create a mock album"},
    {"mock_artist", mock_artist, METH_VARARGS, "Create a mock artist"},
    {"mock_playlist", mock_playlist, METH_VARARGS, "Create a mock playlist"},
    {"mock_playlistcontainer", mock_playlistcontainer, METH_VARARGS, "Create a mock playlist container"},
    {"mock_search", mock_search, METH_VARARGS, "Create mock search results"},
    {"mock_session", mock_session, METH_VARARGS, "Create a mock session"},
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC init_mockspotify(void) {
    PyObject *m;

    if(PyType_Ready(&SessionType) < 0)
	return;
    if(PyType_Ready(&AlbumType) < 0)
	return;
    if(PyType_Ready(&ArtistType) < 0)
	return;
    if(PyType_Ready(&LinkType) < 0)
	return;
    if(PyType_Ready(&PlaylistType) < 0)
	return;
    if(PyType_Ready(&PlaylistContainerType) < 0)
	return;
    if(PyType_Ready(&ResultsType) < 0)
	return;
    if(PyType_Ready(&TrackType) < 0)
	return;

    m = Py_InitModule("_mockspotify", module_methods);
    if(m == NULL)
        return;

    PyObject *spotify = PyImport_ImportModule("spotify");
    PyObject *d = PyModule_GetDict(spotify);
    PyObject *s = PyString_FromString("SpotifyError");
    SpotifyError = PyDict_GetItem(d, s);
    Py_DECREF(s);

    SpotifyApiVersion = Py_BuildValue("i", SPOTIFY_API_VERSION);
    Py_INCREF(SpotifyApiVersion);
    PyModule_AddObject(m, "api_version", SpotifyApiVersion);
    album_init(m);
    artist_init(m);
    link_init(m);
    playlist_init(m);
    session_init(m);
    search_init(m);
    track_init(m);
}

