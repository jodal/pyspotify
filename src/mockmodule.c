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
#include <libmockspotify.h>
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

/***************************** MOCK EVENT GENERATION ***************************/

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
        mocksp_playlist_event(event, ((Playlist *) data)->_playlist);
    }
    else if (40 <= event) {
        /* Container event */
        mocksp_playlistcontainer_event(event, ((PlaylistContainer *)
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

sp_user *
sp_session_user(sp_session * session)
{
    return mocksp_user_create(g_data.username, "", NULL, "", 0, 1);
}

sp_playlistcontainer *
sp_session_playlistcontainer(sp_session * session)
{
    return mocksp_playlistcontainer_create();
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
    return mocksp_playlist_create("Starred");
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
    return mocksp_track_create(link->data + strlen("link:track:"), 0, NULL, NULL, 0,
                       0, 0, 0, 0, 1);
    return t;
}

sp_artist *
sp_link_as_artist(sp_link * link)
{
    if (strncmp(link->data, "link:artist:", strlen("link:artist:")))
        return NULL;
    return mocksp_artist_create(link->data + strlen("link:artist:"), 1);
}

sp_album *
sp_link_as_album(sp_link * link)
{
    if (strncmp(link->data, "link:album:", strlen("link:album:")))
        return NULL;
    return mocksp_album_create(link->data + strlen("link:album:"),
                       mocksp_artist_create("mock", 1), 1901, (byte *) "",
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

/**************** MOCKING NEW OBJECTS *******************/

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

    user = mocksp_user_create(canonical_name, display_name, full_name, picture,
                      relation, loaded);
    return User_FromSpotify(user);
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
    artist->_artist = mocksp_artist_create(s, loaded);
    return (PyObject *)artist;
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
    sp_track *t = mocksp_track_create(name, num_artists, NULL, album->_album, duration,
                              popularity,
                              disc, index, error, loaded);
    Track *track = (Track *) PyObject_CallObject((PyObject *)&TrackType, NULL);

    track->_track = t;
    Py_INCREF(track);
    return (PyObject *)track;
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
        mocksp_album_create(name, artist->_artist, year, cover, type, loaded,
                            available);
    return (PyObject *)album;
}

sp_playlist *
mocksp_playlist_create(char *name)
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
    playlist->_playlist = mocksp_playlist_create(s);
    for (i = 0; i < PySequence_Length(tracks); i++) {
        Track *t = (Track *) PySequence_GetItem(tracks, i);

        Py_INCREF(t);
        playlist->_playlist->track[playlist->_playlist->num_tracks++] =
            t->_track;
    }
    return (PyObject *)playlist;
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

    pc->_playlistcontainer = mocksp_playlistcontainer_create();
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
}
