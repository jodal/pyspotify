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
#include "pyspotify.h"

typedef struct {
    PyObject_HEAD
    sp_playlistcontainer *_playlistcontainer;
} PlaylistContainer;

extern PyTypeObject PlaylistContainerType;

extern void playlistcontainer_init(PyObject *m);

/* Keep track of callbacks added to a playlist container */
typedef struct _playlistcontainer_callback {
    sp_playlistcontainer_callbacks *callback;
    Callback *trampoline;
    struct _playlistcontainer_callback *next;
} playlistcontainer_callback;

/* An entry in the playlist container callback table */
typedef struct _plc_cb_entry {
    sp_playlistcontainer *playlistcontainer;
    playlistcontainer_callback *callbacks;
    struct _plc_cb_entry *next;
} plc_cb_entry;
