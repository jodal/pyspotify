#include <Python.h>
#include "pyspotify.h"

typedef struct {
    PyObject_HEAD sp_playlistcontainer *_playlistcontainer;
} PlaylistContainer;

extern PyTypeObject PlaylistContainerType;

extern void playlistcontainer_init(PyObject *m);

PyObject *PlaylistContainer_FromSpotify(sp_playlistcontainer * container);

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
