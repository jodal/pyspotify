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

#pragma once

// define DEBUG to get lots of extra crap printed out
// #define DEBUG 1

#include <Python.h>

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
