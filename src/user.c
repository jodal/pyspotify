#include <Python.h>
#include <structmember.h>
#include <libspotify/api.h>
#include "pyspotify.h"
#include "session.h"
#include "user.h"

static PyObject *
User_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *self = type->tp_alloc(type, 0);
    User_SP_USER(self) = NULL;
    return self;
}

PyObject *
User_FromSpotify(sp_user *user)
{
    PyObject *self = UserType.tp_alloc(&UserType, 0);
    User_SP_USER(self) = user;
    sp_user_add_ref(user);
    return self;
}

static void
User_dealloc(PyObject *self)
{
    if (User_SP_USER(self) != NULL)
        sp_user_release(User_SP_USER(self));
    self->ob_type->tp_free(self);
}

static PyObject *
User_is_loaded(PyObject *self)
{
    return PyBool_FromLong(sp_user_is_loaded(User_SP_USER(self)));
}

static PyObject *
User_canonical_name(PyObject *self)
{
    const char *name = sp_user_canonical_name(User_SP_USER(self));
    return PyUnicode_FromString(name);
}

static PyObject *
User_display_name(PyObject *self)
{
    const char *name = sp_user_display_name(User_SP_USER(self));
    return PyUnicode_FromString(name);
}

static PyObject *
User_str(PyObject *self)
{
    return User_canonical_name(self);
}

static PyMethodDef User_methods[] = {
    {"is_loaded", (PyCFunction) User_is_loaded, METH_NOARGS,
     "True if this user has been loaded by the client"
    },
    {"canonical_name", (PyCFunction) User_canonical_name, METH_NOARGS,
     "Returns the canonical name of the user"
    },
    {"display_name", (PyCFunction) User_display_name, METH_NOARGS,
     "Returns the display name of the user"
    },
    {NULL} /* Sentinel */
};

static PyMemberDef User_members[] = {
    {NULL} /* Sentinel */
};

PyTypeObject UserType = {
    PyObject_HEAD_INIT(NULL)
    0,                                        /*ob_size*/
    "spotify.User",                           /*tp_name*/
    sizeof(User),                             /*tp_basicsize*/
    0,                                        /*tp_itemsize*/
    (destructor)User_dealloc,                 /*tp_dealloc*/
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
    User_str,                                 /*tp_str*/
    0,                                        /*tp_getattro*/
    0,                                        /*tp_setattro*/
    0,                                        /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "User objects",                           /* tp_doc */
    0,                                        /* tp_traverse */
    0,                                        /* tp_clear */
    0,                                        /* tp_richcompare */
    0,                                        /* tp_weaklistoffset */
    0,                                        /* tp_iter */
    0,                                        /* tp_iternext */
    User_methods,                             /* tp_methods */
    User_members,                             /* tp_members */
    0,                                        /* tp_getset */
    0,                                        /* tp_base */
    0,                                        /* tp_dict */
    0,                                        /* tp_descr_get */
    0,                                        /* tp_descr_set */
    0,                                        /* tp_dictoffset */
    0,                                        /* tp_init */
    0,                                        /* tp_alloc */
    User_new,                                 /* tp_new */
};

void
user_init(PyObject *module)
{
    Py_INCREF(&UserType);
    PyModule_AddObject(module, "User", (PyObject *)&UserType);

    /* TODO: why is this module levels constants instead of object? */
    /* TODO: name should be prefixed with USER_* */
    PyModule_AddIntConstant(module, "RELATION_TYPE_UNKNOWN",
                            SP_RELATION_TYPE_UNKNOWN);
    PyModule_AddIntConstant(module, "RELATION_TYPE_NONE",
                            SP_RELATION_TYPE_NONE);
    PyModule_AddIntConstant(module, "RELATION_TYPE_UNIDIRECTIONAL",
                            SP_RELATION_TYPE_UNIDIRECTIONAL);
    PyModule_AddIntConstant(module, "RELATION_TYPE_BIDIRECTIONAL",
                            SP_RELATION_TYPE_BIDIRECTIONAL);
}
