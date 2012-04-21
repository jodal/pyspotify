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
#include "image.h"
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
        mocksp_event_playlist(event, ((Playlist *) data)->_playlist);
    }
    else if (40 <= event) {
        /* Container event */
        mocksp_event_playlistcontainer(event, ((PlaylistContainer *)
                                             data)->_playlistcontainer);
    }
    Py_RETURN_NONE;
}

/**************** MOCKING NEW OBJECTS *******************/

/// Generate a mock spotify.User object
PyObject *
mock_user(PyObject *self, PyObject *args, PyObject *kwds)
{
    char *canonical_name, *display_name = NULL;
    bool is_loaded = 1;
    sp_user *user;

    static char *kwlist[] =
        { "canonical_name", "display_name", "is_loaded", NULL };

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "es|esb", kwlist,
                                     ENCODING, &canonical_name,
                                     ENCODING, &display_name,
                                     &is_loaded))
        return NULL;
    if (!display_name)
        display_name = canonical_name;

    user = mocksp_user_create(canonical_name, display_name, is_loaded);
    return User_FromSpotify(user);
}

/// Generate a mock spotify.Albumbrowse object
PyObject *
mock_albumbrowse(PyObject *self, PyObject *args, PyObject *kwds)
{
    int i, error, request_duration, num_tracks=0, num_copyrights=0;
    Album *album;
    Artist *py_artist = NULL;
    sp_artist *artist;
    PyObject *py_tracks, *py_copyrights=NULL;
    char *review = "";
    sp_track **tracks = NULL;
    char **copyrights = NULL;
    sp_albumbrowse *ab;

    static char *kwlist[] =
        { "album", "tracks", "artist", "error", "request_duration",
          "copyrights", "review", NULL };

    if (!PyArg_ParseTupleAndKeywords(args, kwds,
                "O!O!|O!iiO!es", kwlist, &AlbumType, &album, &PyList_Type,
                &py_tracks, &ArtistType, &artist, &error, &request_duration,
                &PyList_Type, &py_copyrights, ENCODING, &review))
        return NULL;

    num_tracks = PyList_GET_SIZE(py_tracks);
    tracks = malloc(num_tracks * sizeof(sp_track *));
    for (i = 0; i < num_tracks; i++) {
        tracks[i] = ((Track *)PyList_GET_ITEM(py_tracks, i))->_track;
    }

    if (!py_artist)
        artist = sp_album_artist(album->_album);
    else
        artist = py_artist->_artist;

    if (py_copyrights) {
        num_copyrights = PyList_GET_SIZE(py_copyrights);
        copyrights = malloc(num_copyrights * sizeof(char *));
        for (i = 0; i < num_copyrights; i++) {
            copyrights[i] = PyBytes_AsString(PyList_GET_ITEM(py_copyrights, i));
        }
    }

    ab = mocksp_albumbrowse_create(error, request_duration, album->_album,
                                   artist, num_copyrights,
                                   (const char **)copyrights, num_tracks, tracks,
                                   (const char *)review, NULL, NULL);
    return AlbumBrowser_FromSpotify(ab);
}

/// Generate a mock spotify.Artistbrowse object
PyObject *
mock_artistbrowse(PyObject *self, PyObject *args, PyObject *kwds)
{
    int i, error, request_duration, num_tracks=0, num_albums=0,
        num_similar_artists=0, num_portraits=0;
    Artist *artist;
    PyObject *py_tracks, *py_albums, *py_similar_artists, *py_portraits=NULL;
    char *biography = "";
    sp_track **tracks;
    sp_album **albums;
    sp_artist **similar_artists;
    byte **portraits = NULL;
    sp_artistbrowse_type type = SP_ARTISTBROWSE_FULL;
    sp_artistbrowse *ab;

    static char *kwlist[] =
        { "artist", "tracks", "albums", "similar_artists", "error",
          "request_duration", "portraits", "biography", "type", NULL };

    if (!PyArg_ParseTupleAndKeywords(args, kwds,
                "O!O!O!O!|iiO!esiOO", kwlist, &ArtistType, &artist,
                &PyList_Type, &py_tracks, &PyList_Type, &py_albums,
                &PyList_Type, &py_similar_artists, &error, &request_duration,
                &PyList_Type, &py_portraits, ENCODING, &biography, &type))
        return NULL;

    num_tracks = PyList_GET_SIZE(py_tracks);
    tracks = malloc(num_tracks * sizeof(sp_track *));
    for (i = 0; i < num_tracks; i++) {
        tracks[i] = ((Track *)PyList_GET_ITEM(py_tracks, i))->_track;
    }

    num_albums = PyList_GET_SIZE(py_albums);
    albums = malloc(num_albums * sizeof(sp_album *));
    for (i = 0; i < num_albums; i++) {
        albums[i] = ((Album *)PyList_GET_ITEM(py_albums, i))->_album;
    }

    num_similar_artists = PyList_GET_SIZE(py_similar_artists);
    similar_artists = malloc(num_similar_artists * sizeof(sp_artist *));
    for (i = 0; i < num_similar_artists; i++) {
        similar_artists[i] =
            ((Artist *)PyList_GET_ITEM(py_similar_artists, i))->_artist;
    }

    if (py_portraits) {
        num_portraits = PyList_GET_SIZE(py_portraits);
        portraits = malloc(num_portraits * sizeof(byte *));
        for (i = 0; i < num_portraits; i++) {
            portraits[i] = (byte *)PyBytes_AsString(
                                PyList_GET_ITEM(py_portraits, i));
        }
    }

    ab = mocksp_artistbrowse_create(error, request_duration, artist->_artist,
                                    num_portraits, (const byte **)portraits,
                                    num_tracks, tracks, num_albums, albums,
                                    num_similar_artists, similar_artists,
                                    0, NULL,
                                    (const char *)biography, type, NULL, NULL);
    return ArtistBrowser_FromSpotify(ab);
}

/// Generate a mock spotify.Artist python object
PyObject *
mock_artist(PyObject *self, PyObject *args, PyObject *kwds)
{
    char *name;
    byte *portrait = NULL;
    bool is_loaded=1;
    sp_artist *artist;

    static char *kwlist[] =
        { "name", "portrait", "is_loaded", NULL };

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "es|sb", kwlist,
                                     ENCODING, &name, &portrait, &is_loaded))
        return NULL;

    artist = mocksp_artist_create(name, portrait, is_loaded);
    return Artist_FromSpotify(artist);
}

/// Generate a mock spotify.Track python object
PyObject *
mock_track(PyObject *self, PyObject *args, PyObject *kwds)
{
    char *name;
    int num_artists, i;
    sp_artist **artists;
    PyObject *py_artists;
    Album *album;
    int duration=0, popularity=0, disc=0, index=0;
    sp_error error = SP_ERROR_OK;
    bool is_loaded=1, is_local=0, is_autolinked=0, is_starred=0, is_placeholder=0;
    sp_track_availability availability = SP_TRACK_AVAILABILITY_AVAILABLE;
    sp_track_offline_status status = SP_TRACK_OFFLINE_NO;
    sp_track *track;

    static char *kwlist[] =
        { "name", "artists", "album", "duration", "popularity", "disc",
          "index", "error", "is_loaded", "availability", "status", "is_local",
          "is_autolinked", "is_starred", "is_placeholder", NULL };

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "esO!O!|iiiiibiibbbb", kwlist,
            ENCODING, &name, &PyList_Type, &py_artists, &AlbumType, &album,
            &duration, &popularity, &disc, &index, &error, &is_loaded,
            &availability, &status, &is_local, &is_autolinked, &is_starred,
            &is_placeholder))
        return NULL;

    num_artists = PyList_GET_SIZE(py_artists);
    artists = malloc(num_artists * sizeof(sp_artist *));
    for (i = 0; i < num_artists; i++) {
        artists[i] = ((Artist *)PyList_GET_ITEM(py_artists, i))->_artist;
    }

    track = mocksp_track_create(name, num_artists, artists, album->_album,
                                duration, popularity, disc, index, error,
                                is_loaded, availability, status, is_local,
                                is_autolinked, NULL, is_starred,
                                is_placeholder);
    return Track_FromSpotify(track);
}

/// Generate a mock spotify.Album python object
PyObject *
mock_album(PyObject *self, PyObject *args, PyObject *kwds)
{
    Artist *artist;
    byte *cover=NULL;
    char *name;
    int year=2011;
    bool is_loaded=1, is_available=1;
    sp_albumtype type=SP_ALBUMTYPE_ALBUM;
    sp_album *album;

    static char *kwlist[] =
        { "name", "artist", "year", "cover", "type", "is_loaded",
          "is_available", NULL };

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "esO!|isibb", kwlist,
                ENCODING, &name, &ArtistType, &artist, &year, &cover, &type,
                &is_loaded, &is_available))
        return NULL;

    album = mocksp_album_create(name, artist->_artist, year,
                                (const byte *)cover, type, is_loaded,
                                is_available);
    return Album_FromSpotify(album);
}

/// Generate a mock spotify.Playlist python object
PyObject *
mock_playlist(PyObject *self, PyObject *args, PyObject *kwds)
{
    char *name, *description="";
    sp_playlist_track_t *tracks;
    User *owner;
    PyObject *py_tracks, *py_subscribers=NULL;
    sp_subscribers *subscribers;
    char **names;
    int i, num_subscribers=0, num_tracks, offline_download_completed=1, count;
    byte *image=NULL;
    bool is_loaded=1, is_collaborative=0, has_pending_changes=0, is_in_ram=0;
    sp_playlist_offline_status offline_status = SP_PLAYLIST_OFFLINE_STATUS_NO;

    Track *track;
    User *creator;
    int create_time;
    char *message;
    bool seen;

    sp_playlist *playlist;

    static char *kwlist[] =
        { "name", "tracks", "owner", "subscribers", "num_subscribers",
          "description", "image", "is_loaded", "is_collaborative",
          "has_pending_changes", "is_in_ram", "offline_status",
          "offline_download_completed", NULL };

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "esO!O!|O!iessbbbbii", kwlist,
                ENCODING, &name, &PyList_Type, &py_tracks, &UserType, &owner,
                &PyList_Type, &py_subscribers, &num_subscribers, ENCODING,
                &description, &image, &is_loaded, &is_collaborative,
                &has_pending_changes, &is_in_ram, &offline_status,
                &offline_download_completed))
        return NULL;

    num_tracks = PyList_GET_SIZE(py_tracks);
    tracks = malloc(num_tracks * sizeof(sp_playlist_track_t));
    for (i = 0; i < num_tracks; i++) {
        create_time = 0;
        message = "";
        seen = 0;
        if (!PyArg_ParseTuple(PyList_GET_ITEM(py_tracks, i), "O!O!|iesb",
                              &TrackType, &track, &UserType, &creator,
                              &create_time, ENCODING, &message, &seen))
            return NULL;
        tracks[i].track = track->_track;
        tracks[i].creator = creator->_user;
        tracks[i].create_time = create_time;
        tracks[i].message = message;
        tracks[i].seen = seen;
    }

    if (py_subscribers) {
        count = PyList_GET_SIZE(py_subscribers);
        names = (char **)malloc(count * sizeof(char *));
        for (i = 0; i < count; i++) {
            names[i] = PyBytes_AsString(PyList_GET_ITEM(py_subscribers, i));
        }
    }
    else {
        count = 0;
        names = NULL;
    }
    subscribers = mocksp_subscribers(count, names);
    if (names) free(names);

    playlist = mocksp_playlist_create(name, is_loaded, owner->_user,
                    is_collaborative, (const char *)description,
                    (const byte *)image, has_pending_changes, num_subscribers,
                    subscribers, is_in_ram, offline_status,
                    offline_download_completed, num_tracks, tracks);
    free(tracks);
    return Playlist_FromSpotify(playlist);
}

/// Generate a mock spotify.PlaylistContainer python object
PyObject *
mock_playlistcontainer(PyObject *self, PyObject *args, PyObject *kwds)
{
    User *owner;
    bool is_loaded=1;
    int i, num_playlists;
    sp_playlistcontainer_playlist_t *playlists;
    PyObject *py_playlists, *playlist;

    sp_playlist *p;
    sp_playlist_type type;
    char *folder_name;
    sp_uint64 folder_id;

    sp_playlistcontainer *container;

    static char *kwlist[] =
        { "owner", "playlists", "is_loaded", NULL };

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!O!|b", kwlist,
                                     &UserType, &owner, &PyList_Type,
                                     &py_playlists, &is_loaded))
        return NULL;

    num_playlists = PyList_GET_SIZE(py_playlists);
    playlists = malloc(num_playlists * sizeof(sp_playlistcontainer_playlist_t));
    for (i = 0; i < num_playlists; i++) {
        p = NULL;
        type = SP_PLAYLIST_TYPE_PLACEHOLDER;
        folder_name = "";
        folder_id = 0;
        playlist = PyList_GET_ITEM(py_playlists, i);

        if (playlist->ob_type == &PlaylistType) {
            p = ((Playlist *)playlist)->_playlist;
            type = SP_PLAYLIST_TYPE_PLAYLIST;
        }
        else if (playlist->ob_type == &PlaylistFolderType) {
            type        = ((PlaylistFolder *)playlist)->_type;
            folder_name = ((PlaylistFolder *)playlist)->_name;
            folder_id   = ((PlaylistFolder *)playlist)->_id;
        }
        playlists[i].playlist = p;
        playlists[i].type = type;
        playlists[i].folder_name = folder_name;
        playlists[i].folder_id = folder_id;
    }
    container = mocksp_playlistcontainer_create(owner->_user, is_loaded,
                                                num_playlists, playlists,
                                                NULL, NULL);
    free(playlists);
    return PlaylistContainer_FromSpotify(container);
}

/// Generate a mock spotify.PlaylistFolder python object
PyObject *
mock_playlistfolder(PyObject *self, PyObject *args, PyObject *kwds)
{
    PlaylistFolder *pf;
    char *type, *name = NULL;
    sp_uint64 folder_id = 0;

    static char *kwlist[] =
        { "type", "name", "folder_id", NULL };

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "s|sK", kwlist,
                                     &type, &name, &folder_id))
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
    pf->_id = folder_id;
    return (PyObject *)pf;
}

/// Generate a mock spotify.Results python object
PyObject *
mock_search(PyObject *self, PyObject *args, PyObject *kwds)
{
    int i;
    sp_error error = SP_ERROR_OK;
    char *query, *did_you_mean="";
    int total_tracks=0, total_albums=0, total_artists=0;
    int num_tracks, num_albums, num_artists;
    sp_track **tracks;
    sp_album **albums;
    sp_artist **artists;
    PyObject *py_tracks, *py_albums, *py_artists;

    sp_search *search;

    static char *kwlist[] =
        { "query", "tracks", "albums", "artists",
          "total_tracks", "total_albums", "total_artists", "did_you_mean",
          "error", NULL };

    if (!PyArg_ParseTupleAndKeywords(args, kwds,
                "esO!O!O!|iiiesi", kwlist, ENCODING, &query,
                &PyList_Type, &py_tracks, &PyList_Type, &py_albums,
                &PyList_Type, &py_artists, &total_tracks, &total_albums,
                &total_artists, ENCODING, &did_you_mean, &error))
        return NULL;

    num_tracks = PyList_GET_SIZE(py_tracks);
    tracks = malloc(num_tracks * sizeof(sp_track *));
    for (i = 0; i < num_tracks; i++) {
        tracks[i] = ((Track *)PyList_GET_ITEM(py_tracks, i))->_track;
    }

    num_albums = PyList_GET_SIZE(py_albums);
    albums = malloc(num_albums * sizeof(sp_album *));
    for (i = 0; i < num_albums; i++) {
        albums[i] = ((Album *)PyList_GET_ITEM(py_albums, i))->_album;
    }

    num_artists = PyList_GET_SIZE(py_artists);
    artists = malloc(num_artists * sizeof(sp_artist *));
    for (i = 0; i < num_artists; i++) {
        artists[i] =
            ((Artist *)PyList_GET_ITEM(py_artists, i))->_artist;
    }

    if (total_tracks < num_tracks)
        total_tracks = num_tracks;
    if (total_albums < num_albums)
        total_albums = num_albums;
    if (total_artists < num_artists)
        total_artists = num_artists;

    search = mocksp_search_create(error, query, (const char *)did_you_mean,
                                  total_tracks, num_tracks,
                                  (const sp_track **)tracks,
                                  total_albums, num_albums,
                                  (const sp_album **)albums,
                                  total_artists, num_artists,
                                  (const sp_artist **)artists,
                                  0, 0, NULL,
                                  NULL, NULL);
    free(tracks);
    free(albums);
    free(artists);
    return Results_FromSpotify(search);
}

/// Generate a mock spotify.Session python object
PyObject *
mock_session(PyObject *self, PyObject *args, PyObject *kwds)
{
    sp_session *session;
    sp_session_config config;
    char *username = "";

    sp_connectionstate connectionstate = SP_CONNECTION_STATE_LOGGED_IN;
    sp_offline_sync_status sync_status;
    int offline_time_left=0, offline_num_playlists=0, offline_tracks_to_sync=0;
    sp_playlist *inbox = NULL;

    static char *kwlist[] = { "username", "inbox", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|esO!", kwlist,
                                     ENCODING, &username,
                                     &PlaylistType, &inbox))
        return NULL;

    /* Config */
    memset(&config, 0, sizeof(sp_session_config));
    config.api_version = SPOTIFY_API_VERSION;
    config.application_key = "appkey_good";

    /* Sync status */
    memset(&sync_status, 0, sizeof(sp_offline_sync_status));

    session = mocksp_session_create(&config, connectionstate,
                                    offline_time_left, &sync_status,
                                    offline_num_playlists,
                                    offline_tracks_to_sync, inbox);
    session->username = username;
    return Session_FromSpotify(session);
}


/// Generate a mock spotify.Toplistbrowse object
PyObject *
mock_toplistbrowse(PyObject *self, PyObject *args, PyObject *kwds)
{
    int i, error=0, request_duration=0, num_tracks=0, num_albums=0, num_artists=0;
    PyObject *py_tracks, *py_albums, *py_artists;
    sp_album  **albums;
    sp_artist **artists;
    sp_track  **tracks;
    sp_toplistbrowse *tb;

    static char *kwlist[] =
        { "albums", "artists", "tracks", "error", "request_duration", NULL };

    if (!PyArg_ParseTupleAndKeywords(args, kwds,
                "O!O!O!|ii", kwlist, &PyList_Type, &py_albums,
                &PyList_Type, &py_artists, &PyList_Type, &py_tracks,
                &error, &request_duration))
        return NULL;

    num_tracks = PyList_GET_SIZE(py_tracks);
    tracks = malloc(num_tracks * sizeof(sp_track *));
    for (i = 0; i < num_tracks; i++) {
        tracks[i] = ((Track *)PyList_GET_ITEM(py_tracks, i))->_track;
    }

    num_albums = PyList_GET_SIZE(py_albums);
    albums = malloc(num_albums * sizeof(sp_album *));
    for (i = 0; i < num_albums; i++) {
        albums[i] = ((Album *)PyList_GET_ITEM(py_albums, i))->_album;
    }

    num_artists = PyList_GET_SIZE(py_artists);
    artists = malloc(num_artists * sizeof(sp_artist *));
    for (i = 0; i < num_artists; i++) {
        artists[i] = ((Artist *)PyList_GET_ITEM(py_artists, i))->_artist;
    }

    tb = mocksp_toplistbrowse_create(error, request_duration, num_artists,
                                    artists, num_albums, albums, num_tracks,
                                    tracks, NULL, NULL);
    return ToplistBrowser_FromSpotify(tb);
}

/************************* REGISTRY MANIPULATION ****************************/

PyObject *
mock_registry_add(PyObject *self, PyObject *args, PyObject *kwds)
{
    PyObject *sp_object;
    const char* uri;

    static char *kwlist[] =
        { "uri", "sp_object", NULL };

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "sO", kwlist,
                                     &uri, &sp_object))
        return NULL;

#define REGISTRY_ADD_SP_STRUCT_IF(uri, obj, type, attr) \
    if (obj->ob_type == &type##Type) {                  \
        registry_add(uri, ((type *)obj)->_##attr);      \
        Py_RETURN_NONE;                                 \
    }

    REGISTRY_ADD_SP_STRUCT_IF(uri, sp_object, Album, album)
    REGISTRY_ADD_SP_STRUCT_IF(uri, sp_object, AlbumBrowser, browser)
    REGISTRY_ADD_SP_STRUCT_IF(uri, sp_object, Artist, artist)
    REGISTRY_ADD_SP_STRUCT_IF(uri, sp_object, ArtistBrowser, browser)
    REGISTRY_ADD_SP_STRUCT_IF(uri, sp_object, Image, image)
    REGISTRY_ADD_SP_STRUCT_IF(uri, sp_object, Playlist, playlist)
    REGISTRY_ADD_SP_STRUCT_IF(uri, sp_object,
                              PlaylistContainer, playlistcontainer)
    REGISTRY_ADD_SP_STRUCT_IF(uri, sp_object, Results, search)
    REGISTRY_ADD_SP_STRUCT_IF(uri, sp_object, ToplistBrowser, toplistbrowse)
    REGISTRY_ADD_SP_STRUCT_IF(uri, sp_object, Track, track)
    REGISTRY_ADD_SP_STRUCT_IF(uri, sp_object, User, user)

    Py_RETURN_NONE;
}

PyObject *
mock_registry_clean(PyObject *self)
{
    registry_clean();
    Py_RETURN_NONE;
}

/************************* CURRENT SESSION **********************************/

PyObject *
mock_set_current_session(PyObject *self, PyObject *args, PyObject *kwds)
{
    PyObject *session;

    static char *kwlist[] = { "session", NULL };

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O", kwlist,
                                     &session))
        return NULL;

    if (session == Py_None) {
        g_session = NULL;
    } else {
        g_session = ((Session *)session)->_session;
    }
    Py_RETURN_NONE;
}

/************************* MODULE INITIALISATION ****************************/

static PyMethodDef module_methods[] = {
    {"connect", session_connect, METH_VARARGS,
        "Run the Spotify subsystem. This will return on error,"
        " or after Spotify is logged out."},
    {"mock_track", (PyCFunction)mock_track,
        METH_VARARGS | METH_KEYWORDS, "Create a mock track"},
    {"mock_album", (PyCFunction)mock_album,
        METH_VARARGS | METH_KEYWORDS, "Create a mock album"},
    {"mock_albumbrowse", (PyCFunction)mock_albumbrowse,
        METH_VARARGS | METH_KEYWORDS, "Create a mock album browser"},
    {"mock_artist", (PyCFunction)mock_artist,
        METH_VARARGS | METH_KEYWORDS, "Create a mock artist"},
    {"mock_artistbrowse", (PyCFunction)mock_artistbrowse,
        METH_VARARGS | METH_KEYWORDS, "Create a mock artist browser"},
    {"mock_playlist", (PyCFunction)mock_playlist,
        METH_VARARGS | METH_KEYWORDS, "Create a mock playlist"},
    {"mock_playlistcontainer", (PyCFunction)mock_playlistcontainer,
        METH_VARARGS | METH_KEYWORDS, "Create a mock playlist container"},
    {"mock_playlistfolder", (PyCFunction)mock_playlistfolder,
        METH_VARARGS | METH_KEYWORDS, "Create a mock playlist folder"},
    {"mock_search", (PyCFunction)mock_search,
        METH_VARARGS | METH_KEYWORDS, "Create mock search results"},
    {"mock_session", (PyCFunction)mock_session,
        METH_VARARGS | METH_KEYWORDS, "Create a mock session"},
    {"mock_toplistbrowse", (PyCFunction)mock_toplistbrowse,
        METH_VARARGS | METH_KEYWORDS, "Create a mock toplist browser"},
    {"mock_set_current_session", (PyCFunction)mock_set_current_session,
        METH_VARARGS | METH_KEYWORDS, "Set the current session."},
    {"mock_event_trigger", event_trigger,
        METH_VARARGS, "Triggers an event"},
    {"mock_user", (PyCFunction)mock_user,
        METH_VARARGS | METH_KEYWORDS, "Create a mock user."},
    {"registry_add", (PyCFunction)mock_registry_add,
        METH_VARARGS | METH_KEYWORDS, "Add an object to the mock registry."},
    {"registry_clean", (PyCFunction)mock_registry_clean,
        METH_NOARGS, "Delete all the objects from the mock registry."},
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
