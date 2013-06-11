#include <Python.h>
#include <structmember.h>
#include "libspotify/api.h"
#include "pyspotify.h"
#include "artist.h"
#include "artistbrowser.h"
#include "album.h"
#include "albumbrowser.h"
#include "link.h"
#include "playlist.h"
#include "playlistcontainer.h"
#include "playlistfolder.h"
#include "search.h"
#include "session.h"
#include "toplistbrowser.h"
#include "track.h"
#include "image.h"
#include "user.h"

PyObject *SpotifyError;
PyObject *SpotifyApiVersion;

static PyMethodDef module_methods[] = {
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC
init_spotify(void)
{
    if (PyType_Ready(&SessionType) < 0)
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
    if (PyType_Ready(&ToplistBrowserType) < 0)
        return;
    if (PyType_Ready(&TrackType) < 0)
        return;
    if (PyType_Ready(&ImageType) < 0)
        return;
    if (PyType_Ready(&UserType) < 0)
        return;

    PyObject *module = Py_InitModule("_spotify", module_methods);
    if (module == NULL)
        return;

    PyObject *spotify = PyImport_ImportModule("spotify");
    PyObject *module_dict = PyModule_GetDict(spotify);

    SpotifyError = PyDict_GetItemString(module_dict, "SpotifyError");
    SpotifyApiVersion = Py_BuildValue("i", SPOTIFY_API_VERSION);

    /* TODO: figure out why we store these globaly.                          */
    Py_XINCREF(SpotifyError);      /* SpotifyError has a borrowed ref.       */
    Py_XINCREF(SpotifyApiVersion); /* PyModule_AddObject steals the ref.     */
    Py_XDECREF(spotify);           /* dict is borrowed, only cleanup module. */

    PyModule_AddObject(module, "api_version", SpotifyApiVersion);

    /* TODO: rename to Type_add_to_module? */
    /* TODO: figure out we we can remove this in favour of generic helper? */
    /* TODO: figure out if PyType_Ready needs to be both in _init and above? */
    album_init(module);
    albumbrowser_init(module);
    artist_init(module);
    artistbrowser_init(module);
    link_init(module);
    playlist_init(module);
    playlistcontainer_init(module);
    playlistfolder_init(module);
    session_init(module);
    search_init(module);
    toplistbrowser_init(module);
    track_init(module);
    image_init(module);
    user_init(module);
}
