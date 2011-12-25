/*
 * Provides bindings to the libmockspotify API, which exports and implements
 * all the sp_* symbols from the Spotify API.
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
#include "playlistfolder.h"
#include "search.h"
#include "session.h"
#include "track.h"
#include "user.h"
#include "toplistbrowser.h"

/****************************** GLOBALS ************************************/

PyObject *SpotifyError;
PyObject *SpotifyApiVersion;

/***************************** MOCK EVENT GENERATION ***************************/

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

/**************** MOCKING NEW OBJECTS *******************/

/// Generate a mock spotify.User object
PyObject *
mock_user(PyObject *self, PyObject *args)
{
    char *canonical_name, *display_name;
    int loaded;
    sp_user *user;

    if (!PyArg_ParseTuple(args, "esesi", ENCODING, &canonical_name,
                          ENCODING, &display_name, &loaded))
        return NULL;

    user = mocksp_user_create(canonical_name, display_name, loaded);
    return User_FromSpotify(user);
}

/// Generate a mock spotify.Albumbrowse object
PyObject *
mock_albumbrowse(PyObject *self, PyObject *args, PyObject *kwds)
{
    AlbumBrowser *ab;
    int loaded;
    PyObject *album, *callback = NULL, *userdata = NULL;
    static char *kwlist[] =
        { "album", "loaded", "callback", "userdata", NULL };

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!i|OO", kwlist,
                                     &AlbumType, &album, &loaded,
                                     &callback, &userdata))
        return NULL;
    ab = (AlbumBrowser *) PyObject_CallFunctionObjArgs((PyObject *)&AlbumBrowserType,
                                                album, callback,
                                                userdata, NULL);
    ab->_browser->loaded = loaded;
    return (PyObject *)ab;
}

/// Generate a mock spotify.Artistbrowse object
PyObject *
mock_artistbrowse(PyObject *self, PyObject *args, PyObject *kwds)
{
    ArtistBrowser *ab;
    int loaded;
    PyObject *artist, *callback = NULL, *userdata = NULL;
    static char *kwlist[] =
        { "artist", "loaded", "callback", "userdata", NULL };

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!i|OO", kwlist,
                                     &ArtistType, &artist, &loaded,
                                     &callback, &userdata))
        return NULL;
    ab = (ArtistBrowser *) PyObject_CallFunctionObjArgs((PyObject *)&ArtistBrowserType,
                                                artist, callback,
                                                userdata, NULL);
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
    PyObject *seq, *item;
    sp_playlist *p;

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
        item = PySequence_GetItem(seq, i);
        PyObject *ptype = PyObject_CallMethod(item, "type", NULL);
        if (ptype) {
            if (strcmp(PyBytes_AS_STRING(ptype), "playlist") == 0) {
                p = ((Playlist *)item)->_playlist;
            }
            else if (strcmp(PyBytes_AS_STRING(ptype), "folder_start") == 0) {
                p = mocksp_playlist_create(((PlaylistFolder *)item)->_name);
                p->type = SP_PLAYLIST_TYPE_START_FOLDER;
            }
            else if (strcmp(PyBytes_AS_STRING(ptype), "folder_end") == 0) {
                p = mocksp_playlist_create("");
                p->type = SP_PLAYLIST_TYPE_END_FOLDER;
            }
            else {
                p = mocksp_playlist_create("");
                p->type = SP_PLAYLIST_TYPE_PLACEHOLDER;
            }
        }
        else return NULL;
        pc->_playlistcontainer->playlist[
            pc->_playlistcontainer->num_playlists++] = p;
    }
    return (PyObject *)pc;
}

PyObject *
mock_playlistfolder(PyObject *self, PyObject *args)
{
    PlaylistFolder *pf;
    char *type, *name = NULL;

    if (!PyArg_ParseTuple(args, "s|s", &type, &name))
            return NULL;
    pf = (PlaylistFolder *)PyObject_CallObject((PyObject *)&PlaylistFolderType,
                                               NULL);
    if (strcmp(type, "folder_start") == 0) {
        if (name) {
            pf->_type = SP_PLAYLIST_TYPE_START_FOLDER;
            pf->_name = PyMem_New(char, 256);
            strncpy(pf->_name, name, 256);
        }
        else {
            PyErr_SetString(PyExc_ValueError, "must provide name");
            return NULL;
        }
    }
    else if (strcmp(type, "folder_end") == 0) {
        pf->_type = SP_PLAYLIST_TYPE_END_FOLDER;
    }
    else {
        pf->_type = SP_PLAYLIST_TYPE_PLACEHOLDER;
    }
    return (PyObject *)pf;
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
    {"mock_playlistfolder", mock_playlistfolder, METH_VARARGS,
        "Create a mock playlist folder"},
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
    if (PyType_Ready(&PlaylistFolderType) < 0)
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
    playlistfolder_init(m);
    session_init(m);
    search_init(m);
    track_init(m);
    user_init(m);
    toplistbrowser_init(m);
}
