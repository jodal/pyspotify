
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


PyObject *SpotifyError;
PyObject *SpotifyApiVersion;

typedef struct {
    void *userdata;
    char username[1024];
    char password[1024];
    sp_session_config config;
} mocking_data;

mocking_data g_data;

struct sp_track {
    char mock[1024];
};

struct sp_link {
    char mock[1024];
};

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

void * sp_session_userdata(sp_session *session) {
    return g_data.config.userdata;
}

void sp_session_process_events(sp_session *session, int *next_timeout) {
    fprintf(stderr, "MOCK: sp_session_process_events called\n");
    fprintf(stderr, "MOCK: %d pending events\n", events);
    if(events > 0) {
        events--;
        event_type next = eventq[events];
        if(next == MOCK_LOGGED_IN) {
            fprintf(stderr, "MOCK: processing login event\n");
            g_data.config.callbacks->logged_in(session, SP_ERROR_OK);
        }
    }
    *next_timeout = 1;
    fprintf(stderr, "MOCK: sp_session_process_events completed\n");
}

const char * sp_user_canonical_name(sp_user *user) {
    fprintf(stderr, "MOCK: sp_user_canonical_name called\n");
    return g_data.username;
}

const char * sp_user_display_name(sp_user *user) {
    return "Mock display name";
}

bool sp_user_is_loaded(sp_user *user) {
    return 0;
}

sp_track* sp_link_as_track(sp_link *link) {
    fprintf(stderr, "sp_link_as_track called\n");
    sp_track *t = malloc(sizeof(sp_track));
    memset(t,0,sizeof(t));
    sprintf(t->mock, "track:%s", link->mock);
    fprintf(stderr, "sp_link_as_track: track mock is %s\n", t->mock);
    return t;
}

sp_link* sp_link_create_from_track(sp_track *track,int offset) {
    sp_link *l = malloc(sizeof(sp_link));
    memset(l,0,sizeof(l));
    sprintf(l->mock, "link:%s/%d", track->mock, offset);
    return l;
}

sp_link* sp_link_create_from_string(const char * link) {
    sp_link *l = malloc(sizeof(sp_link));
    memset(l,0,sizeof(l));
    sprintf(l->mock, "link:%s", link);
    return l;
}

int sp_link_as_string (sp_link *link, char *buffer, int buffer_size) {
    strncpy(buffer, link->mock, buffer_size);
    return strlen(link->mock);
}

const char *sp_track_name (sp_track *track) {
    fprintf(stderr, "track mock is %s\n", track->mock);
    return track->mock;
}

sp_error sp_session_init(const sp_session_config *config, sp_session **sess) {
    fprintf(stderr, "MOCK: sp_session_init called\n");
    if(strcmp(config->application_key, "appkey_good"))
        return SP_ERROR_BAD_APPLICATION_KEY;
    fprintf(stderr, "MOCK: sp_session_init mark 1\n");
    g_data.config.cache_location = malloc(strlen(config->cache_location) + 1);
    g_data.config.settings_location = malloc(strlen(config->settings_location) + 1);
    g_data.config.application_key = malloc(config->application_key_size);
    g_data.config.user_agent = malloc(strlen(config->user_agent) + 1);
    g_data.config.callbacks = (sp_session_callbacks *)malloc(sizeof(sp_session_callbacks));
    g_data.config.userdata = config->userdata;

    fprintf(stderr, "MOCK: sp_session_init mark 2\n");
    g_data.config.api_version = config->api_version;
    fprintf(stderr, "MOCK: sp_session_init mark 3\n");
    strcpy((char *)g_data.config.cache_location, config->cache_location);
    fprintf(stderr, "MOCK: sp_session_init mark 4\n");
    strcpy((char *)g_data.config.settings_location, config->settings_location);
    fprintf(stderr, "MOCK: sp_session_init mark 5\n");
    memcpy((char *)g_data.config.application_key, config->application_key, config->application_key_size);
    fprintf(stderr, "MOCK: sp_session_init mark 6\n");
    strcpy((char *)g_data.config.user_agent, config->user_agent);
    fprintf(stderr, "MOCK: sp_session_init mark 7\n");
    memcpy((char *)g_data.config.callbacks, config->callbacks, sizeof(sp_session_callbacks));
    fprintf(stderr, "MOCK: sp_session_init mark 8\n");
    g_data.config.userdata = config->userdata;
    fprintf(stderr, "MOCK: sp_session_init completed\n");
    return SP_ERROR_OK;
}

sp_error sp_session_login(sp_session *session, const char *username, const char *password) {
    fprintf(stderr, "MOCK: sp_session_login called\n");
    strcpy(g_data.username, username);
    strcpy(g_data.password, password);
    eventq[events++] = MOCK_LOGGED_IN;
    fprintf(stderr, "MOCK: sp_session_login completed\n");
    return SP_ERROR_OK;
}

sp_error sp_session_logout(sp_session *session) {
    fprintf(stderr, "MOCK: sp_session_logout called\n");
    eventq[events++] = MOCK_LOGGED_OUT;
    fprintf(stderr, "MOCK: sp_session_logout completed\n");
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

