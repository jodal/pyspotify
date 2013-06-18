#include <Python.h>
#include <structmember.h>
#include <libspotify/api.h>
#include <string.h>
#include "pyspotify.h"
#include "session.h"
#include "toplistbrowser.h"
#include "user.h"
#include "album.h"
#include "artist.h"
#include "track.h"

static void
ToplistBrowser_browse_complete(sp_toplistbrowse *browser, void *data)
{
    Callback *trampoline = (Callback *)data;
    debug_printf("browse complete (%p, %p)", browser, trampoline);

    if (trampoline == NULL)
        return;

    PyObject *result, *self;
    PyGILState_STATE gstate = PyGILState_Ensure();

    self = ToplistBrowser_FromSpotify(browser);
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
ToplistBrowser_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *region, *self, *callback = NULL, *userdata = NULL;
    Callback *trampoline = NULL;

    char *tmp = NULL, *username = NULL;
    sp_toplistbrowse *browser;
    sp_toplisttype browse_type = SP_TOPLIST_TYPE_ARTISTS;
    sp_toplistregion browse_region = SP_TOPLIST_REGION_EVERYWHERE;

    static char *kwlist[] = {"type", "region", "callback", "userdata", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "esO|OO", kwlist, ENCODING,
                                     &tmp, &region, &callback, &userdata))
        return NULL;

    /* TODO: create type string constants. */
    /* TODO: extract to helper */
    if (tmp != NULL) {
        if (strcmp(tmp, "albums") == 0)
            browse_type = SP_TOPLIST_TYPE_ALBUMS;
        else if(strcmp(tmp, "artists") == 0)
            browse_type = SP_TOPLIST_TYPE_ARTISTS;
        else if (strcmp(tmp, "tracks") == 0)
            browse_type = SP_TOPLIST_TYPE_TRACKS;
        else {
            PyErr_Format(PyExc_ValueError,
                         "%s is not a valid toplist type", tmp);
            return NULL;
        }
    }

    /* Region, can be
     *   - "XY" where XY is a 2 letter country code
     *   - "all" to get worlwide toplists
     *   - "current" to get the current user's toplists
     *   - user (spotify.User) to get this user's toplists
     */
    /* TODO: extract to helper */
    /* TODO: use parse helpers with es to get region? */
    if (PyUnicode_Check(region)) {
        region = PyUnicode_AsUTF8String(region);
        if (!region)
            return NULL;
    } else
        Py_INCREF(region);

    if (PyBytes_Check(region)) {
        tmp = PyBytes_AS_STRING(region);
        if (strcmp(tmp, "all") == 0)
            browse_region = SP_TOPLIST_REGION_EVERYWHERE;
        else if (strcmp(tmp, "current") == 0)
            browse_region = SP_TOPLIST_REGION_USER;
        else /* TODO: sanity checking country code */
            browse_region = SP_TOPLIST_REGION(tmp[0], tmp[1]);
    } else if (Py_TYPE(region) == &UserType) {
        browse_region = SP_TOPLIST_REGION_USER;
        username = (char *)sp_user_canonical_name(User_SP_USER(region));
    }
    Py_DECREF(region);

    if (callback)
        trampoline = create_trampoline(callback, userdata);

    Py_BEGIN_ALLOW_THREADS
    /* TODO: audit that we cleanup with _release */
    browser = sp_toplistbrowse_create(g_session, browse_type, browse_region,
                                      username, ToplistBrowser_browse_complete,
                                      (void*)trampoline);
    Py_END_ALLOW_THREADS

    self = type->tp_alloc(type, 0);
    ToplistBrowser_SP_TOPLISTBROWSE(self) = browser;
    /* TODO: this leaks a ref */
    sp_toplistbrowse_add_ref(browser);
    return self;
}

PyObject *
ToplistBrowser_FromSpotify(sp_toplistbrowse * browser)
{
    PyObject *self = ToplistBrowserType.tp_alloc(&ToplistBrowserType, 0);
    ToplistBrowser_SP_TOPLISTBROWSE(self) = browser;
    sp_toplistbrowse_add_ref(browser);
    return self;
}

static void
ToplistBrowser_dealloc(PyObject* self)
{
    if (ToplistBrowser_SP_TOPLISTBROWSE(self) != NULL)
        sp_toplistbrowse_release(ToplistBrowser_SP_TOPLISTBROWSE(self));
    self->ob_type->tp_free(self);
}

static PyObject *
ToplistBrowser_is_loaded(PyObject* self)
{
    return PyBool_FromLong(sp_toplistbrowse_is_loaded(
        ToplistBrowser_SP_TOPLISTBROWSE(self)));
}

static PyObject *
ToplistBrowser_error(PyObject* self)
{
    return error_message(sp_toplistbrowse_error(
        ToplistBrowser_SP_TOPLISTBROWSE(self)));
}

/* sequence protocol: */
Py_ssize_t
ToplistBrowser_sq_length(PyObject* self)
{
    int n;
    sp_toplistbrowse *browser = ToplistBrowser_SP_TOPLISTBROWSE(self);

    /* TODO: see if we can store type to avoid this crazy hack */
    if ((n = sp_toplistbrowse_num_albums(browser)))
        return n;
    else if ((n = sp_toplistbrowse_num_artists(browser)))
        return n;
    else
        return sp_toplistbrowse_num_tracks(browser);
}

PyObject *
ToplistBrowser_sq_item(PyObject *self, Py_ssize_t index)
{
    int i = (int)index;
    sp_toplistbrowse *browser = ToplistBrowser_SP_TOPLISTBROWSE(self);

    /* TODO: see if we can store type to avoid this crazy hack */
    if (index < sp_toplistbrowse_num_albums(browser))
        return Album_FromSpotify(sp_toplistbrowse_album(browser, i));
    else if (index < sp_toplistbrowse_num_artists(browser))
        return Artist_FromSpotify( sp_toplistbrowse_artist(browser, i));
    else if (index < sp_toplistbrowse_num_tracks(browser))
        return Track_FromSpotify( sp_toplistbrowse_track(browser, i));

    PyErr_SetNone(PyExc_IndexError);
    return NULL;
}

PySequenceMethods ToplistBrowser_as_sequence = {
    (lenfunc) ToplistBrowser_sq_length,    /*sq_length*/
    0,                                     /*sq_concat*/
    0,                                     /*sq_repeat*/
    (ssizeargfunc) ToplistBrowser_sq_item, /*sq_item*/
    0,                                     /*sq_ass_item*/
    0,                                     /*sq_contains*/
    0,                                     /*sq_inplace_concat*/
    0,                                     /*sq_inplace_repeat*/
};

static PyMethodDef ToplistBrowser_methods[] = {
    {"is_loaded", (PyCFunction) ToplistBrowser_is_loaded, METH_NOARGS,
     "True if this toplist browser has been loaded by the client"
    },
    {"error", (PyCFunction) ToplistBrowser_error, METH_NOARGS,
     ""
    },
    {NULL} /* Sentinel */
};

static PyMemberDef ToplistBrowser_members[] = {
    {NULL} /* Sentinel */
};

PyTypeObject ToplistBrowserType = {
    PyObject_HEAD_INIT(NULL)
    0,                                        /*ob_size*/
    "spotify.ToplistBrowser",                 /*tp_name*/
    sizeof(ToplistBrowser),                   /*tp_basicsize*/
    0,                                        /*tp_itemsize*/
    (destructor) ToplistBrowser_dealloc,      /*tp_dealloc*/
    0,                                        /*tp_print*/
    0,                                        /*tp_getattr*/
    0,                                        /*tp_setattr*/
    0,                                        /*tp_compare*/
    0,                                        /*tp_repr*/
    0,                                        /*tp_as_number*/
    &ToplistBrowser_as_sequence,              /*tp_as_sequence*/
    0,                                        /*tp_as_mapping*/
    0,                                        /*tp_hash*/
    0,                                        /*tp_call*/
    0,                                        /*tp_str*/
    0,                                        /*tp_getattro*/
    0,                                        /*tp_setattro*/
    0,                                        /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "ToplistBrowser objects",                 /* tp_doc */
    0,                                        /* tp_traverse */
    0,                                        /* tp_clear */
    0,                                        /* tp_richcompare */
    0,                                        /* tp_weaklistoffset */
    0,                                        /* tp_iter */
    0,                                        /* tp_iternext */
    ToplistBrowser_methods,                   /* tp_methods */
    ToplistBrowser_members,                   /* tp_members */
    0,                                        /* tp_getset */
    0,                                        /* tp_base */
    0,                                        /* tp_dict */
    0,                                        /* tp_descr_get */
    0,                                        /* tp_descr_set */
    0,                                        /* tp_dictoffset */
    0,                                        /* tp_init */
    0,                                        /* tp_alloc */
    ToplistBrowser_new,                       /* tp_new */
};

void
toplistbrowser_init(PyObject *module)
{
    Py_INCREF(&ToplistBrowserType);
    PyModule_AddObject(module, "ToplistBrowser", (PyObject *)&ToplistBrowserType);
}
