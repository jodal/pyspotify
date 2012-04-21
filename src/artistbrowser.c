#include <Python.h>
#include <structmember.h>
#include "libspotify/api.h"
#include "pyspotify.h"
#include "artist.h"
#include "artistbrowser.h"
#include "album.h"
#include "session.h"
#include "track.h"

PyObject *
ArtistBrowser_FromSpotify(sp_artistbrowse * browse)
{
    ArtistBrowser *b = (ArtistBrowser *)ArtistBrowserType.tp_alloc(&ArtistBrowserType, 0);

    b->_browser = browse;
    sp_artistbrowse_add_ref(browse);

    return (PyObject *)b;
}

void
ArtistBrowser_browse_complete(sp_artistbrowse *browse, Callback *st)
{
#ifdef DEBUG
    fprintf(stderr, "[DEBUG]-artbrw- browse complete (%p, %p)\n", browse, st);
#endif
    if (!st) return;
    PyGILState_STATE gstate = PyGILState_Ensure();
    PyObject *browser = ArtistBrowser_FromSpotify(browse);

    PyObject *res = PyObject_CallFunctionObjArgs(st->callback, browser,
                                                 st->userdata, NULL);
    if (!res)
        PyErr_WriteUnraisable(st->callback);
    delete_trampoline(st);
    Py_DECREF(browser);
    Py_XDECREF(res);
    PyGILState_Release(gstate);
}

static PyObject *
ArtistBrowser_new(PyTypeObject * type, PyObject *args, PyObject *kwds)
{
    PyObject *artist, *callback = NULL, *userdata = NULL;
    char *str_type = NULL;
    sp_artistbrowse_type abtype = SP_ARTISTBROWSE_FULL;
    Callback *cb = NULL;
    ArtistBrowser *self;
    static char *kwlist[] =
        { "artist", "type", "callback", "userdata", NULL };

    if (!PyArg_ParseTupleAndKeywords
        (args, kwds, "O!|sOO", kwlist, &ArtistType, &artist, &str_type,
         &callback, &userdata))
        return NULL;
    if (str_type) {
        if (strcmp(str_type, "full") == 0) {} // default
        else if (strcmp(str_type, "no_tracks") == 0) {
            abtype = SP_ARTISTBROWSE_NO_TRACKS;
        }
        else if (strcmp(str_type, "no_albums") == 0) {
            abtype = SP_ARTISTBROWSE_NO_ALBUMS;
        }
        else {
            PyErr_SetString(PyExc_ValueError, "Unknown artist browser type.");
            return NULL;
        }
    }
    self = (ArtistBrowser *) type->tp_alloc(type, 0);
    if (callback) {
        if (!userdata)
            userdata = Py_None;
        cb = create_trampoline(callback, NULL, userdata);
    }
    self->_browser =
        sp_artistbrowse_create(g_session,
                               ((Artist *) artist)->_artist,
                               abtype,
                               (artistbrowse_complete_cb *)
                               ArtistBrowser_browse_complete,
                               cb);
    return (PyObject *)self;
}

static void
ArtistBrowser_dealloc(PyObject *arg)
{
    ArtistBrowser *self = (ArtistBrowser *) arg;
    sp_artistbrowse_release(self->_browser);
    ArtistBrowserType.tp_free(self);
}

static PyObject *
ArtistBrowser_is_loaded(ArtistBrowser * self)
{
    return Py_BuildValue("i", sp_artistbrowse_is_loaded(self->_browser));
}

static PyObject *
ArtistBrowser_albums(ArtistBrowser * self)
{
    sp_album *album;
    int count = sp_artistbrowse_num_albums(self->_browser);
    PyObject *l = PyList_New(count);
    int i;

    for (i = 0; i < count; ++i) {
        album = sp_artistbrowse_album(self->_browser, i);
        PyObject *a = Album_FromSpotify(album);

        PyList_SetItem(l, i, a);
    }
    return l;
}

static PyObject *
ArtistBrowser_similar_artists(ArtistBrowser * self)
{
    sp_artist *artist;
    int count = sp_artistbrowse_num_similar_artists(self->_browser);
    PyObject *l = PyList_New(count);
    int i;

    for (i = 0; i < count; ++i) {
        artist = sp_artistbrowse_similar_artist(self->_browser, i);
        PyObject *a = Artist_FromSpotify(artist);

        PyList_SetItem(l, i, a);
    }
    return l;
}

static PyObject *
ArtistBrowser_tracks(ArtistBrowser * self)
{
    int count = sp_artistbrowse_num_tracks(self->_browser);
    PyObject *l = PyList_New(count);
    int i;

    for (i = 0; i < count; ++i) {
        PyObject *a = Track_FromSpotify(sp_artistbrowse_track(self->_browser, i));

        PyList_SetItem(l, i, a);
    }
    return l;
}

static PyObject *
ArtistBrowser_tophit_tracks(ArtistBrowser * self)
{
    int count = sp_artistbrowse_num_tophit_tracks(self->_browser);
    PyObject *l = PyList_New(count);
    int i;

    for (i = 0; i < count; ++i) {
        PyObject *a = Track_FromSpotify(sp_artistbrowse_tophit_track(self->_browser, i));

        PyList_SetItem(l, i, a);
    }
    return l;
}

Py_ssize_t
ArtistBrowser_sq_length(ArtistBrowser * self)
{
    return sp_artistbrowse_num_tracks(self->_browser);
}

PyObject *
ArtistBrowser_sq_item(ArtistBrowser * self, Py_ssize_t index)
{
    if (index >= sp_artistbrowse_num_tracks(self->_browser)) {
        PyErr_SetString(PyExc_IndexError, "");
        return NULL;
    }
    sp_track *track = sp_artistbrowse_track(self->_browser, (int)index);
    PyObject *wrapper = Track_FromSpotify(track);

    return wrapper;
}

PySequenceMethods ArtistBrowser_as_sequence = {
    (lenfunc) ArtistBrowser_sq_length,  // sq_length
    0,                  // sq_concat
    0,                  // sq_repeat
    (ssizeargfunc) ArtistBrowser_sq_item,       // sq_item
    0,                  // sq_ass_item
    0,                  // sq_contains
    0,                  // sq_inplace_concat
    0,                  // sq_inplace_repeat
};

static PyMethodDef ArtistBrowser_methods[] = {
    {"is_loaded",
     (PyCFunction)ArtistBrowser_is_loaded,
     METH_NOARGS,
     "True if this artist browser has finished loading"},
    {"albums",
     (PyCFunction)ArtistBrowser_albums,
     METH_NOARGS,
     "Return a list of all the albums found while browsing."},
    {"similar_artists",
     (PyCFunction)ArtistBrowser_similar_artists,
     METH_NOARGS,
     "Return a list of all the artists found while browsing."},
    {"tracks",
     (PyCFunction)ArtistBrowser_tracks,
     METH_NOARGS,
     "Return a list of all the tracks found while browsing."},
    {"tophit_tracks",
     (PyCFunction)ArtistBrowser_tophit_tracks,
     METH_NOARGS,
     "Return a list of all the top tracks found while browsing."},
    {NULL}
};

static PyMemberDef ArtistBrowser_members[] = {
    {NULL}
};

PyTypeObject ArtistBrowserType = {
    PyObject_HEAD_INIT(NULL) 0, /*ob_size */
    "spotify.ArtistBrowser",    /*tp_name */
    sizeof(ArtistBrowser),      /*tp_basicsize */
    0,                  /*tp_itemsize */
    ArtistBrowser_dealloc,      /*tp_dealloc */
    0,                  /*tp_print */
    0,                  /*tp_getattr */
    0,                  /*tp_setattr */
    0,                  /*tp_compare */
    0,                  /*tp_repr */
    0,                  /*tp_as_number */
    &ArtistBrowser_as_sequence, /*tp_as_sequence */
    0,                  /*tp_as_mapping */
    0,                  /*tp_hash */
    0,                  /*tp_call */
    0,                  /*tp_str */
    0,                  /*tp_getattro */
    0,                  /*tp_setattro */
    0,                  /*tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,   /*tp_flags */
    "ArtistBrowser objects",    /* tp_doc */
    0,                  /* tp_traverse */
    0,                  /* tp_clear */
    0,                  /* tp_richcompare */
    0,                  /* tp_weaklistoffset */
    0,                  /* tp_iter */
    0,                  /* tp_iternext */
    ArtistBrowser_methods,      /* tp_methods */
    ArtistBrowser_members,      /* tp_members */
    0,                  /* tp_getset */
    0,                  /* tp_base */
    0,                  /* tp_dict */
    0,                  /* tp_descr_get */
    0,                  /* tp_descr_set */
    0,                  /* tp_dictoffset */
    0,                  /* tp_init */
    0,                  /* tp_alloc */
    ArtistBrowser_new,  /* tp_new */
};

void
artistbrowser_init(PyObject *m)
{
    if (PyType_Ready(&ArtistBrowserType) < 0)
        return;

    Py_INCREF(&ArtistBrowserType);
    PyModule_AddObject(m, "ArtistBrowser", (PyObject *)&ArtistBrowserType);
}
