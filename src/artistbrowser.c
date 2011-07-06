#include <Python.h>
#include <structmember.h>
#include "libspotify/api.h"
#include "pyspotify.h"
#include "artist.h"
#include "artistbrowser.h"
#include "album.h"
#include "session.h"

static PyObject *
ArtistBrowser_FromSpotify(sp_artistbrowse * browse)
{
    ArtistBrowser *b = (ArtistBrowser *)ArtistBrowserType.tp_alloc(&ArtistBrowserType, 0);

    b->_browser = browse;
    sp_artistbrowse_add_ref(browse);

    return (PyObject *)b;
}

void
ArtistBrowser_browse_complete(sp_artistbrowse * browse, Callback * st)
{
#ifdef DEBUG
    fprintf(stderr, "Artist browse complete\n");
#endif
    PyGILState_STATE gstate = PyGILState_Ensure();
    PyObject *browser = ArtistBrowser_FromSpotify(browse);

    PyObject *res = PyObject_CallFunctionObjArgs(st->callback, browser,
                                                 st->userdata, NULL);
    if (!res)
        PyErr_WriteUnraisable(st->callback);
    Py_DECREF(browser);
    Py_XDECREF(res);
    PyGILState_Release(gstate);
}

static PyObject *
ArtistBrowser_new(PyTypeObject * type, PyObject *args, PyObject *kwds)
{
    PyObject *session, *artist, *callback, *userdata = NULL;
    static char *kwlist[] =
        { "session", "artist", "callback", "userdata", NULL };
    if (!PyArg_ParseTupleAndKeywords
        (args, kwds, "O!O!O|O", kwlist, &SessionType, &session, &ArtistType,
         &artist, &callback, &userdata))
        return NULL;

    ArtistBrowser *self = (ArtistBrowser *) type->tp_alloc(type, 0);

    self->_callback.callback = callback;
    self->_callback.userdata = userdata;
    Py_XINCREF(callback);
    Py_XINCREF(userdata);

    Py_BEGIN_ALLOW_THREADS;
    self->_browser =
        sp_artistbrowse_create(((Session *) session)->_session,
                               ((Artist *) artist)->_artist,
                               (artistbrowse_complete_cb *)
                               ArtistBrowser_browse_complete,
                               (void *)&self->_callback);
    Py_END_ALLOW_THREADS;
    return (PyObject *)self;
}

static void
ArtistBrowser_dealloc(PyObject *arg)
{
#ifdef DEBUG
    fprintf(stderr, "Deallocating artist browser");
#endif

    ArtistBrowser *self = (ArtistBrowser *) arg;

    Py_XDECREF(self->_callback.callback);
    Py_XDECREF(self->_callback.userdata);
    sp_artistbrowse_release(self->_browser);
    ArtistBrowserType.tp_free(self);
}

static PyObject *
ArtistBrowser_is_loaded(ArtistBrowser * self)
{
    return Py_BuildValue("i", sp_artistbrowse_is_loaded(self->_browser));
}

Py_ssize_t
ArtistBrowser_sq_length(ArtistBrowser * self)
{
    return sp_artistbrowse_num_albums(self->_browser);
}

PyObject *
ArtistBrowser_sq_item(ArtistBrowser * self, Py_ssize_t index)
{
    if (index >= sp_artistbrowse_num_albums(self->_browser)) {
        PyErr_SetString(PyExc_IndexError, "");
        return NULL;
    }
    sp_album *album = sp_artistbrowse_album(self->_browser, (int)index);
    PyObject *wrapper = Album_FromSpotify(album);

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
