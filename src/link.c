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

#include <Python.h>
#include <structmember.h>
#include "spotify/api.h"
#include "pyspotify.h"
#include "link.h"
#include "track.h"
#include "artist.h"
#include "album.h"
#include "playlist.h"
#include "search.h"

static PyMemberDef Link_members[] = {
    {NULL}
};

static PyObject *Link_new(PyTypeObject *type, PyObject *args, PyObject *kwds) {
    Link *self;

    self = (Link *)type->tp_alloc(type, 0);
    self->_link = NULL;
    return (PyObject *)self;
}

static PyObject *Link_from_string(Link *self, PyObject *args) {
    char *s, *s2;
    if(!PyArg_ParseTuple(args, "s", &s))
	return NULL;
    s2 = malloc(strlen(s) +1);
    strcpy(s2, s);
    sp_link *link = sp_link_create_from_string(s2);
    if(!link) {
	PyErr_SetString(SpotifyError, "Failed to get link from a Spotify URI");
	return NULL;
    }
    Link *plink = (Link *)PyObject_CallObject((PyObject *)&LinkType, NULL);
    Py_INCREF(plink);
    plink->_link = link;
    return (PyObject *)plink;
}

static PyObject *Link_from_track(Link *self, PyObject *args) {
    Track *track;
    int offset;
    if(!PyArg_ParseTuple(args, "O!i", &TrackType, &track, &offset)) {
	return NULL;
    }
    sp_link *link = sp_link_create_from_track(track->_track, offset);
    if(!link) {
	PyErr_SetString(SpotifyError, "Failed to get track from a Link");
	return NULL;
    }
    Link *plink = (Link *)PyObject_CallObject((PyObject *)&LinkType, NULL);
    plink->_link = link;
    return (PyObject *)plink;
}

static PyObject *Link_from_album(Link *self, PyObject *args) {
    Album *album;
    if(!PyArg_ParseTuple(args, "O!", &AlbumType, &album))
	return NULL;
    sp_link *link = sp_link_create_from_album(album->_album);
    if(!link) {
	PyErr_SetString(SpotifyError, "Failed to get link from an album");
	return NULL;
    }
    Link *plink = (Link *)PyObject_CallObject((PyObject *)&LinkType, NULL);
    plink->_link = link;
    return (PyObject *)plink;
}

static PyObject *Link_from_artist(Link *self, PyObject *args) {
    Artist *artist;
    if(!PyArg_ParseTuple(args, "O!", &ArtistType, &artist)) {
	return NULL;
    }
    sp_link *l = sp_link_create_from_artist(artist->_artist);
    if(!l) {
	PyErr_SetString(SpotifyError, "Failed to get track from a Link");
	return NULL;
    }
    Link *link = (Link *)PyObject_CallObject((PyObject *)&LinkType, NULL);
    link->_link = l;
    return (PyObject *)link;
}

static PyObject *Link_from_search(Link *self, PyObject *args) {
    Results *results;
    if(!PyArg_ParseTuple(args, "O!", &ResultsType, &results)) {
	return NULL;
    }
    sp_link *l = sp_link_create_from_search(results->_search);
    if(!l) {
	PyErr_SetString(SpotifyError, "Failed to get link from a search");
	return NULL;
    }
    Link *link = (Link *)PyObject_CallObject((PyObject *)&LinkType, NULL);
    link->_link = l;
    return (PyObject *)link;
}

static PyObject *Link_from_playlist(Link *self, PyObject *args) {
    Playlist *playlist;
    if(!PyArg_ParseTuple(args, "O!", &PlaylistType, &playlist))
	return NULL;
    sp_link *link = sp_link_create_from_playlist(playlist->_playlist);
    if(!link) {
	PyErr_SetString(SpotifyError, "Failed to get link from an album");
	return NULL;
    }
    Link *plink = (Link *)PyObject_CallObject((PyObject *)&LinkType, NULL);
    plink->_link = link;
    return (PyObject *)plink;
}

static PyObject *Link_type(Link *self) {
    return Py_BuildValue("i", sp_link_type(self->_link));
}

static PyObject *Link_as_track(Link *self) {
    sp_track *track = sp_link_as_track(self->_link);
    if(!track) {
	PyErr_SetString(SpotifyError, "Not a track link");
	return NULL;
    }
    Track *ptrack = (Track *)PyObject_CallObject((PyObject *)&TrackType, NULL);
    ptrack->_track = track;
    Py_INCREF(ptrack);
    return (PyObject *)ptrack;
}

static PyObject *Link_as_album(Link *self) {
    sp_album *a = sp_link_as_album(self->_link);
    if(!a) {
	PyErr_SetString(SpotifyError, "Not an album link");
	return NULL;
    }
    Album *album = (Album *)PyObject_CallObject((PyObject *)&AlbumType, NULL);
    album->_album = a;
    Py_INCREF(album);
    return (PyObject *)album;
}

static PyObject *Link_as_artist(Link *self) {
    sp_artist *a = sp_link_as_artist(self->_link);
    if(!a) {
	PyErr_SetString(SpotifyError, "Not an artist link");
	return NULL;
    }
    Artist *artist = (Artist *)PyObject_CallObject((PyObject *)&ArtistType, NULL);
    artist->_artist = a;
    Py_INCREF(artist);
    return (PyObject *)artist;
}

static PyObject *Link_str(PyObject *oself) {
    Link *self = (Link *)oself;
    char uri[1024];
    if(0 > sp_link_as_string(self->_link, uri, sizeof(uri))) {
	PyErr_SetString(SpotifyError, "failed to render Spotify URI from link");
	return NULL;
    }
    return Py_BuildValue("s", uri);
}

static PyMethodDef Link_methods[] = {
    {"from_string",
     (PyCFunction)Link_from_string,
     METH_VARARGS | METH_CLASS,
     "Create a new Link object from a string"},
    {"from_track",
     (PyCFunction)Link_from_track,
     METH_VARARGS | METH_CLASS,
     "Create a new Link object from a Track object"},
    {"from_album",
     (PyCFunction)Link_from_album,
     METH_VARARGS | METH_CLASS,
     "Create a new Link object from an Album object"},
    {"from_artist",
     (PyCFunction)Link_from_artist,
     METH_VARARGS | METH_CLASS,
     "Create a new Link object from an Artist object"},
    {"from_search",
     (PyCFunction)Link_from_search,
     METH_VARARGS | METH_CLASS,
     "Create a new Link object from a Search object"},
    {"from_playlist",
     (PyCFunction)Link_from_playlist,
     METH_VARARGS | METH_CLASS,
     "Create a new Link object from a Playlist object"},
    {"type",
     (PyCFunction)Link_type,
     METH_NOARGS,
     "Return the type of the link"},
    {"as_track",
     (PyCFunction)Link_as_track,
     METH_NOARGS,
     "Return this link as a Track object"},
    {"as_album",
     (PyCFunction)Link_as_album,
     METH_NOARGS,
     "Return this link as a Album object"},
    {"as_artist",
     (PyCFunction)Link_as_artist,
     METH_NOARGS,
     "Return this link as an Artist object"},
    {NULL}
};

PyTypeObject LinkType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "_spotify.Link",           /*tp_name*/
    sizeof(Link),              /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    0,                         /*tp_dealloc*/  // TODO: IMPLEMENT THIS WITH sp_link_release
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    Link_str,                  /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "Link objects",            /* tp_doc */
    0,		               /* tp_traverse */
    0,		               /* tp_clear */
    0,		               /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    Link_methods,              /* tp_methods */
    Link_members,              /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    0,			       /* tp_init */
    0,                         /* tp_alloc */
    Link_new,                  /* tp_new */
};

void link_init(PyObject *m) {
    PyModule_AddObject(m, "Link", (PyObject *)&LinkType);
    Py_INCREF(&LinkType);
    PyMapping_SetItemString(LinkType.tp_dict, "LINK_INVALID", Py_BuildValue("i", SP_LINKTYPE_INVALID));
    PyMapping_SetItemString(LinkType.tp_dict, "LINK_TRACK", Py_BuildValue("i", SP_LINKTYPE_TRACK));
    PyMapping_SetItemString(LinkType.tp_dict, "LINK_ALBUM", Py_BuildValue("i", SP_LINKTYPE_ALBUM));
    PyMapping_SetItemString(LinkType.tp_dict, "LINK_ARTIST", Py_BuildValue("i", SP_LINKTYPE_ARTIST));
    PyMapping_SetItemString(LinkType.tp_dict, "LINK_SEARCH", Py_BuildValue("i", SP_LINKTYPE_SEARCH));
    PyMapping_SetItemString(LinkType.tp_dict, "LINK_PLAYLIST", Py_BuildValue("i", SP_LINKTYPE_PLAYLIST));
    
}
