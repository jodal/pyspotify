#include <Python.h>
#include <structmember.h>
#include "libspotify/api.h"
#include "pyspotify.h"
#include "image.h"

static PyObject *
Image_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *self = type->tp_alloc(type, 0);
    Image_SP_IMAGE(self) = NULL;
    return self;
}

PyObject *
Image_FromSpotify(sp_image *image)
{
    PyObject *self = ImageType.tp_alloc(&ImageType, 0);
    Image_SP_IMAGE(self) = image;
    sp_image_add_ref(image);
    return self;
}

static void
Image_dealloc(PyObject *self)
{
    if (Image_SP_IMAGE(self) != NULL)
        sp_image_release(Image_SP_IMAGE(self));
    self->ob_type->tp_free(self);
}

static PyObject *
Image_is_loaded(PyObject *self)
{
    return PyBool_FromLong(sp_image_is_loaded(Image_SP_IMAGE(self)));
}

static PyObject *
Image_error(PyObject *self)
{
    /* TODO: return enums that represent sp_error */
    sp_error error = sp_image_error(Image_SP_IMAGE(self));
    return Py_BuildValue("i", error);
}

static PyObject *
Image_format(PyObject *self)
{
    /* TODO: return enums that represent sp_imageformat */
    sp_imageformat format = sp_image_format(Image_SP_IMAGE(self));
    return Py_BuildValue("i", format);
}

static PyObject *
Image_data(PyObject *self)
{
    size_t size;
    void *data = (void *)sp_image_data(Image_SP_IMAGE(self), &size);
    return PyBuffer_FromMemory(data, size);
}

static PyObject *
Image_image_id(PyObject *self)
{
    /* TODO */
    Py_RETURN_NONE;
}

void
Image_loaded(sp_image *image, void *data)
{
    Callback *trampoline= (Callback *)data;
    debug_printf(">> image loaded (%p, %p)", image, trampoline);

    if (trampoline == NULL)
        return;

    PyObject *result, *self;
    PyGILState_STATE gstate = PyGILState_Ensure();

    self = Image_FromSpotify(image);
    result = PyObject_CallFunctionObjArgs(trampoline->callback, self,
                                          trampoline->userdata, NULL);
    Py_DECREF(self);

    if (result != NULL)
        Py_DECREF(result);
    else
        PyErr_WriteUnraisable(trampoline->callback);

    delete_trampoline(trampoline);
    PyGILState_Release(gstate);
}

static PyObject *
Image_add_load_callback(PyObject *self, PyObject *args)
{
    PyObject *callback = NULL, *userdata = NULL;
    Callback *trampoline;

    if (!PyArg_ParseTuple(args, "O|O", &callback, &userdata))
        return NULL;

    trampoline = create_trampoline(callback, userdata);
    sp_image_add_load_callback(Image_SP_IMAGE(self), Image_loaded, trampoline);
    Py_RETURN_NONE;
}

static PyObject *
Image_remove_load_callback(PyObject *self, PyObject *args)
{
    /* TODO */
    Py_RETURN_NONE;
}

static PyMethodDef Image_methods[] = {
    {"is_loaded", (PyCFunction)Image_is_loaded, METH_NOARGS,
     "True if this Image has been loaded by the client"
    },
    {"error", (PyCFunction)Image_error, METH_NOARGS,
     "Check if image retrieval returned an error code"
    },
    {"format", (PyCFunction)Image_format, METH_NOARGS,
     "Get image format (currently only JPEG)"
    },
    {"data", (PyCFunction)Image_data, METH_NOARGS,
     "Get image data"
    },
    {"image_id", (PyCFunction)Image_image_id, METH_NOARGS,
     "Get image ID"
    },
    {"add_load_callback", (PyCFunction)Image_add_load_callback, METH_VARARGS,
     "Add a load callback"
    },
    {"remove_load_callback", (PyCFunction)Image_remove_load_callback, METH_VARARGS,
     "Remove a load callback"
    },
    {NULL} /* Sentinel */
};

static PyMemberDef Image_members[] = {
    {NULL}
};

PyTypeObject ImageType = {
    PyObject_HEAD_INIT(NULL)
    0,                                        /*ob_size*/
    "spotify.Image",                          /*tp_name*/
    sizeof(Image),                            /*tp_basicsize*/
    0,                                        /*tp_itemsize*/
    (destructor) Image_dealloc,               /*tp_dealloc*/
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
    0,                                        /*tp_str*/
    0,                                        /*tp_getattro*/
    0,                                        /*tp_setattro*/
    0,                                        /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "Image objects",                          /* tp_doc */
    0,                                        /* tp_traverse */
    0,                                        /* tp_clear */
    0,                                        /* tp_richcompare */
    0,                                        /* tp_weaklistoffset */
    0,                                        /* tp_iter */
    0,                                        /* tp_iternext */
    Image_methods,                            /* tp_methods */
    Image_members,                            /* tp_members */
    0,                                        /* tp_getset */
    0,                                        /* tp_base */
    0,                                        /* tp_dict */
    0,                                        /* tp_descr_get */
    0,                                        /* tp_descr_set */
    0,                                        /* tp_dictoffset */
    0,                                        /* tp_init */
    0,                                        /* tp_alloc */
    Image_new,                                /* tp_new */
};

void
image_init(PyObject *module)
{
    if (PyType_Ready(&ImageType) < 0)
        return;
    Py_INCREF(&ImageType);
    PyModule_AddObject(module, "Image", (PyObject *)&ImageType);
}
