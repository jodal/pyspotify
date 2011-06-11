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
