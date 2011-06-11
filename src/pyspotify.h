#pragma once

// define DEBUG to get lots of extra crap printed out
// #define DEBUG 1

#include <Python.h>

#define ENCODING "utf-8"

extern PyObject *SpotifyError;
extern PyObject *SpotifyApiVersion;

typedef struct {
    PyObject *callback;
    PyObject *manager;
    PyObject *userdata;
} Callback;

/* Trampolines for callback handling */
Callback *create_trampoline(PyObject *callback, PyObject *manager,
                            PyObject *userdata);
void delete_trampoline(Callback * tr);

/* Returns o as a function, making type checks.
 * 3 cases:
 *   o is a Function object: returns o
 *   o is a Method object  : returns the corresponding function
 *   o is another object   : sets an exception and returns NULL
 */
PyObject *as_function(PyObject *o);
