#include <Python.h>
#include <structmember.h>
#include "libspotify/api.h"
#include "pyspotify.h"
#include "link.h"
#include "track.h"
#include "artist.h"
#include "album.h"
#include "playlist.h"
#include "search.h"
#include "session.h"

static PyObject *
Link_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *self = type->tp_alloc(type, 0);
    Link_SP_LINK(self) = NULL;
    return self;
}

PyObject *
Link_FromSpotify(sp_link *link, bool add_ref)
{
    PyObject *self = LinkType.tp_alloc(&LinkType, 0);
    Link_SP_LINK(self) = link;
    if (add_ref)
        sp_link_add_ref(link);
    return self;
}

static void
Link_dealloc(PyObject *self)
{
    if (Link_SP_LINK(self) != NULL)
        sp_link_release(Link_SP_LINK(self));
    self->ob_type->tp_free(self);
}

static PyObject *
Link_from_string(PyObject *self, PyObject *args)
{
    const char *tmp;
    if (!PyArg_ParseTuple(args, "s", &tmp))
        return NULL;

    sp_link *link = sp_link_create_from_string(tmp);
    if (link == NULL) {
        PyErr_SetString(SpotifyError, "Failed to get link from a Spotify URI");
        return NULL;
    }
    return Link_FromSpotify(link, 0 /* add_ref */);
}

static PyObject *
Link_from_track(PyObject *self, PyObject *args)
{
    PyObject *track;
    int offset = 0;
    if (!PyArg_ParseTuple(args, "O!|i", &TrackType, &track, &offset)) {
        return NULL;
    }

    sp_link *link = sp_link_create_from_track(Track_SP_TRACK(track), offset);
    if (link == NULL) {
        PyErr_SetString(SpotifyError, "Failed to get link from a track");
        return NULL;
    }
    return Link_FromSpotify(link, 0 /* add_ref */);
}

static PyObject *
Link_from_album(PyObject *self, PyObject *args)
{
    PyObject *album;
    if (!PyArg_ParseTuple(args, "O!", &AlbumType, &album))
        return NULL;

    sp_link *link = sp_link_create_from_album(Album_SP_ALBUM(album));
    if (link == NULL) {
        PyErr_SetString(SpotifyError, "Failed to get link from an album");
        return NULL;
    }
    return Link_FromSpotify(link, 0 /* add_ref */);
}

static PyObject *
Link_from_artist(PyObject *self, PyObject *args)
{
    PyObject *artist;
    if (!PyArg_ParseTuple(args, "O!", &ArtistType, &artist)) {
        return NULL;
    }

    sp_link *link = sp_link_create_from_artist(Artist_SP_ARTIST(artist));
    if (link == NULL) {
        PyErr_SetString(SpotifyError, "Failed to get link from an artist");
        return NULL;
    }
    return Link_FromSpotify(link, 0 /* add_ref */);
}

static PyObject *
Link_from_search(PyObject *self, PyObject *args)
{
    PyObject *results;
    if (!PyArg_ParseTuple(args, "O!", &ResultsType, &results)) {
        return NULL;
    }

    sp_link *link = sp_link_create_from_search(Results_SP_SEARCH(results));
    if (link == NULL) {
        PyErr_SetString(SpotifyError, "Failed to get link from a search");
        return NULL;
    }
    return Link_FromSpotify(link, 0 /* add_ref */);
}

static PyObject *
Link_from_playlist(PyObject *self, PyObject *args)
{
    PyObject *playlist;

    if (!PyArg_ParseTuple(args, "O!", &PlaylistType, &playlist))
        return NULL;

    sp_link *link = sp_link_create_from_playlist(Playlist_SP_PLAYLIST(playlist));
    if (link == NULL) {
        PyErr_SetString(SpotifyError, "Failed to get link from a playlist");
        return NULL;
    }
    return Link_FromSpotify(link, 0 /* add_ref */);
}

static PyObject *
Link_type(PyObject *self)
{
    /* TODO: return enums that represent sp_linktype */
    sp_linktype link_type = sp_link_type(Link_SP_LINK(self));
    return Py_BuildValue("i", link_type);
}

static PyObject *
Link_as_track(PyObject *self)
{
    sp_track *track = sp_link_as_track(Link_SP_LINK(self));
    if (track == NULL) {
        PyErr_SetString(SpotifyError, "Not a track link");
        return NULL;
    }
    return Track_FromSpotify(track, 1 /* add_ref */);
}

static PyObject *
Link_as_album(PyObject *self)
{
    sp_album *album = sp_link_as_album(Link_SP_LINK(self));
    if (album == NULL) {
        PyErr_SetString(SpotifyError, "Not an album link");
        return NULL;
    }
    return Album_FromSpotify(album, 1 /* add_ref */);
}

static PyObject *
Link_as_artist(PyObject *self)
{
    sp_artist *artist = sp_link_as_artist(Link_SP_LINK(self));
    if (artist == NULL) {
        PyErr_SetString(SpotifyError, "Not an artist link");
        return NULL;
    }
    return Artist_FromSpotify(artist, 1 /* add_ref */);
}

static PyObject *
Link_as_playlist(PyObject *self)
{
    if (!g_session) {
        PyErr_SetString(SpotifyError, "Not logged in");
        return NULL;
    }

    sp_playlist *playlist = sp_playlist_create(g_session, Link_SP_LINK(self));
    if (playlist == NULL) {
        PyErr_SetString(SpotifyError, "Not a playlist link");
        return NULL;
    }
    return Playlist_FromSpotify(playlist, 0 /* add_ref */);
}

static PyObject *
Link_str(PyObject *self)
{
    char uri[LINK_MAX_URI_LENGTH];
    int len;

    len = sp_link_as_string(Link_SP_LINK(self), uri, sizeof(uri));
    if (len < 0) {
        PyErr_SetString(SpotifyError,
                        "failed to render Spotify URI from link");
        return NULL;
    }
    return Py_BuildValue("s#", uri, len);
}

static PyMethodDef Link_methods[] = {
    {"from_string", (PyCFunction)Link_from_string, METH_VARARGS | METH_CLASS,
     "Create a new Link object from a string"
    },
    {"from_track", (PyCFunction)Link_from_track, METH_VARARGS | METH_CLASS,
     "Create a new Link object from a Track object"
    },
    {"from_album", (PyCFunction)Link_from_album, METH_VARARGS | METH_CLASS,
     "Create a new Link object from an Album object"
    },
    {"from_artist", (PyCFunction)Link_from_artist, METH_VARARGS | METH_CLASS,
     "Create a new Link object from an Artist object"
    },
    {"from_search", (PyCFunction)Link_from_search, METH_VARARGS | METH_CLASS,
     "Create a new Link object from a Search object"
    },
    {"from_playlist", (PyCFunction)Link_from_playlist, METH_VARARGS | METH_CLASS,
     "Create a new Link object from a Playlist object"
    },
    {"type", (PyCFunction)Link_type, METH_NOARGS,
     "Return the type of the link"},
    {"as_playlist", (PyCFunction)Link_as_playlist, METH_NOARGS,
     "Return this link as a Playlist object"
    },
    {"as_track", (PyCFunction)Link_as_track, METH_NOARGS,
     "Return this link as a Track object"
    },
    {"as_album", (PyCFunction)Link_as_album, METH_NOARGS,
     "Return this link as a Album object"
    },
    {"as_artist", (PyCFunction)Link_as_artist, METH_NOARGS,
     "Return this link as an Artist object"
    },
    {NULL} /* Sentinel */
};

static PyMemberDef Link_members[] = {
    {NULL} /* Sentinel */
};

PyTypeObject LinkType = {
    PyObject_HEAD_INIT(NULL)
    0,                                        /*ob_size*/
    "spotify.Link",                           /*tp_name*/
    sizeof(Link),                             /*tp_basicsize*/
    0,                                        /*tp_itemsize*/
    (destructor) Link_dealloc,                /*tp_dealloc*/
    0,                                        /*tp_print*/
    0,                                        /*tp_getattr*/
    0,                                        /*tp_setattr*/
    0,                                        /*tp_compare*/
    0,                                        /*tp_repr*/
    0,                                        /*tp_as_number*/
    0,                                        /*tp_as_sequence*/
    0,                                        /*tp_as_mapping*/
    0,                                        /*tp_hash*/
    0,                                        /*tp_call*/
    Link_str,                                 /*tp_str*/
    0,                                        /*tp_getattro*/
    0,                                        /*tp_setattro*/
    0,                                        /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags */
    "Link objects",                           /* tp_doc */
    0,                                        /* tp_traverse */
    0,                                        /* tp_clear */
    0,                                        /* tp_richcompare */
    0,                                        /* tp_weaklistoffset */
    0,                                        /* tp_iter */
    0,                                        /* tp_iternext */
    Link_methods,                             /* tp_methods */
    Link_members,                             /* tp_members */
    0,                                        /* tp_getset */
    0,                                        /* tp_base */
    0,                                        /* tp_dict */
    0,                                        /* tp_descr_get */
    0,                                        /* tp_descr_set */
    0,                                        /* tp_dictoffset */
    0,                                        /* tp_init */
    0,                                        /* tp_alloc */
    Link_new,                                 /* tp_new */
};

void
link_init(PyObject *module)
{
    if (PyType_Ready(&LinkType) < 0)
        return;

    PyModule_AddObject(module, "Link", (PyObject *)&LinkType);
    Py_INCREF(&LinkType);

    PyObject *invalid = Py_BuildValue("i", SP_LINKTYPE_INVALID);
    PyObject *track = Py_BuildValue("i", SP_LINKTYPE_TRACK);
    PyObject *album = Py_BuildValue("i", SP_LINKTYPE_ALBUM);
    PyObject *artist = Py_BuildValue("i", SP_LINKTYPE_ARTIST);
    PyObject *search = Py_BuildValue("i", SP_LINKTYPE_SEARCH);
    PyObject *playlist = Py_BuildValue("i", SP_LINKTYPE_PLAYLIST);
    PyObject *profile = Py_BuildValue("i", SP_LINKTYPE_PROFILE);
    PyObject *starred = Py_BuildValue("i", SP_LINKTYPE_STARRED);
    PyObject *localtrack = Py_BuildValue("i", SP_LINKTYPE_LOCALTRACK);
    PyObject *image = Py_BuildValue("i", SP_LINKTYPE_IMAGE);

    PyMapping_SetItemString(LinkType.tp_dict, "LINK_INVALID", invalid);
    PyMapping_SetItemString(LinkType.tp_dict, "LINK_TRACK", track);
    PyMapping_SetItemString(LinkType.tp_dict, "LINK_ALBUM", album);
    PyMapping_SetItemString(LinkType.tp_dict, "LINK_ARTIST", artist);
    PyMapping_SetItemString(LinkType.tp_dict, "LINK_SEARCH", search);
    PyMapping_SetItemString(LinkType.tp_dict, "LINK_PLAYLIST", playlist);
    PyMapping_SetItemString(LinkType.tp_dict, "LINK_PROFILE", profile);
    PyMapping_SetItemString(LinkType.tp_dict, "LINK_STARRED", starred);
    PyMapping_SetItemString(LinkType.tp_dict, "LINK_LOCALTRACK", localtrack);
    PyMapping_SetItemString(LinkType.tp_dict, "LINK_IMAGE", image);

    /* TODO: should we decref as SetItem does not steal the ref? */
    /* TODO: consider following code instead? */
    /*
    PyObject *types = Py_BuildValue("{sisi...}",
                                    "LINK_INVALID", SP_LINKTYPE_INVALID,
                                    "LINK_TRACK", SP_LINKTYPE_TRACK,
                                    ...);
    PyDict_Update(LinkType.tp_dict, types);
    Py_DECREF(types);
     */
}
