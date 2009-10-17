#include <Python.h>
#include <structmember.h>
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

static PyMethodDef module_methods[] = {
    {"connect", session_connect, METH_VARARGS, "Run the spotify subsystem.  this will return on error, or after spotify is logged out."},
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC init_spotify(void) {
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

    m = Py_InitModule("_spotify", module_methods);
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
