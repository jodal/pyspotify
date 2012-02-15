#include <Python.h>
#include <structmember.h>
#include "libspotify/api.h"
#include "pyspotify.h"
#include "album.h"
#include "albumbrowser.h"
#include "track.h"
#include "session.h"

PyObject *
AlbumBrowser_FromSpotify(sp_albumbrowse * browse)
{
    AlbumBrowser *b = (AlbumBrowser *)AlbumBrowserType.tp_alloc(&AlbumBrowserType, 0);

    b->_browser = browse;
    sp_albumbrowse_add_ref(browse);

    return (PyObject *)b;
}

static void
AlbumBrowser_browse_complete(sp_albumbrowse * browse, Callback * st)
{
#ifdef DEBUG
    fprintf(stderr, "[DEBUG]-albbrw- browse complete (%p, %p)\n", browse, st);
#endif
    if (!st) return;
    PyGILState_STATE gstate = PyGILState_Ensure();
    PyObject *browser = AlbumBrowser_FromSpotify(browse);

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
AlbumBrowser_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *album, *callback = NULL, *userdata = NULL;
    Callback *cb = NULL;
    AlbumBrowser *self;
    static char *kwlist[] =
        { "album", "callback", "userdata", NULL };

    if (!PyArg_ParseTupleAndKeywords
        (args, kwds, "O!|OO", kwlist, &AlbumType, &album, &callback,
            &userdata))
        return NULL;
    self = (AlbumBrowser *) type->tp_alloc(type, 0);
    if (callback) {
        if (!userdata)
            userdata = Py_None;
        cb = create_trampoline(callback, NULL, userdata);
    }
    self->_browser =
        sp_albumbrowse_create(g_session,
                               ((Album *) album)->_album,
                               (albumbrowse_complete_cb *)
                               AlbumBrowser_browse_complete,
                               cb);
    return (PyObject *)self;
}

static void
AlbumBrowser_dealloc(PyObject *arg)
{
    AlbumBrowser *self = (AlbumBrowser *) arg;

    Py_XDECREF(self->_callback.callback);
    Py_XDECREF(self->_callback.userdata);
    sp_albumbrowse_release(self->_browser);
    AlbumBrowserType.tp_free(self);
}

static PyObject *
AlbumBrowser_is_loaded(AlbumBrowser * self)
{
    return Py_BuildValue("i", sp_albumbrowse_is_loaded(self->_browser));
}

Py_ssize_t
AlbumBrowser_sq_length(AlbumBrowser * self)
{
    return sp_albumbrowse_num_tracks(self->_browser);
}

PyObject *
AlbumBrowser_sq_item(AlbumBrowser * self, Py_ssize_t index)
{
    if (index >= sp_albumbrowse_num_tracks(self->_browser)) {
        PyErr_SetString(PyExc_IndexError, "");
        return NULL;
    }
    sp_track *track = sp_albumbrowse_track(self->_browser, (int)index);
    PyObject *wrapper = Track_FromSpotify(track);

    return wrapper;
}

PySequenceMethods AlbumBrowser_as_sequence = {
    (lenfunc) AlbumBrowser_sq_length,   // sq_length
    0,                  // sq_concat
    0,                  // sq_repeat
    (ssizeargfunc) AlbumBrowser_sq_item,        // sq_item
    0,                  // sq_ass_item
    0,                  // sq_contains
    0,                  // sq_inplace_concat
    0,                  // sq_inplace_repeat
};

static PyMethodDef AlbumBrowser_methods[] = {
    {"is_loaded",
     (PyCFunction)AlbumBrowser_is_loaded,
     METH_NOARGS,
     "True if this album browser has finished loading"},
    {NULL}
};

static PyMemberDef AlbumBrowser_members[] = {
    {NULL}
};

PyTypeObject AlbumBrowserType = {
    PyObject_HEAD_INIT(NULL) 0, /*ob_size */
    "spotify.AlbumBrowser",     /*tp_name */
    sizeof(AlbumBrowser),       /*tp_basicsize */
    0,                  /*tp_itemsize */
    AlbumBrowser_dealloc,       /*tp_dealloc */
    0,                  /*tp_print */
    0,                  /*tp_getattr */
    0,                  /*tp_setattr */
    0,                  /*tp_compare */
    0,                  /*tp_repr */
    0,                  /*tp_as_number */
    &AlbumBrowser_as_sequence,  /*tp_as_sequence */
    0,                  /*tp_as_mapping */
    0,                  /*tp_hash */
    0,                  /*tp_call */
    0,                  /*tp_str */
    0,                  /*tp_getattro */
    0,                  /*tp_setattro */
    0,                  /*tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,   /*tp_flags */
    "AlbumBrowser objects",     /* tp_doc */
    0,                  /* tp_traverse */
    0,                  /* tp_clear */
    0,                  /* tp_richcompare */
    0,                  /* tp_weaklistoffset */
    0,                  /* tp_iter */
    0,                  /* tp_iternext */
    AlbumBrowser_methods,       /* tp_methods */
    AlbumBrowser_members,       /* tp_members */
    0,                  /* tp_getset */
    0,                  /* tp_base */
    0,                  /* tp_dict */
    0,                  /* tp_descr_get */
    0,                  /* tp_descr_set */
    0,                  /* tp_dictoffset */
    0,                  /* tp_init */
    0,                  /* tp_alloc */
    AlbumBrowser_new,   /* tp_new */
};

void
albumbrowser_init(PyObject *m)
{
    if (PyType_Ready(&AlbumBrowserType) < 0)
        return;

    Py_INCREF(&AlbumBrowserType);
    PyModule_AddObject(m, "AlbumBrowser", (PyObject *)&AlbumBrowserType);
}
