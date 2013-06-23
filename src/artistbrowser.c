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
ArtistBrowser_FromSpotify(sp_artistbrowse * browser)
{
    PyObject *self = ArtistBrowserType.tp_alloc(&ArtistBrowserType, 0);
    ArtistBrowser_SP_ARTISTBROWSE(self) = browser;
    sp_artistbrowse_add_ref(browser);
    return self;
}

void
ArtistBrowser_browse_complete(sp_artistbrowse *browser, void *data)
{
    Callback *trampoline = (Callback *)data;
    debug_printf("browse complete (%p, %p)", browser, trampoline);

    if (trampoline == NULL)
        return;

    PyObject *result, *self;
    PyGILState_STATE gstate = PyGILState_Ensure();

    self = ArtistBrowser_FromSpotify(browser);
    result = PyObject_CallFunction(trampoline->callback, "NO", self,
                                   trampoline->userdata);

    if (result != NULL)
        Py_DECREF(result);
    else
        PyErr_WriteUnraisable(trampoline->callback);

    delete_trampoline(trampoline);
    PyGILState_Release(gstate);
}

static bool
sp_artistbrowse_type_converter(PyObject *o, void *address) {
    sp_artistbrowse_type *type = (sp_artistbrowse_type *)address;

    if (o == NULL || o == Py_None)
        return 1;

    if (!PyString_Check(o))
        goto error;

    char *tmp = PyString_AsString(o);
    if (strcmp(tmp, "full") == 0)
        *type = SP_ARTISTBROWSE_FULL;
    else if (strcmp(tmp, "no_tracks") == 0)
        *type = SP_ARTISTBROWSE_NO_TRACKS;
    else if (strcmp(tmp, "no_albums") == 0)
        *type = SP_ARTISTBROWSE_NO_ALBUMS;
    else
        goto error;

    return 1;

error:
    PyErr_Format(PyExc_ValueError, "Unknown artist browser type: %s",
                 PyString_AsString(PyObject_Repr(o)));
    return 0;
}

static PyObject *
ArtistBrowser_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *artist, *self, *callback = NULL, *userdata = NULL;
    Callback *trampoline = NULL;

    sp_artistbrowse *browser;
    sp_artistbrowse_type browse_type = SP_ARTISTBROWSE_FULL;

    static char *kwlist[] = {"artist", "type", "callback", "userdata", NULL};

    if (!PyArg_ParseTupleAndKeywords (args, kwds, "O!|O&OO", kwlist,
                                      &ArtistType, &artist,
                                      &sp_artistbrowse_type_converter,
                                      (void *)&browse_type, &callback,
                                      &userdata))
        return NULL;

    if (callback != NULL)
        trampoline = create_trampoline(callback, userdata);

    /* TODO: audit that we cleanup with _release */
    browser = sp_artistbrowse_create(g_session, Artist_SP_ARTIST(artist),
                                     browse_type,
                                     ArtistBrowser_browse_complete,
                                     (void*)trampoline);

    self = type->tp_alloc(type, 0);
    ArtistBrowser_SP_ARTISTBROWSE(self) = browser;
    return self;
}

static void
ArtistBrowser_dealloc(PyObject *self)
{
    sp_artistbrowse_release(ArtistBrowser_SP_ARTISTBROWSE(self));
    ArtistBrowserType.tp_free(self);
}

static PyObject *
ArtistBrowser_is_loaded(PyObject *self)
{
    sp_artistbrowse *browser = ArtistBrowser_SP_ARTISTBROWSE(self);
    return PyBool_FromLong(sp_artistbrowse_is_loaded(browser));
}

static PyObject *
ArtistBrowser_albums(PyObject *self)
{
    sp_artistbrowse *browser = ArtistBrowser_SP_ARTISTBROWSE(self);
    sp_album *album;
    int i;
    int count = sp_artistbrowse_num_albums(browser);
    PyObject *list = PyList_New(count);

    for (i = 0; i < count; ++i) {
        album = sp_artistbrowse_album(browser, i);
        PyList_SET_ITEM(list, i, Album_FromSpotify(album));
    }
    return list;
}

static PyObject *
ArtistBrowser_similar_artists(PyObject *self)
{
    sp_artistbrowse *browser = ArtistBrowser_SP_ARTISTBROWSE(self);
    sp_artist *artist;
    int i;
    int count = sp_artistbrowse_num_similar_artists(browser);
    PyObject *list = PyList_New(count);

    for (i = 0; i < count; ++i) {
        artist = sp_artistbrowse_similar_artist(browser, i);
        PyList_SET_ITEM(list, i, Artist_FromSpotify(artist));
    }
    return list;
}

static PyObject *
ArtistBrowser_tracks(PyObject *self)
{
    sp_artistbrowse *browser = ArtistBrowser_SP_ARTISTBROWSE(self);
    sp_track *track;
    int i;
    int count = sp_artistbrowse_num_tracks(browser);
    PyObject *list = PyList_New(count);

    for (i = 0; i < count; ++i) {
        track = sp_artistbrowse_track(browser, i);
        PyList_SET_ITEM(list, i, Track_FromSpotify(track));
    }
    return list;
}

static PyObject *
ArtistBrowser_tophit_tracks(PyObject *self)
{
    sp_artistbrowse *browser = ArtistBrowser_SP_ARTISTBROWSE(self);
    sp_track *track;
    int i;
    int count = sp_artistbrowse_num_tophit_tracks(browser);
    PyObject *list = PyList_New(count);

    for (i = 0; i < count; ++i) {
        track = sp_artistbrowse_tophit_track(browser, i);
        PyList_SET_ITEM(list, i, Track_FromSpotify(track));
    }
    return list;
}

/* sequence protocol: */
Py_ssize_t
ArtistBrowser_sq_length(PyObject *self)
{
    return sp_artistbrowse_num_tracks(ArtistBrowser_SP_ARTISTBROWSE(self));
}

PyObject *
ArtistBrowser_sq_item(PyObject *self, Py_ssize_t index)
{
    if (index >= ArtistBrowser_sq_length(self)) {
        PyErr_SetNone(PyExc_IndexError);
        return NULL;
    }
    sp_track *track = sp_artistbrowse_track(
        ArtistBrowser_SP_ARTISTBROWSE(self), (int)index);
    return Track_FromSpotify(track);
}

PySequenceMethods ArtistBrowser_as_sequence = {
    (lenfunc) ArtistBrowser_sq_length,          /*sq_length*/
    0,                                          /*sq_concat*/
    0,                                          /*sq_repeat*/
    (ssizeargfunc) ArtistBrowser_sq_item,       /*sq_item*/
    0,                                          /*sq_ass_item*/
    0,                                          /*sq_contains*/
    0,                                          /*sq_inplace_concat*/
    0,                                          /*sq_inplace_repeat*/
};

static PyMethodDef ArtistBrowser_methods[] = {
    {"is_loaded", (PyCFunction)ArtistBrowser_is_loaded, METH_NOARGS,
     "True if this artist browser has finished loading"
    },
    {"albums", (PyCFunction)ArtistBrowser_albums, METH_NOARGS,
     "Return a list of all the albums found while browsing."
    },
    {"similar_artists", (PyCFunction)ArtistBrowser_similar_artists, METH_NOARGS,
     "Return a list of all the artists found while browsing."
    },
    {"tracks", (PyCFunction)ArtistBrowser_tracks, METH_NOARGS,
     "Return a list of all the tracks found while browsing."
    },
    {"tophit_tracks", (PyCFunction)ArtistBrowser_tophit_tracks, METH_NOARGS,
     "Return a list of all the top tracks found while browsing."
    },
    {NULL} /* Sentinel */
};

static PyMemberDef ArtistBrowser_members[] = {
    {NULL} /* Sentinel */
};

PyTypeObject ArtistBrowserType = {
    PyObject_HEAD_INIT(NULL) 0,               /*ob_size */
    "spotify.ArtistBrowser",                  /*tp_name */
    sizeof(ArtistBrowser),                    /*tp_basicsize */
    0,                                        /*tp_itemsize */
    (destructor)ArtistBrowser_dealloc,        /*tp_dealloc */
    0,                                        /*tp_print */
    0,                                        /*tp_getattr */
    0,                                        /*tp_setattr */
    0,                                        /*tp_compare */
    0,                                        /*tp_repr */
    0,                                        /*tp_as_number */
    &ArtistBrowser_as_sequence,               /*tp_as_sequence */
    0,                                        /*tp_as_mapping */
    0,                                        /*tp_hash */
    0,                                        /*tp_call */
    0,                                        /*tp_str */
    0,                                        /*tp_getattro */
    0,                                        /*tp_setattro */
    0,                                        /*tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags */
    "ArtistBrowser objects",                  /* tp_doc */
    0,                                        /* tp_traverse */
    0,                                        /* tp_clear */
    0,                                        /* tp_richcompare */
    0,                                        /* tp_weaklistoffset */
    0,                                        /* tp_iter */
    0,                                        /* tp_iternext */
    ArtistBrowser_methods,                    /* tp_methods */
    ArtistBrowser_members,                    /* tp_members */
    0,                                        /* tp_getset */
    0,                                        /* tp_base */
    0,                                        /* tp_dict */
    0,                                        /* tp_descr_get */
    0,                                        /* tp_descr_set */
    0,                                        /* tp_dictoffset */
    0,                                        /* tp_init */
    0,                                        /* tp_alloc */
    ArtistBrowser_new,                        /* tp_new */
};

void
artistbrowser_init(PyObject *module)
{
    if (PyType_Ready(&ArtistBrowserType) < 0)
        return;
    Py_INCREF(&ArtistBrowserType);
    PyModule_AddObject(module, "ArtistBrowser", (PyObject *)&ArtistBrowserType);
}
