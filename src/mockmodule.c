/* $Id$
 *
 * mockmodule.c
 *
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

sp_artist *_mock_artist(char *name, int loaded);
sp_track *_mock_track(char *name, int num_artists, sp_artist **artists,
		      sp_album *album, int duration, int popularity,
		      int disc, int index, sp_error error, int loaded);

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
    char *image;
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

sp_link* sp_link_create_from_track(sp_track *track,int offset) {
    sp_link *l = malloc(sizeof(sp_link));
    memset(l,0,sizeof(sp_link));
    sprintf(l->data, "link:%s/%d", track->name, offset);
    return l;
}

sp_link *sp_link_create_from_artist(sp_artist *artist) {
    sp_link *l = malloc(sizeof(sp_link));
    memset(l, 0, sizeof(sp_link));
    sprintf(l->data, "link_from_artist:%s", artist->name);
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

/*************** MOCK TRACK METHODS ************************/

bool sp_track_is_loaded(sp_track *t) {
    return t->loaded;
}

const char *sp_track_name (sp_track *track) {
    return track->name;
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

/*********************** MOCK ALBUM METHODS ************************/

bool sp_album_is_loaded(sp_album *a) {
    return a->loaded;
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
    return artist;
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
    return t;
}

PyObject *mock_track(PyObject *self, PyObject *args) {
    char *name;
    int num_artists;
    sp_artist **artists;
    sp_album *album;
    int duration;
    int popularity;
    int disc;
    int index;
    sp_error error;
    int loaded;
    if(!PyArg_ParseTuple(args, "siO!iiiiii", &name, &num_artists, &AlbumType, &album,
	&duration, &popularity, &disc, &index, &error, &loaded))
	return NULL;
    sp_track *t = _mock_track(name, num_artists, NULL, album, duration, popularity, disc, index, error, loaded);
    Track *track = (Track *)PyObject_CallObject((PyObject *)&TrackType, NULL);
    track->_track = t;
    Py_INCREF(track);
    return (PyObject *)track;
}

sp_album *_mock_album(char *name, sp_artist *artist, int year, char *image, int type, int loaded) {
    sp_album *a;
    a = malloc(sizeof(sp_album));
    memset(a, 0, sizeof(sp_album));
    strcpy(a->name, name);
    a->artist = artist;
    a->year = year;
    a->image = malloc(strlen(image)+1);
    strcpy(a->image, image);
    a->type = type;
    a->loaded = loaded;
    return a;
}

PyObject *mock_album(PyObject *self, PyObject *args) {
    PyObject *artist, *cover;
    char *name;
    int year, type, loaded;
    if(!PyArg_ParseTuple(args, "sO!isii", &name, &ArtistType, &artist, &year, &cover, &type, &loaded))
	return NULL;
    Album *album = (Album *)PyObject_CallObject((PyObject *)&AlbumType, NULL);
    album->_album = _mock_album(name, artist, year, cover, type, loaded);
    return album;
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
    return playlist;
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
    return pc;
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
    const char buff[1024];
    sprintf((char *)buff, "Error number %d", error);
    return buff;
}

sp_user * sp_session_user(sp_session *session) {
    return (sp_user *)-1;
}

static PyMethodDef module_methods[] = {
    {"connect", session_connect, METH_VARARGS, "Run the spotify subsystem.  this will return on error, or after spotify is logged out."},
    {"mock_track", mock_track, METH_VARARGS, "Create a mock track"},
    {"mock_album", mock_album, METH_VARARGS, "Create a mock album"},
    {"mock_artist", mock_artist, METH_VARARGS, "Create a mock artist"},
    {"mock_playlist", mock_playlist, METH_VARARGS, "Create a mock playlist"},
    {"mock_playlistcontainer", mock_playlistcontainer, METH_VARARGS, "Create a mock playlist container"},
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

