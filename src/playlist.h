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
    PyObject_HEAD sp_playlist *_playlist;
} Playlist;

extern PyTypeObject PlaylistType;

extern void playlist_init(PyObject *m);

/* Keep track of callbacks added to a playlist */
typedef struct _playlist_callback {
    sp_playlist_callbacks *callback;
    Callback *trampoline;
    struct _playlist_callback *next;
} playlist_callback;

/* An entry in the playlist callback table */
typedef struct _pl_cb_entry {
    sp_playlist *playlist;
    playlist_callback *callbacks;
    struct _pl_cb_entry *next;
} pl_cb_entry;

PyObject *Playlist_FromSpotify(sp_playlist * spl);
