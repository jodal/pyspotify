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
#include "image.h"

static PyMemberDef Image_members[] = {
    {NULL}
};

static PyObject *Image_new(PyTypeObject *type, PyObject *args, PyObject *kwds) {
    Image *self;

    self = (Image *)type->tp_alloc(type, 0);
    self->_image = NULL;
    return (PyObject *)self;
}

static PyObject *Image_is_loaded(Image *self) {
    return Py_BuildValue("i", sp_image_is_loaded(self->_image));
}

static PyObject *Image_error(Image *self) {
    return  Py_BuildValue("i", sp_image_error(self->_image));
}

static PyObject *Image_format(Image *self) {
    return  Py_BuildValue("i", sp_image_format(self->_image));
}

static PyObject *Image_data(Image *self) {
    size_t data_size;
    void *ptr;
    ptr = sp_image_data(self->_image, &data_size);
    return PyBuffer_FromMemory(ptr, data_size);
}

static PyObject *Image_image_id(Image *self) {
}

typedef struct {
    PyObject *callback;
    PyObject *userdata;
} image_callback_trampoline;

void image_callback(sp_image *image, void *userdata) {
    image_callback_trampoline *tramp = (image_callback_trampoline *)userdata;
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    Image *i = PyObject_CallObject((PyObject *)&ImageType, NULL);
    i->_image = image;
    PyObject_CallFunctionObjArgs(tramp->callback, i, tramp->userdata, NULL);
    Py_DECREF(tramp->callback);
    Py_DECREF(tramp->userdata);
    free(userdata);
    PyGILState_Release(gstate);
}

static PyObject *Image_add_load_callback(Image *self, PyObject *args) {
    PyObject *callback;
    PyObject *userdata;
    image_callback_trampoline *tramp;
    if(!PyArg_ParseTuple(args, "OO", &callback, &userdata))
        return NULL;
    Py_INCREF(callback);
    Py_INCREF(userdata);
    tramp = malloc(sizeof(image_callback_trampoline));
    tramp->userdata = userdata;
    tramp->callback = callback;
    Py_BEGIN_ALLOW_THREADS
    sp_image_add_load_callback(self->_image, image_callback, tramp);
    Py_END_ALLOW_THREADS
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *Image_remove_load_callback(Image *self, PyObject *args) {
}

static PyMethodDef Image_methods[] = {
    {"is_loaded",
     (PyCFunction)Image_is_loaded,
     METH_NOARGS,
     "True if this Image has been loaded by the client"},
    {"error",
     (PyCFunction)Image_error,
     METH_NOARGS,
     "Check if image retrieval returned an error code"},
    {"format",
     (PyCFunction)Image_format,
     METH_NOARGS,
     "Get image format (currently only JPEG)"},
    {"data",
     (PyCFunction)Image_data,
     METH_NOARGS,
     "Get image data"},
    {"image_id",
     (PyCFunction)Image_image_id,
     METH_NOARGS,
     "Get image ID"},
    {"add_load_callback",
     (PyCFunction)Image_add_load_callback,
     METH_VARARGS,
     "Add a load callback"},
    {"remove_load_callback",
     (PyCFunction)Image_remove_load_callback,
     METH_VARARGS,
     "Remove a load callback"},
    {NULL}
};

PyTypeObject ImageType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "spotify.Image.Image",     /*tp_name*/
    sizeof(Image),             /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    0,                         /*tp_dealloc*/
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
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "Image objects",           /* tp_doc */
    0,		               /* tp_traverse */
    0,		               /* tp_clear */
    0,		               /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    Image_methods,             /* tp_methods */
    Image_members,             /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    0,			       /* tp_init */
    0,                         /* tp_alloc */
    Image_new,                 /* tp_new */
};

void image_init(PyObject *m) {
    Py_INCREF(&ImageType);
    PyModule_AddObject(m, "Image", (PyObject *)&ImageType);
}
