#include <Python.h>
#include <structmember.h>
#include "libspotify/api.h"
#include "pyspotify.h"
#include "album.h"
#include "albumbrowser.h"
#include "track.h"
#include "session.h"

PyObject *
AlbumBrowser_FromSpotify(sp_albumbrowse *browser)
{
    PyObject *self = AlbumBrowserType.tp_alloc(&AlbumBrowserType, 0);
    AlbumBrowser_SP_ALBUMBROWSE(self) = browser;
    sp_albumbrowse_add_ref(browser);
    return self;
}

static void
AlbumBrowser_browse_complete(sp_albumbrowse *browser, void *data)
{
    Callback *trampoline = (Callback *)data;
    debug_printf("browse complete (%p, %p)", browser, trampoline);

    if (trampoline == NULL)
        return;

    PyObject *result, *self;
    PyGILState_STATE gstate = PyGILState_Ensure();

    self = AlbumBrowser_FromSpotify(browser);
    result = PyObject_CallFunction(trampoline->callback, "OO", self,
                                   trampoline->userdata);
    Py_XDECREF(self);

    if (result != NULL)
        Py_DECREF(result);
    else
        PyErr_WriteUnraisable(trampoline->callback);

    delete_trampoline(trampoline);
    PyGILState_Release(gstate);
}

static PyObject *
AlbumBrowser_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *album, *self, *callback = NULL, *userdata = NULL;
    Callback *trampoline = NULL;

    static char *kwlist[] = {"album", "callback", "userdata", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!|OO", kwlist, &AlbumType,
                                     &album, &callback, &userdata))
        return NULL;

    if (callback)
        trampoline = create_trampoline(callback, userdata);

    /* TODO: audit that we cleanup with _release */
    sp_albumbrowse *browser = sp_albumbrowse_create(
        g_session, Album_SP_ALBUM(album), AlbumBrowser_browse_complete,
        (void*)trampoline);

    /* This code duplicates AlbumBrowser_FromSpotify but without sp incref */
    self = AlbumBrowserType.tp_alloc(&AlbumBrowserType, 0);
    AlbumBrowser_SP_ALBUMBROWSE(self) = browser;
    return self;
}

static void
AlbumBrowser_dealloc(PyObject *self)
{
    sp_albumbrowse_release(AlbumBrowser_SP_ALBUMBROWSE(self));
    AlbumBrowserType.tp_free(self);
}

static PyObject *
AlbumBrowser_is_loaded(PyObject *self)
{
    bool loaded = sp_albumbrowse_is_loaded(AlbumBrowser_SP_ALBUMBROWSE(self));
    return PyBool_FromLong(loaded);
}

/* sequence protocol: */
Py_ssize_t
AlbumBrowser_sq_length(PyObject *self)
{
    return sp_albumbrowse_num_tracks(AlbumBrowser_SP_ALBUMBROWSE(self));
}

PyObject *
AlbumBrowser_sq_item(PyObject *self, Py_ssize_t index)
{
    if (index >= AlbumBrowser_sq_length(self)) {
        PyErr_SetNone(PyExc_IndexError);
        return NULL;
    }
    sp_track *track = sp_albumbrowse_track(
        AlbumBrowser_SP_ALBUMBROWSE(self), (int)index);
    return Track_FromSpotify(track);
}

PySequenceMethods AlbumBrowser_as_sequence = {
    (lenfunc) AlbumBrowser_sq_length,    /*sq_length*/
    0,                                   /*sq_concat*/
    0,                                   /*sq_repeat*/
    (ssizeargfunc) AlbumBrowser_sq_item, /*sq_item*/
    0,                                   /*sq_ass_item*/
    0,                                   /*sq_contains*/
    0,                                   /*sq_inplace_concat*/
    0,                                   /*sq_inplace_repeat*/
};

static PyMethodDef AlbumBrowser_methods[] = {
    {"is_loaded", (PyCFunction)AlbumBrowser_is_loaded, METH_NOARGS,
     "True if this album browser has finished loading"
    },
    {NULL} /* Sentinel */
};

static PyMemberDef AlbumBrowser_members[] = {
    {NULL} /* Sentinel */
};

PyTypeObject AlbumBrowserType = {
    PyObject_HEAD_INIT(NULL)
    0,                                        /*ob_size*/
    "spotify.AlbumBrowser",                   /*tp_name*/
    sizeof(AlbumBrowser),                     /*tp_basicsize*/
    0,                                        /*tp_itemsize*/
    (destructor)AlbumBrowser_dealloc,         /*tp_dealloc*/
    0,                                        /*tp_print*/
    0,                                        /*tp_getattr*/
    0,                                        /*tp_setattr*/
    0,                                        /*tp_compare*/
    0,                                        /*tp_repr*/
    0,                                        /*tp_as_number*/
    &AlbumBrowser_as_sequence,                /*tp_as_sequence*/
    0,                                        /*tp_as_mapping*/
    0,                                        /*tp_hash*/
    0,                                        /*tp_call*/
    0,                                        /*tp_str*/
    0,                                        /*tp_getattro*/
    0,                                        /*tp_setattro*/
    0,                                        /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "AlbumBrowser objects",                   /* tp_doc */
    0,                                        /* tp_traverse */
    0,                                        /* tp_clear */
    0,                                        /* tp_richcompare */
    0,                                        /* tp_weaklistoffset */
    0,                                        /* tp_iter */
    0,                                        /* tp_iternext */
    AlbumBrowser_methods,                     /* tp_methods */
    AlbumBrowser_members,                     /* tp_members */
    0,                                        /* tp_getset */
    0,                                        /* tp_base */
    0,                                        /* tp_dict */
    0,                                        /* tp_descr_get */
    0,                                        /* tp_descr_set */
    0,                                        /* tp_dictoffset */
    0,                                        /* tp_init */
    0,                                        /* tp_alloc */
    AlbumBrowser_new,                         /* tp_new */
};

void
albumbrowser_init(PyObject *module)
{
    if (PyType_Ready(&AlbumBrowserType) < 0)
        return;
    Py_INCREF(&AlbumBrowserType);
    PyModule_AddObject(module, "AlbumBrowser", (PyObject *)&AlbumBrowserType);
}
